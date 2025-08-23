import os
import requests
from dotenv import load_dotenv
import json
import logging
import time

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

def extract_interview_summary(text):
    prompt = f"""
    
You are an information extractor. 
Extract details about interview experiences only if the text explicitly describes the interview experience of the poster themselves.

If the text is only asking for advice, speculation, or does not describe the interview experience directly, 
respond with exactly:

None

Do not wrap "None" in JSON or code blocks.
ELSE Summarize the interview experience in concise bullet points.
MAKE sure to include the company name and role if mentioned.
Text:
{text}
"""
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
    logging.info("Sending request to Groq API for interview summary extraction.")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        logging.info("Received response from Groq API.")
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        logging.error(f"Groq API request failed: {e}")
        return None


def summarize_post(raw_doc: str, url: str):
    logging.info("Summarizing a Reddit post.")
    summary = extract_interview_summary(raw_doc)
    if summary == "None":
        logging.warning("No summary returned for post.")
    # Write to summary_output.json as a JSON array if the file contains an array, else create a new array
    output_path = "summary_output.json"
    entry = {"raw": raw_doc, "summary": summary, "url": url}
    try:
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        data.append(entry)
                    else:
                        data = [data, entry]
                except json.JSONDecodeError:
                    # File exists but is not valid JSON, start new array
                    data = [entry]
        else:
            data = [entry]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info("Summary written to summary_output.json as array.")
    except Exception as e:
        logging.error(f"Failed to write summary to file: {e}")
    logging.info("Summary written to summary_output.json.")

def create_summaries_for_all_posts():
    logging.info(f"Loading Reddit posts from {RAW_REDDIT_DATA_FILE}.")
    try:
        with open(RAW_REDDIT_DATA_FILE, "r", encoding="utf-8") as f:
            posts = json.load(f)
            logging.info(f"Loaded {len(posts)} posts from file.")
        i = 0
        while i < len(posts):
            raw_doc = posts[i]
            summarize_post(raw_doc.get("title", "") + raw_doc.get("selftext", ""), raw_doc.get("url", ""))
            del posts[i]
            logging.info(f"Deleted processed post at index {i}.")
            i += 1
            time.sleep(4)  # Sleep to avoid hitting API rate limits
            # Write the updated posts list back to the source file after each deletion
        try:
            with open(RAW_REDDIT_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
            logging.info(f"Updated {RAW_REDDIT_DATA_FILE} after deletion.")
        except Exception as e:
            logging.error(f"Failed to update {RAW_REDDIT_DATA_FILE}: {e}")
    except Exception as e:
        logging.error(f"Failed to process posts: {e}")
    filter_summaries()
        
def filter_summaries(input_file="summary_output.json", output_file="filtered_summaries.json"):
    """
    Filters out entries where summary is "None" or null and writes the rest to a new JSON file.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        filtered = [entry for entry in data if entry.get("summary") not in [None, "None", "None \n"]]
        # Write to interview-search frontend directory
        frontend_output_path = os.path.join("..", "interview-search", "public", "filtered_summaries.json")
        with open(frontend_output_path, "w", encoding="utf-8") as f:
            json.dump(filtered, f, ensure_ascii=False, indent=2)
        logging.info(f"Filtered summaries written to {output_file}.")
    except Exception as e:
        logging.error(f"Failed to filter summaries: {e}")

