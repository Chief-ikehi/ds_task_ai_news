# DS Task AI News - Developer Guide

## Project Overview

DS Task AI News is an AI-powered news retrieval and recommendation system that aggregates, processes, and analyzes news articles using cutting-edge AI technologies.

## Development Environment Setup

### Prerequisites
- Python 3.9+
- pip
- Virtual environment (recommended)

### Installation Steps

1. Clone the repository
```bash
git clone http://23.29.118.76:3000/Task/ds_task_ai_news
cd ds-task-ai-news
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

4. Set up NLTK resources
```bash
cd backend
python setup_nltk.py
```

5. Set up environment variables
Create a `.env` file in the backend directory with the following variables:
```
COHERE_API_KEY=your_cohere_api_key
GROQ_API_KEY=your_groq_api_key
```

## Project Structure

### Key Components
- `news_fetcher.py`: Handles news aggregation from RSS feeds
- `embeddings.py`: Generates article embeddings using Cohere
- `vector_store.py`: Manages vector database operations
- `recommender.py`: Generates article recommendations
- `llm_analyzer.py`: Provides AI-powered article analysis
- `main.py`: FastAPI backend with API endpoints

### Data Flow
1. News is fetched from RSS feeds
2. Articles are processed and stored
3. Embeddings are generated
4. Vector database is updated
5. Recommendations and analysis can be generated

## Development Workflow

### Running the Application
```bash
python main.py
```

### Logging
- Logging is configured in each module
- Check individual module logs for detailed information

## Contribution Guidelines

1. Create a new branch for each feature
2. Write clear, concise commit messages
3. Ensure code passes all tests before submitting a PR
4. Update documentation as needed

## Troubleshooting

### Common Issues
- Ensure API keys are correctly set in `.env`
- Check network connectivity for RSS feed fetching
- Verify dependencies are correctly installed

### Debugging
- Use logging to track module-specific issues
- Check API responses in FastAPI Swagger UI