# Reddit Interview Experience Database

A comprehensive full-stack application that automatically collects, processes, and presents interview experiences from Reddit. The system uses AI to extract structured information from Reddit posts and comments, providing a searchable database of real interview experiences from top tech companies.

## 🚀 Features

- **Automated Data Collection**: Fetches interview posts from r/csmajors and r/leetcode using Reddit API
- **AI-Powered Processing**: Uses Groq API to intelligently extract and summarize interview information
- **Comment Integration**: Analyzes both original posts and top comments for comprehensive insights
- **Smart Filtering**: Advanced filtering by company, role, and relevance scoring
- **Modern Web Interface**: Built with Next.js 14, TypeScript, and shadcn/ui components
- **Real-time Search**: Fast, paginated search with debounced queries
- **Responsive Design**: Optimized for desktop and mobile devices
- **Rate Limiting**: Built-in API protection with ephemeral token authentication
- **Cloud Infrastructure**: Deployed on Azure with MongoDB Atlas and Azure Functions

## 🏗️ Architecture

### Backend Services

- **FastAPI Server** (`backend/app.py`): REST API with authentication and rate limiting
- **Reddit Collector** (`backend/reddit_collector.py`): Automated data fetching from Reddit API
- **AI Processing** (`backend/ai_processing.py`): Groq API integration for intelligent summarization
- **Azure Functions** (`jobs/ScrapeRedditJob/`): Scheduled daily data collection
- **Queue System** (`aqs/queue_handlers.py`): Azure Queue for asynchronous processing
- **Database Layer** (`db/handlers.py`): MongoDB with MongoEngine ODM

### Frontend Application

- **Next.js 14** with App Router and TypeScript
- **shadcn/ui** component library with Tailwind CSS
- **Real-time Search** with debounced queries and pagination
- **Advanced Filtering** by company and role with searchable dropdowns
- **Responsive Design** with mobile-first approach

### Infrastructure

- **Database**: MongoDB Atlas (Cosmos DB)
- **Queue**: Azure Storage Queue
- **Functions**: Azure Functions for scheduled jobs
- **Authentication**: HMAC-based ephemeral tokens
- **Rate Limiting**: SlowAPI with configurable limits

## 📋 Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB Atlas account
- Azure account (for queue and functions)
- Reddit API credentials
- Groq API key

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/reddit-interviews.git
cd reddit-interviews
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
# or
yarn install
# or
pnpm install
```

### 4. Environment Configuration

Create a `.env` file in the `backend` directory:

```env
# Reddit API Configuration
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=interviewsdb-bot/0.1

# AI Processing
GROQ_TOKEN=your_groq_api_token

# Database
COSMODB_CONNSTR=mongodb+srv://username:password@cluster.mongodb.net/reddit-interview?retryWrites=true&w=majority

# Azure Services
AZURE_QUEUE_CONN=DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=yourkey;EndpointSuffix=core.windows.net

# Authentication
HMAC_SECRET=your_hmac_secret_key

# Frontend URL (for CORS)
REDDIT_INTERVIEWS_FRONTEND_URL=http://localhost:3000
```

#### Getting API Credentials

**Reddit API:**

1. Go to https://www.reddit.com/prefs/apps
2. Create a new app (select "script")
3. Note your client ID and client secret

**Groq API:**

1. Sign up at https://console.groq.com/
2. Generate an API key
3. Add it to your environment variables

**MongoDB Atlas:**

1. Create a cluster at https://cloud.mongodb.com/
2. Get your connection string
3. Create a database named `reddit-interview`

**Azure Storage:**

1. Create a storage account in Azure Portal
2. Get the connection string from Access Keys
3. Create a queue named `reddit-posts`

## 🚀 Running the Application

### Start the Backend

```bash
cd backend

# Activate virtual environment (if not already active)
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run the server
python run_server.py
```

The backend will be available at:

- API: http://localhost:8000
- Documentation: http://localhost:8000/docs

### Start the Frontend

```bash
cd frontend

# Development mode
npm run dev
# or
yarn dev
# or
pnpm dev
```

The frontend will be available at http://localhost:3000

## 📊 API Endpoints

### Authentication

#### GET /token

Generates an ephemeral authentication token (valid for 60 seconds)

**Response:**

```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Search & Data

#### POST /search

Searches interview experiences with filtering and pagination

**Request Body:**

```json
{
  "query": "system design",
  "company": "Google",
  "role": "SDE II",
  "page": 1,
  "limit": 10
}
```

**Response:**

```json
{
  "total": 150,
  "page": 1,
  "limit": 10,
  "results": [
    {
      "_id": "64f1a2b3c4d5e6f7g8h9i0j1",
      "raw_post": "Title: Google SDE II Interview Experience...",
      "summary": "Company: Google\nRole: SDE II\nSummary:...",
      "url": "https://reddit.com/r/csmajors/comments/...",
      "company": "Google",
      "role": "SDE II"
    }
  ],
  "companies": ["Google", "Microsoft", "Amazon"],
  "roles": ["SDE I", "SDE II", "SDE III"]
}
```

#### GET /

Health check endpoint

**Response:**

```json
{
  "message": "InterviewsDB API is running"
}
```

## 🎯 Usage

1. **Start both servers** (backend and frontend)
2. **Search for interviews** using the search bar
3. **Filter by company or role** using the dropdown menus
4. **View detailed summaries** with AI-extracted information
5. **Read full experiences** by expanding posts
6. **Navigate pages** using the pagination controls

## 🔧 Configuration

### Backend Configuration

- **Subreddits**: Modify `SUBREDDITS` in `backend/reddit_collector.py`
- **Search Queries**: Update `QUERIES` array for different search terms
- **AI Prompts**: Customize prompts in `backend/ai_processing.py`
- **Rate Limits**: Adjust limits in `backend/app.py`

### Frontend Configuration

- **API Endpoint**: Set `NEXT_PUBLIC_BACKEND_API_ENDPOINT` environment variable
- **UI Components**: Customize components in `frontend/components/`
- **Styling**: Modify `frontend/styles/globals.css`

### Azure Functions

The system includes an Azure Function that runs daily to collect new posts:

```python
# jobs/ScrapeRedditJob/function_app.py
@app.timer_trigger(schedule="0 0 0 * * *", arg_name="myTimer", run_on_startup=True)
def ScrapeRedditJob(myTimer: func.TimerRequest) -> None:
    fetch_and_store_posts(time_filter='day')
```

## 📁 Project Structure

```
reddit-interviews/
├── backend/                    # FastAPI backend
│   ├── app.py                 # Main FastAPI application
│   ├── reddit_collector.py    # Reddit data collection
│   ├── ai_processing.py       # AI summarization logic
│   ├── run_server.py          # Server startup script
│   └── test.py               # Backend tests
├── frontend/                   # Next.js frontend
│   ├── app/                   # Next.js app directory
│   │   ├── page.tsx          # Main search interface
│   │   ├── layout.tsx        # App layout
│   │   └── globals.css       # Global styles
│   ├── components/            # React components
│   │   └── ui/               # shadcn/ui components
│   ├── lib/                   # Utility functions
│   └── package.json          # Node.js dependencies
├── db/                        # Database layer
│   └── handlers.py           # MongoDB models and operations
├── aqs/                       # Azure Queue System
│   └── queue_handlers.py     # Queue operations
├── middleware/                # Authentication middleware
│   └── auth.py               # Token generation and verification
├── jobs/                      # Azure Functions
│   └── ScrapeRedditJob/      # Scheduled data collection
│       └── function_app.py   # Azure Function implementation
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🚀 Deployment

### Backend Deployment

The backend can be deployed to various platforms:

**Railway:**

1. Connect your GitHub repository
2. Set root directory to `backend/`
3. Add environment variables
4. Deploy

**Render:**

1. Create a new Web Service
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

### Frontend Deployment

**Vercel (Recommended):**

1. Import your GitHub repository
2. Set root directory to `frontend/`
3. Add environment variable: `NEXT_PUBLIC_BACKEND_API_ENDPOINT`
4. Deploy

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Azure Functions Deployment

Deploy the scheduled job to Azure Functions:

```bash
cd jobs/ScrapeRedditJob
func azure functionapp publish your-function-app-name
```

## 🔒 Security Features

- **Ephemeral Tokens**: Short-lived authentication tokens (60 seconds)
- **Rate Limiting**: Configurable API rate limits
- **CORS Protection**: Restricted to specific frontend URLs
- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Comprehensive error handling and logging

## 📈 Performance

- **Pagination**: Efficient data loading with configurable page sizes
- **Debounced Search**: Reduces API calls during typing
- **Caching**: MongoDB indexing for fast queries
- **Async Processing**: Azure Queue for background tasks
- **CDN**: Vercel's global CDN for frontend assets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Reddit API](https://www.reddit.com/dev/api/) for data access
- [Groq API](https://console.groq.com/) for AI processing
- [Next.js](https://nextjs.org/) for the frontend framework
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [shadcn/ui](https://ui.shadcn.com/) for UI components
- [MongoDB Atlas](https://cloud.mongodb.com/) for database hosting
- [Azure](https://azure.microsoft.com/) for cloud infrastructure

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/reddit-interviews/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## 🔄 Data Collection

The application automatically collects new interview posts daily through:

1. **Scheduled Azure Function**: Runs every day at midnight UTC
2. **Reddit API**: Fetches posts from configured subreddits
3. **AI Processing**: Extracts structured information using Groq
4. **Queue System**: Processes posts asynchronously
5. **Database Storage**: Stores processed data in MongoDB

## ⚠️ Important Disclaimer

This application is for **educational and research purposes only**. All interview experiences are collected from public Reddit posts and are user-generated content. Please respect Reddit's terms of service and API usage guidelines. The information provided may not be accurate, complete, or up-to-date. Always verify information from official sources and consult with professionals for career advice.

---

**Note**: This application demonstrates modern full-stack development practices including microservices architecture, cloud deployment, AI integration, and real-time data processing.
