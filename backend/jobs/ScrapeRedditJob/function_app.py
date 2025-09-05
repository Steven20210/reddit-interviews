import azure.functions as func
import datetime
import json
import logging

import sys
import os
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if os.path.isdir(repo_root):
    sys.path.insert(0, repo_root)
else:
    print(f"Directory does not exist: {repo_root}")

from backend.reddit_collector import fetch_and_store_posts

app = func.FunctionApp()

@app.timer_trigger(schedule="0 */5 * * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def ScrapeRedditJob(myTimer: func.TimerRequest) -> None:
    
    if myTimer.past_due:
        logging.info('The timer is past due!')

    fetch_and_store_posts(time_filter='day')  # fetches this day's posts
    logging.info('Python timer trigger function executed.')