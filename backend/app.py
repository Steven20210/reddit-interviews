from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import os 
import re
import sys
import time
from collections import defaultdict
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pymongo import MongoClient
from pydantic import BaseModel, validator, Field
from typing import Optional
from middleware.auth import verify_ephemeral_token, make_ephemeral_token, get_token_from_header
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

# Validate required environment variables
required_env_vars = [
    "COSMODB_CONNSTR",
    "HMAC_SECRET",
    "REDDIT_INTERVIEWS_FRONTEND_URL"
]

for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"Required environment variable {var} is not set")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="InterviewsDB API", version="1.0.0")
client = MongoClient(os.getenv("COSMODB_CONNSTR"), tls=True)
db = client["reddit-interview"]
summarized_collection = db["summarized_posts"]
companies_metadata_collection = db["company_metadata"]
summarized_collection.create_index([("timestamp", -1)])

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def sanitize_regex_input(user_input: str) -> str:
    # Escape special regex characters
    return re.escape(user_input)

# Add CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("REDDIT_INTERVIEWS_FRONTEND_URL"), "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Add request logging middleware

class SearchRequest(BaseModel):
    query: Optional[str] = Field(None, max_length=100, pattern=r'^[a-zA-Z0-9\s\-_.,!?]*$')
    company: Optional[str] = Field("all", max_length=50)
    role: Optional[str] = Field("all", max_length=50)
    page: int = Field(1, ge=1, le=100)
    limit: int = Field(10, ge=1, le=50)
    sort_order: Optional[str] = Field("desc", pattern=r'^(asc|desc)$')

    @validator('query')
    def validate_query(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Query must be at least 2 characters')
        return v
    
@limiter.limit("5/minute")    
@app.get("/")
async def root(request: Request):
    return {"message": "InterviewsDB API is running"}

@limiter.limit("30/minute")
@app.get("/token")
def get_token(request: Request):
    token = make_ephemeral_token()
    return {"token": token}

@limiter.limit("10/minute")  # Reduced rate limit for expensive operations
@app.post("/search")
def search(request: Request, search_request: SearchRequest, token: str = Depends(get_token_from_header)):
    try:
        ok, info = verify_ephemeral_token(token)
        if not ok:
            raise HTTPException(401, "Invalid or expired token")
    except Exception as e:
        logging.error(f"Token verification failed: {type(e).__name__}")
        raise HTTPException(401, "Authentication failed")
    filter_query = {}
    companies = set()
    roles = set()
    company_map = defaultdict(set)
    role_map = defaultdict(set)
    sort_direction = -1 if search_request.sort_order == "desc" else 1


    # Full-text search in raw + summary
    if search_request.query:
        sanitized_query = sanitize_regex_input(search_request.query)
        filter_query["$or"] = [
            {"raw_post": {"$regex": sanitized_query, "$options": "i"}},
            {"summary": {"$regex": sanitized_query, "$options": "i"}}
        ]
        
    metadata = companies_metadata_collection.find({})
    for entry in metadata:
        companies.add(entry["company"])
        company_map[entry["company"]] = set(entry.get("roles", [])) 
        for r in entry.get("roles", []):
            role_map[r].add(entry["company"])
            roles.add(r)
            
    # Company filter
    if search_request.company and search_request.company != "all":
        filter_query["company"] = search_request.company
        roles = company_map.get(search_request.company, set())
    # Role filter
    if search_request.role and search_request.role != "all":
        filter_query["role"] = search_request.role
        companies = role_map.get(search_request.role, set())
        
    # Count + Pagination
    total = summarized_collection.count_documents(filter_query)
    results = list(
        summarized_collection.find(filter_query)
        .sort("timestamp", sort_direction)
        .skip((search_request.page - 1) * search_request.limit)
        .limit(search_request.limit)
    )

    # Convert ObjectId to string
    for r in results:
        r["_id"] = str(r["_id"])
        companies.add(r["company"])
        roles.add(r["role"])

    return {
        "total": total,
        "page": search_request.page,
        "limit": search_request.limit,
        "results": results,
        "companies": sorted(companies),
        "roles": sorted(roles)
    }
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # fallback to 8000 locally
    uvicorn.run(app, host="0.0.0.0", port=port)
