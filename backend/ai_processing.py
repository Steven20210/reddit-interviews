import os
import requests
from dotenv import load_dotenv
import json
import logging
import time
from azure.storage.queue import QueueClient
from db.handlers import SummarizedPost
import hashlib
import re
from typing import Tuple
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

role_patterns = [
    {"regex": re.compile(r"sde[\s\-]?i\b|sde[\s\-]?1\b|sdei\b|sde1\b|software engineer[\s\-]?i\b|software engineer[\s\-]?1\b", re.I), "norm": "SDE I"},
    {"regex": re.compile(r"sde[\s\-]?ii\b|sde[\s\-]?2\b|sdeii\b|sde2\b|software engineer[\s\-]?ii\b|software engineer[\s\-]?2\b", re.I), "norm": "SDE II"},
    {"regex": re.compile(r"sde[\s\-]?iii\b|sde[\s\-]?3\b|sdeiii\b|sde3\b|software engineer[\s\-]?iii\b|software engineer[\s\-]?3\b", re.I), "norm": "SDE III"},
    {"regex": re.compile(r"sde[\s\-]?intern|software engineer intern", re.I), "norm": "SDE Intern"},
    {"regex": re.compile(r"swe[\s\-]?intern", re.I), "norm": "SWE Intern"},
    {"regex": re.compile(r"software engineer", re.I), "norm": "Software Engineer"},
    {"regex": re.compile(r"software developer", re.I), "norm": "Software Developer"},
    {"regex": re.compile(r"backend engineer", re.I), "norm": "Backend Engineer"},
    {"regex": re.compile(r"frontend engineer", re.I), "norm": "Frontend Engineer"},
    {"regex": re.compile(r"full[\s\-]?stack engineer", re.I), "norm": "Full Stack Engineer"},
    {"regex": re.compile(r"data scientist", re.I), "norm": "Data Scientist"},
    {"regex": re.compile(r"data engineer", re.I), "norm": "Data Engineer"},
    {"regex": re.compile(r"product manager", re.I), "norm": "Product Manager"},
    {"regex": re.compile(r"engineering manager", re.I), "norm": "Engineering Manager"},
    {"regex": re.compile(r"new grad", re.I), "norm": "New Grad"},
    {"regex": re.compile(r"intern", re.I), "norm": "Intern"},
]

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
    company, role = extract_company_and_role(summary)    
    SummarizedPost.upsert_post(entry["url"], summary, raw_post, hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest(), role, company)

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

def extract_company_and_role(text: str) -> Tuple[str, str]:
    # Remove bullets, asterisks, and excessive whitespace
    clean_text = re.sub(r"[*•]", "", text)
    clean_text = clean_text.strip()

    # Extract company
    company_match = re.search(r"Company:\s*(.+)", clean_text, re.I)
    company = company_match.group(1).strip() if company_match else "Unknown"

    # Extract raw role text
    role_match = re.search(r"Role:\s*(.+)", clean_text, re.I)
    role_raw = role_match.group(1).strip() if role_match else ""

    # Normalize role using role_patterns
    normalized_role = "Unknown"
    if role_raw:
        for pattern in role_patterns:
            if pattern["regex"].search(role_raw):
                normalized_role = pattern["norm"]
                break

    return company, normalized_role


def migrate_old_data():
    if not os.path.exists("backend/filtered_summaries copy.json"):
        print("No filtered_summaries copy file found for migration.")
        return
    
    with open("backend/filtered_summaries copy.json", "r", encoding="utf-8") as f:
        reddit_data = json.load(f)
    
    if not isinstance(reddit_data, list):
        reddit_data = [reddit_data]
    
    for post_data in reddit_data:
        company, role = extract_company_and_role(post_data["summary"])
        print(company, role)    
        SummarizedPost.upsert_post(post_data["url"], post_data["summary"], post_data["raw"], hashlib.sha256(json.dumps(post_data, sort_keys=True).encode("utf-8")).hexdigest(), role, company)
    
if __name__ == "__main__":
    migrate_old_data()