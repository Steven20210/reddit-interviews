# Reddit Interviews Database

A full-stack web application that collects, processes, and displays interview experiences from Reddit. The application automatically fetches interview-related posts from tech subreddits, uses AI to extract and summarize key information, and presents them in a searchable, filterable interface.

## 🚀 Features

- **Automated Data Collection**: Fetches interview posts from r/csmajors and r/leetcode
- **AI-Powered Summarization**: Uses Groq API to extract structured interview information
- **Smart Filtering**: Filters posts by relevance and interview-specific content
- **Modern Web Interface**: Built with Next.js and Tailwind CSS
- **Real-time Updates**: Fetch new posts on-demand
- **Search & Filter**: Find interviews by company, role, or keywords
- **Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

### Backend (FastAPI)

- **Data Collection**: Reddit API integration using PRAW
- **AI Processing**: Groq API for intelligent summarization
- **REST API**: FastAPI endpoints for data retrieval and processing
- **CORS Support**: Configured for frontend communication

### Frontend (Next.js)

- **Modern UI**: Built with shadcn/ui components
- **TypeScript**: Full type safety
- **Real-time Updates**: Fetch and display new data
- **Search & Filter**: Advanced filtering capabilities
- **Responsive**: Mobile-first design

## 📋 Prerequisites

- Python 3.8+
- Node.js 18+
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

# Create .env file
cp .env.example .env
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

Create a `.env` file in the `backend` directory with the following variables:

```env
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=interviewsdb-bot/0.1
GROQ_TOKEN=your_groq_api_token
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

### GET /

Health check endpoint

### POST /api/fetch-reddit-posts

Fetches new Reddit posts and processes them into summaries

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

Returns current statistics about the data

**Response:**

```json
{
  "reddit_posts_count": 1234,
  "summaries_count": 567
}
```

## 🎯 Usage

1. **Start both servers** (backend and frontend)
2. **Fetch new data** by clicking the "Fetch New Posts" button
3. **Search and filter** interviews using the search bar and filters
4. **View detailed summaries** by clicking on interview cards
5. **Filter by company or role** using the dropdown menus

## 🔧 Configuration

### Backend Configuration

The backend can be configured by modifying the following files:

- `backend/reddit_collector.py`: Adjust subreddits, search queries, and filtering criteria
- `backend/ai_processing.py`: Modify AI prompts and processing logic
- `backend/app.py`: Configure CORS, endpoints, and server settings

### Frontend Configuration

- `frontend/app/page.tsx`: Modify the main interface and data display
- `frontend/components/`: Customize UI components
- `frontend/styles/`: Adjust styling and themes

## 📁 Project Structure

```
reddit-interviews/
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── reddit_collector.py    # Reddit data collection
│   ├── ai_processing.py       # AI summarization logic
│   ├── requirements.txt       # Python dependencies
│   ├── run_server.py         # Server startup script
│   └── README.md             # Backend documentation
├── frontend/
│   ├── app/                  # Next.js app directory
│   ├── components/           # React components
│   ├── styles/              # CSS styles
│   ├── package.json         # Node.js dependencies
│   └── tsconfig.json        # TypeScript configuration
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

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

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/reddit-interviews/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## 🔄 Updates

The application automatically fetches new interview posts from Reddit. You can manually trigger updates using the "Fetch New Posts" button in the web interface.

---

**Note**: This application is for educational and research purposes. Please respect Reddit's terms of service and API usage guidelines.
