# DS Task AI News - API Documentation

## Base URL
`http://localhost:8000`

## Authentication
Currently, no authentication is required for API endpoints.

## Endpoints

### 1. Root Endpoint
- **URL**: `/`
- **Method**: GET
- **Description**: Welcome endpoint
- **Response**:
  ```json
  {
    "message": "Welcome to DS Task AI News API"
  }
  ```

### 2. Fetch News
- **URL**: `/fetch-news`
- **Method**: GET
- **Description**: Fetches and processes news articles from configured RSS feeds
- **Response**:
  ```json
  {
    "status": "success",
    "articles": [
      {
        "id": "unique_article_id",
        "title": "Article Title",
        "content": "Article summary",
        "date": "Publication date",
        "link": "Full article URL",
        "source": "RSS feed URL",
        "categories": ["Technology", "AI"],
        "summary": "Extracted article summary"
      }
    ]
  }
  ```

### 3. Recommend News
- **URL**: `/recommend-news`
- **Method**: GET
- **Query Parameters**:
  - `article_id` (required): ID of the article to find similar articles for
- **Description**: Retrieves similar news articles based on the given article
- **Response**:
  ```json
  {
    "status": "success",
    "similar_articles": [
      {
        "id": "similar_article_id",
        "title": "Similar Article Title",
        "content": "Similar article summary"
      }
    ]
  }
  ```

### 4. Analyze Article
- **URL**: `/analyze-article/{article_id}`
- **Method**: GET
- **Path Parameters**:
  - `article_id`: Unique identifier of the article to analyze
- **Description**: Provides AI-generated analysis of a specific article
- **Response**:
  ```json
  {
    "status": "success",
    "article": {
      "id": "article_id",
      "title": "Article Title"
    },
    "analysis": {
      "summary": "Brief article summary",
      "main_topics": ["Topic 1", "Topic 2"],
      "sentiment": "positive/negative/neutral"
    }
  }
  ```

### 5. Topic Clusters
- **URL**: `/topic-clusters`
- **Method**: GET
- **Description**: Generates AI-powered topic clusters from current news articles
- **Response**:
  ```json
  {
    "status": "success",
    "clusters": {
      "cluster_1": {
        "name": "Technology Trends",
        "articles": ["Article 1", "Article 2"]
      }
    }
  }
  ```

### 6. Trending Analysis
- **URL**: `/trending-analysis`
- **Method**: GET
- **Description**: Provides analysis of current trending topics
- **Response**:
  ```json
  {
    "status": "success",
    "trending_analysis": "Detailed trending topics analysis"
  }
  ```

## Error Handling
- All endpoints return a standard error response for failures:
  ```json
  {
    "detail": "Error description"
  }
  ```
- Typical HTTP status codes:
  - 200: Successful request
  - 404: Resource not found
  - 500: Server error

## Rate Limiting
- Currently, no rate limiting is implemented
- Be mindful of API usage to avoid potential service disruptions

## Potential Future Improvements
- Authentication
- More advanced filtering
- Pagination for large result sets