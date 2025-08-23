from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from reddit_collector import fetch_and_store_posts
from ai_processing import create_summaries_for_all_posts
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="InterviewsDB API", version="1.0.0")

# Add CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "InterviewsDB API is running"}

@app.post("/api/fetch-reddit-posts")
async def fetch_reddit_posts():
    """
    Fetch new Reddit posts and process them into summaries
    """
    try:
        logger.info("Starting Reddit post fetch process...")
        
        # Fetch posts from different time periods
        fetch_and_store_posts(time_filter='day')   # fetches today's posts
        fetch_and_store_posts(time_filter='week')  # fetches this week's posts
        
        logger.info("Reddit posts fetched successfully, now creating summaries...")
        
        # Create summaries for all posts
        create_summaries_for_all_posts()
        
        # Get the count of posts and summaries
        reddit_data_count = 0
        summary_count = 0
        
        if os.path.exists("reddit_data.json"):
            with open("reddit_data.json", "r", encoding="utf-8") as f:
                reddit_data = json.load(f)
                reddit_data_count = len(reddit_data) if isinstance(reddit_data, list) else 1
        
        if os.path.exists("filtered_summaries.json"):
            with open("filtered_summaries.json", "r", encoding="utf-8") as f:
                summaries = json.load(f)
                summary_count = len(summaries) if isinstance(summaries, list) else 1
        
        logger.info(f"Process completed. Reddit posts: {reddit_data_count}, Summaries: {summary_count}")
        
        return JSONResponse({
            "success": True,
            "message": "Reddit posts fetched and processed successfully",
            "reddit_posts_count": reddit_data_count,
            "summaries_count": summary_count
        })
        
    except Exception as e:
        logger.error(f"Error fetching Reddit posts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching Reddit posts: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
