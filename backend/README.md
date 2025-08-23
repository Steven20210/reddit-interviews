# InterviewsDB Backend

This backend provides a FastAPI server for fetching and processing Reddit interview posts.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:

```
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=interviewsdb-bot/0.1
GROQ_TOKEN=your_groq_api_token
```

## Running the Server

### Option 1: Using the run script

```bash
python run_server.py
```

### Option 2: Using uvicorn directly

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The server will be available at:

- Main server: http://localhost:8000
- API documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### GET /

Health check endpoint that returns a simple message.

### POST /api/fetch-reddit-posts

Fetches new Reddit posts and processes them into summaries.

**Response:**

```json
{
  "success": true,
  "message": "Reddit posts fetched and processed successfully",
  "reddit_posts_count": 1234,
  "summaries_count": 567
}
```

### GET /api/stats

Returns current statistics about the data.

**Response:**

```json
{
  "reddit_posts_count": 1234,
  "summaries_count": 567
}
```

## Frontend Integration

The frontend (Next.js app) can call the `/api/fetch-reddit-posts` endpoint to trigger new post fetching. The button is available in the main interface and will:

1. Show a loading state while fetching
2. Display success/error messages
3. Automatically reload the page after successful fetch to show new data

## CORS Configuration

The server is configured to allow requests from:

- http://localhost:3000
- http://127.0.0.1:3000

This allows the Next.js frontend to communicate with the FastAPI backend.
