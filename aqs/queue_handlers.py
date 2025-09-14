from azure.storage.queue import QueueClient
from db.handlers import Post
import json, os
from typing import Callable
from dotenv import load_dotenv
from azure.core.exceptions import ResourceExistsError

def ensure_queue_exists(conn_str: str, queue_name: str) -> QueueClient:
    """
    Ensure that the given queue exists. If it already exists, do nothing.
    
    :param conn_str: Azure Storage connection string
    :param queue_name: Name of the queue
    :return: QueueClient instance
    """
    queue_client = QueueClient.from_connection_string(conn_str, queue_name)
    try:
        queue_client.create_queue()
        print(f"Created queue '{queue_name}'")
    except ResourceExistsError:
        # Safe to ignore — queue is already there
        print(f" Queue '{queue_name}' already exists")
    return queue_client


def enqueue_post(queue_client, model, url, payload, hash):
    # Upsert in MongoDB
    enque = model.upsert_post(url, payload, hash)
    
    # Push a message to Azure Queue
    if enque:
        queue_client.send_message(json.dumps({"url": url, "hash": hash, "payload": payload}))
    
    
def consume_messages(queue_client, callback: Callable[[Post], None], batch_size: int = 10):
    """
    Consume messages from the queue, update posts, and trigger a callback.

    Args:
        queue_client: Azure QueueClient instance
        callback: A function that accepts a Post object
        batch_size: Number of messages to pull per request
    """
    messages = queue_client.receive_messages(messages_per_page=batch_size)

    for msg in messages:
        try:
            data = json.loads(msg.content)
            post = Post.objects(url=data["url"]).first()

            if post:
                print(f"Processing: {post.url}")
                post.update(set__processed=True)

                # Trigger callback with the Post object
                callback(post)

            # Always delete the message after processing attempt
            queue_client.delete_message(msg)

        except Exception as e:
            print(f"Error processing message: {e}")
    