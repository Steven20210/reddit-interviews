import azure.functions as func
import datetime
import json
import logging
from backend.reddit_collector import fetch_and_store_posts
import requests
app = func.FunctionApp()

@app.timer_trigger(schedule="0 0 0 * * *", arg_name="myTimer", run_on_startup=True)
def ScrapeRedditJob(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')
    logging.info("Starting Reddit scraping job")
    fetch_and_store_posts(time_filter='day')  # fetches this day's posts
    logging.info('Python timer trigger function executed.')