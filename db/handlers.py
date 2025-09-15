from mongoengine import connect, Document, StringField, DictField, BooleanField, ListField, IntField
import logging 
import os
from dotenv import load_dotenv
load_dotenv()
# Connect to local MongoDB
connect(host=os.getenv("COSMODB_CONNSTR"), db="reddit-interview", tls=True)

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
    def upsert_post(cls, input_url: str, payload: dict, new_hash: str) -> bool:
        logging.info(f"Upserting post with URL: {input_url} and hash: {new_hash}")
        try:
            existing = cls.objects(url=input_url).first()
            if existing:
                if existing.hash != new_hash:
                    existing.hash = new_hash
                    existing.payload = payload
                    existing.save()
                    print(f"Replaced existing post with new hash: {input_url}")
                else:
                    print(f"Post already exists with same hash: {input_url}")
                    return False
            else:
                cls(url=input_url, hash=new_hash, payload=payload).save()
                print(f"Inserted new post: {input_url}")
        except Exception as e:
            logging.error(f"Caught an exception: {e}")
        return True

class SummarizedPost(Document):
    url = StringField(required=True, unique=True)
    hash = StringField(required=True)
    company = StringField(required=True)
    role = StringField(required=True)
    summary = StringField(required=True)
    raw_post = StringField(required=True)
    payload = DictField(required=False)
    timestamp = IntField(required=True)
    
    meta = {
        'collection': 'summarized_posts',
        'indexes': [
            {'fields': ['url'], 'unique': True}
        ]
    }

    @classmethod
    def upsert_post(cls, url: str, summary: str, raw_post: str, new_hash: str, role: str, company: str, timestamp: int) -> None:
        existing = cls.objects(url=url).first()
        if existing:
            if existing.hash != new_hash:
                existing.hash = new_hash
                existing.summary = summary
                existing.save()
                print(f"Replaced existing summarized post with new hash: {url}")
            else:
                print(f"Summarized post already exists with same hash: {url}")
                return False
        else:
            logging.info(f"Upserting summarized post with URL: {url} and hash: {new_hash}")
            cls(url=url, hash=new_hash, summary=summary, raw_post=raw_post, role=role, company=company, timestamp=timestamp).save()
            print(f"Inserted new summarized post: {url}")
        return True
class CompanyMetadata(Document):
    company = StringField(required=True, unique=True)
    roles = ListField(StringField(), default=list)

    meta = {
        'collection': 'company_metadata',
        'indexes': [
            {'fields': ['company'], 'unique': True}
        ]
    }

    @classmethod
    def upsert_metadata(cls, company: str, role: str) -> None:
        existing = cls.objects(company=company).first()
        if existing:
            if role not in existing.roles:
                existing.roles.append(role)
            existing.save()
            print(f"Updated metadata for company: {company}")
        else:
            logging.info(f"Upserting metadata for company: {company}")
            cls(company=company, roles=[role]).save()
            print(f"Inserted new metadata for company: {company}")