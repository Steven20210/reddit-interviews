import os
import requests
from dotenv import load_dotenv
import json
import logging
import time
from azure.storage.queue import QueueClient
from db.handlers import SummarizedPost
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

load_dotenv()
logging.info("Loaded environment variables from .env")

GROQ_API_KEY = os.getenv("GROQ_TOKEN")
RAW_REDDIT_DATA_FILE = "reddit_data.json"
if not GROQ_API_KEY:
    logging.error("GROQ_TOKEN not found in environment variables.")

def extract_interview_summary_with_comments(post_data):
    """
    Intelligently extracts interview information from posts and their comments.
    
    Args:
        post_data: Dictionary containing post title, selftext, and comments
    """
    
    title = post_data.get("title", "")
    selftext = post_data.get("selftext", "")
    comments = post_data.get("comments", [])
    
    # Combine post content
    post_content = f"Title: {title}\n\nContent: {selftext}"
    
    # Extract comment content
    comment_content = ""
    if comments:
        comment_content = "\n\nTop Comments:\n"
        for i, comment in enumerate(comments[:3], 1):
            comment_content += f"\nComment {i}:\n{comment.get('body', '')}\n"
    
    full_content = post_content + comment_content
    
    prompt = f"""Extract interview experience info from Reddit posts/comments.

RULES:
- Post has detailed experience → summarize it
- Post is question + comments have experience → summarize both
- Post is question + no useful comments → return "None"
- Include company/role if mentioned
- Focus on rounds, questions, difficulty, tips
- Ignore generic advice

FORMAT: Bullet points if valuable info, "None" if not.

CONTENT:
{full_content}"""
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gemma2-9b-it",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.2
    }
    logging.info("Sending request to Groq API for interview summary extraction with comments.")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        logging.info("Received response from Groq API.")
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        logging.error(f"Groq API request failed: {e}")
        return None


def summarize_post_with_comments(post_data: dict):
    """
    Summarizes a Reddit post with its comments using the new intelligent extraction.
    
    Args:
        post_data: Dictionary containing post data including title, selftext, comments, url, etc.
    """
    logging.info("Summarizing a Reddit post with comments.")
    
    # Use the new comment-aware extraction function
    summary = extract_interview_summary_with_comments(post_data)
    
    if summary == "None":
        logging.warning("No summary returned for post.")
    
    # Create entry with all relevant post data
    raw_post = post_data.get("title", "") + "\n\n" + post_data.get("selftext", "")
    entry = {
        "raw":  raw_post,
        "summary": summary,
        "url": post_data.get("url", ""),
        "post_id": post_data.get("post_id", ""),
        "subreddit": post_data.get("subreddit", ""),
        "author": post_data.get("author", ""),
        "num_comments": post_data.get("num_comments", 0),
        "comments": post_data.get("comments", [])
    }
    SummarizedPost.upsert_post(entry["url"], summary, raw_post, hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest())

def create_summaries_for_all_posts(queue_client: QueueClient):
    logging.info(f"Dequeuing Reddit Posts.")
    posts = queue_client.receive_messages()
    posts = list(posts)
    for post in posts:
        post_data = json.loads(post.content)
        # logging.info('erer', post_data)
        logging.info(f"Processing post: {post}")
        # Use the new comment-aware summarization function
        summarize_post_with_comments(post_data["payload"])
        time.sleep(4)  # Sleep to avoid hitting API rate limits
        queue_client.delete_message(post)