from fastapi import FastAPI, HTTPException, Depends

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import os 
from collections import defaultdict
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional
from middleware.auth import verify_ephemeral_token, make_ephemeral_token, get_token_from_header
from dotenv import load_dotenv
load_dotenv()
from fastapi import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="InterviewsDB API", version="1.0.0")
client = MongoClient(os.getenv("MONGODBATLAS_CLUSTER_CONNECTIONSTRING"), tls=True)
db = client["reddit-interview"]
summarized_collection = db["summarized_posts"]
companies_metadata_collection = db["company_metadata"]
companies_metadata_inverted_collection = db["company_metadata_inverted"]
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class SearchRequest(BaseModel):
    query: Optional[str] = None
    company: Optional[str] = "all"
    role: Optional[str] = "all"
    page: int = 1
    limit: int = 10
    
@limiter.limit("5/minute")    
@app.get("/")
async def root(request: Request):
    return {"message": "InterviewsDB API is running"}

@limiter.limit("30/minute")
@app.get("/token")
def get_token(request: Request):
    token = make_ephemeral_token()
    return {"token": token}

@limiter.limit("30/minute")
@app.post("/search")
def search(request: Request, search_request: SearchRequest, token: str = Depends(get_token_from_header)):
    ok, info = verify_ephemeral_token(token)
    if not ok:
        raise HTTPException(401, info)
    filter_query = {}
    companies = set()
    roles = set()
    company_map = defaultdict(set)
    role_map = defaultdict(set)
    
    # Full-text search in raw + summary
    if search_request.query:
        filter_query["$or"] = [
            {"raw": {"$regex": search_request.query, "$options": "i"}},
            {"summary": {"$regex": search_request.query, "$options": "i"}}
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
    uvicorn.run(app, host="0.0.0.0", port=8001)
