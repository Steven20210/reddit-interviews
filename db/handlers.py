from mongoengine import connect, Document, StringField, DictField, BooleanField
from mongoengine.errors import NotUniqueError
from typing import Type, Union
import logging 
# Connect to local MongoDB
connect(db="mydb", host="localhost", port=27017)

class Post(Document):
    url = StringField(required=True, unique=True)
    payload = DictField(required=True)
    hash = StringField(required=True, unique=True)  # unique hash
    meta = {
        'collection': 'posts',
        'indexes': [
            {'fields': ['url'], 'unique': True}  # enforce unique URL
        ],
        'allow_inheritance': True
    }

    processed = BooleanField(default=False)

    @classmethod
    def upsert_post(cls, input_url: str, payload: dict, new_hash: str) -> None:
        logging.info(f"Upserting post with URL: {input_url} and hash: {new_hash}")
        for post in cls.objects:
            logging.info(post)
        logging.info([doc.to_mongo().to_dict() for doc in cls.objects])
        arr =  [doc.url for doc in cls.objects]
        logging.info(arr)
        existing = cls.objects(url=input_url).first()
        # logging.info(existing)
        if existing:
            if existing.hash != new_hash:
                existing.hash = new_hash
                existing.payload = payload
                existing.save()
                print(f"Replaced existing post with new hash: {input_url}")
            else:
                print(f"Post already exists with same hash: {input_url}")
        else:
            cls(url=input_url, hash=new_hash, payload=payload).save()
            print(f"Inserted new post: {input_url}")


class SummarizedPost(Document):
    url = StringField(required=True, unique=True)
    hash = StringField(required=True)
    company = StringField(required=True)
    role = StringField(required=True)
    summary = StringField(required=True)
    raw_post = StringField(required=True)
    payload = DictField(required=False)

    meta = {
        'collection': 'summarized_posts',
        'indexes': [
            {'fields': ['url'], 'unique': True}
        ]
    }

    @classmethod
    def upsert_post(cls, url: str, summary: str, raw_post: str, new_hash: str, role: str, company: str) -> None:
        existing = cls.objects(url=url).first()
        if existing:
            if existing.hash != new_hash:
                existing.hash = new_hash
                existing.summary = summary
                existing.save()
                print(f"Replaced existing summarized post with new hash: {url}")
            else:
                existing.role = role
                existing.company = company
                existing.save()
                print(f"Summarized post already exists with same hash: {url}")
        else:
            logging.info(f"Upserting summarized post with URL: {url} and hash: {new_hash}")
            cls(url=url, hash=new_hash, summary=summary, raw_post=raw_post, role=role, company=company).save()
            print(f"Inserted new summarized post: {url}")
    
