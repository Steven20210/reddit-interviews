import os
import praw
from dotenv import load_dotenv
import re
import json 
from collections import Counter
from backend.ai_processing import create_summaries_for_all_posts
import hashlib
from aqs.queue_handlers import enqueue_post, ensure_queue_exists
from db.handlers import Post, SummarizedPost
import logging
from urllib.parse import urlparse

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "interviewsdb-bot/0.1")

SUBREDDITS = [
    "csmajors",
    "leetcode",
]

negative_pattern = re.compile(r"""
\b(
    have\ an?\ interview\ (coming\ up|soon|tomorrow|next\ week)              # interview is soon

)\b
""", re.IGNORECASE | re.VERBOSE)
RANK_PATTERNS = [
    r"Round\s*\d+",
    r"Data\s*Structure",
    r"algo|algorithm",
    r"problem|question",
    r"(High|Low)\s*Level\s*Design",
    r"system\s*design",
    r"architecture\s*diagram",
    r"\bapi\b",
    r"code|code\s*explanation",
    r"follow-?up",
    r"ownership",
    r"leadership",
    r"behavioral",
    r"bias\s*for\s*action",
    r"customer\s*obsession",
    r"\(\d+\/10\)"
]
RANK_PATTERNS = re.compile("|".join(f"({p})" for p in RANK_PATTERNS), re.IGNORECASE)

LEETCODE_PATTERN = re.compile(r"""
\b(
  LC\s?\d+|
  leetcode\s?problem\s?\d+|
  leetcode\s?\d+|
  https?://leetcode\.com/problems/[\w-]+|
)\b
""", re.IGNORECASE | re.VERBOSE)

QUERIES = [
    # Company-specific interview experience queries
    "Apple", "Google", "Meta", "Amazon", "Microsoft", "Netflix", "Tesla",
    '(title:"interview" OR title:"experience") AND title:(oa OR onsite OR final OR phone OR screening)',
]


def get_reddit_instance():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

def score_post(text):
    matches = re.findall(RANK_PATTERNS, text)
    # matches is a list of tuples because of capture groups — flatten and count non-empty
    flat_matches = [m for tup in matches for m in tup if m]
    # Count unique patterns matched
    counts = Counter(flat_matches)
    score = len(counts)  # number of unique patterns matched
    total_matches = len(flat_matches)  # total number of matches including duplicates
    return score, total_matches

def fetch_and_store_posts(time_filter):
    reddit = get_reddit_instance()
    queue_client = ensure_queue_exists(os.getenv("AZURE_QUEUE_CONN"), "reddit-posts")
    all_data = []
    for subreddit_name in SUBREDDITS:
        subreddit = reddit.subreddit(subreddit_name)
        for query in QUERIES:
            posts = subreddit.search(query, sort='top', time_filter=time_filter, limit=100)
            for post in posts:
                # Fetch top 3 comments for this post
                post.comment_sort = 'top'  # Sort comments by top
                post.comment_limit = 3     # Limit to top 3 comments
                post.comments.replace_more(limit=0)  # Don't expand "more comments" links
                
                comments_data = []
                for comment in post.comments[:3]:  # Get top 3 comments
                    if hasattr(comment, 'body') and comment.body and comment.body != '[deleted]':
                        comment_data = {
                            "comment_id": comment.id,
                            "body": comment.body,
                            "author": str(comment.author) if comment.author else "[deleted]",
                            "score": comment.score,
                            "created_utc": comment.created_utc,
                            "permalink": f"https://reddit.com{comment.permalink}"
                        }
                        comments_data.append(comment_data)
                
                post_data = {
                    "subreddit": subreddit_name,
                    "post_id": post.id,
                    "title": post.title,
                    "selftext": post.selftext,
                    "created_utc": post.created_utc,
                    "author": str(post.author),
                    "url": post.url,
                    "num_comments": post.num_comments,
                    "comments": comments_data
                }
                all_data.append(post_data)
                logging.info(f"Fetched post: {post.title} with {len(comments_data)} comments")
                enqueue_post(queue_client, Post, post.url, post_data, hashlib.sha256(json.dumps(post_data, sort_keys=True).encode("utf-8")).hexdigest())
    create_summaries_for_all_posts(queue_client)



def is_reddit_submission_url(url: str) -> bool:
    """
    Returns True only if the URL looks like a Reddit submission (post) URL.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        if "reddit.com" not in parsed.netloc:
            return False

        # Path should contain /r/.../comments/...
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 4:
            return False
        if path_parts[0] != "r" or path_parts[2] != "comments":
            return False

        return True
    except:
        return False
    
def remove_deleted_posts():
    reddit = get_reddit_instance()
    all_posts = Post.objects()  
    all_summarized_posts = SummarizedPost.objects()

    # Example: print them
    for doc in all_summarized_posts:
        url = doc.url
        if not is_reddit_submission_url(url):
            doc.delete()
            logging.info(f"SummarizedPost deleted: {url} due to invalid url, removed from DB.")
            continue
        post = reddit.submission(url=url)
        if post.selftext == '[deleted]' or post.title == '[deleted]':
            doc.delete()
            logging.info(f"SummarizedPost deleted: {url}, removed from DB.")
    
    for doc in all_posts:
        url = doc.url
        if not is_reddit_submission_url(url):
            doc.delete()
            logging.info(f"Post deleted: {url} due to invalid url, removed from DB.")
            continue
        post = reddit.submission(url=url)
        if post.selftext == '[deleted]' or post.title == '[deleted]':
            Post.objects(url=url).delete()
            logging.info(f"Post deleted: {url}, removed from DB.")

if __name__ == "__main__":
    remove_deleted_posts()