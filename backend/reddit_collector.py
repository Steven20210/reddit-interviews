import os
import praw
from dotenv import load_dotenv
import re
import json 
from collections import Counter
from ai_processing import create_summaries_for_all_posts
import hashlib

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

# Major tech companies for interview experience searches
COMPANIES = [
    # FAANG+ Companies
    # "Apple", "Google", "Meta", "Amazon", "Microsoft", "Netflix", "Tesla",
    
    # Cloud & Enterprise Software
    # "Salesforce", "Oracle", "Adobe"
    
    # # AI & Data
    # "Palantir"
    
    # # Social Media & Communication
    # "Twitter", "LinkedIn", "Snapchat", "Discord", "Slack", "Zoom",
    
    # # E-commerce & Fintech
    "Shopify", "Stripe", "Square", "PayPal", "DoorDash", "Instacart", "Airbnb",
    
    # # Gaming & Entertainment
    # "Roblox", "Unity", "Epic Games", "Twitch", "Spotify", "Pinterest",
    
    # # Hardware & Semiconductor
    # "Intel", "NVIDIA", "AMD", "Qualcomm", "Cisco", "IBM",
    
    # # Developer Tools & Platforms
    # "GitHub", "GitLab", "Hashicorp", "Docker", "JetBrains", "Stack Overflow",
    
    # # Emerging Tech
    # "SpaceX", "Coinbase", "Robinhood", "Uber",
    
    # # Chinese Tech Giants
    # "Alibaba", "Tencent", "Baidu", "ByteDance"
]

QUERIES = [
    # Company-specific interview experience queries
    # "palantir interview"
    # *[f'"{company} interview" experience' for company in COMPANIES],
    # # General interview experience queries (keeping some original ones)
    '(title:"interview" OR title:"experience") AND title:(oa OR onsite OR final OR phone OR screening)',
    '(title:"interview" OR title:"experience") AND title:(oa OR hackerrank OR leetcode OR coding)',
    '(title:"interview" OR title:"experience") AND title:("system design" OR architecture OR hld OR lld)',
    # '(title:"interview" OR title:"experience") AND title:(behavioral OR "leadership principles" OR hr OR recruiter)',
    # '(title:"interview" OR title:"experience") AND title:(intern OR internship OR "new grad" OR campus)',
    # '(title:"interview" OR title:"experience") AND title:(phone OR recruiter OR screening OR first OR initial)',
    # '(title:"interview" OR title:"experience") AND title:(onsite OR "final round" OR panel OR loop)',
    # '(title:"interview" OR title:"experience") AND title:(round OR screening OR final OR onsite OR oa OR phone) -AM -trading -crypto',
    # '(title:"interview" OR title:"experience") AND title:(SDE OR engineer OR "software dev" OR "data engineer")',
    # 'title:(interview OR experience OR onsite OR oa OR "phone screen" OR "final round")'
]

# for company in COMPANIES:
#     QUERIES.append(f"{company} interview experience")

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

def fetch_and_store_posts(minlength=400, score_threshold=3, time_filter='year'):
    reddit = get_reddit_instance()
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

    output_path = "reddit_data.json"
    # Try to load existing array, else start new
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if not isinstance(existing, list):
                existing = [existing]
        except Exception:
            existing = []
    else:
        existing = []
    # Add new posts
    existing.extend(all_data)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    deduplicate_reddit_data_file()
    create_summaries_for_all_posts()

def deduplicate_json_list(json_list, hash_file="hashes.txt"):
    """
    Removes duplicate JSON objects from a list based on a hash of their content.
    Stores seen hashes in a persistent file.
    Returns a deduplicated list.
    """
    # Load existing hashes from file
    if os.path.exists(hash_file):
        with open(hash_file, "r", encoding="utf-8") as f:
            hash_set = set(line.strip() for line in f if line.strip())
    else:
        hash_set = set()

    deduped = []
    new_hashes = set()
    for obj in json_list:
        # Use a stable hash of the JSON string (sorted keys for consistency)
        obj_str = json.dumps(obj, sort_keys=True, ensure_ascii=False)
        obj_hash = hashlib.sha256(obj_str.encode("utf-8")).hexdigest()
        if obj_hash not in hash_set and obj_hash not in new_hashes:
            deduped.append(obj)
            new_hashes.add(obj_hash)
        # If hash exists, skip (delete from list)

    # Update persistent hash file
    with open(hash_file, "a", encoding="utf-8") as f:
        for h in new_hashes:
            f.write(h + "\n")

    return deduped

def deduplicate_reddit_data_file(input_file="reddit_data.json", hash_file="hashes.txt"):
    output_path = "reddit_data.json"
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        deduped_data = deduplicate_json_list(data)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(deduped_data, f, ensure_ascii=False, indent=2)
            
if __name__ == "__main__":
    fetch_and_store_posts(time_filter='day')   # fetches today's posts
    fetch_and_store_posts(time_filter='week')  # fetches this week's posts
    # fetch_and_store_posts(time_filter='month') # fetches this month's posts
    # fetch_and_store_posts(time_filter='year')  # fetches this year's posts
    # fetch_and_store_posts(time_filter='month')  # fetches all posts
    # create_summaries_for_all_posts()