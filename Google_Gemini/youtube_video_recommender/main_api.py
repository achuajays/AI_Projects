import os
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import serpapi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SERPAPI_KEY = os.getenv('SERPAPI_KEY')

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(
    title="YouTube Search API",
    description="An API for searching YouTube videos using Gemini topic extraction and SerpAPI"
)

origins = [
    "http://localhost:3000",  # Example: React frontend running locally
    "https://yourdomain.com",  # Example: Production domain
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Domains that are allowed to access the API
    allow_credentials=True,  # Allow cookies and other credentials
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class SearchRequest(BaseModel):
    prompt: str


class VideoResult(BaseModel):
    title: str
    link: str
    channel: str
    channel_link: str
    thumbnail: str
    views: str
    published_date: str
    length: str


def extract_search_topic(prompt: str) -> str:
    """
    Use Gemini to extract the main topic from the user's prompt
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Prompt to extract the core search topic
        topic_extraction_prompt = f"Extract the main search topic from this prompt: '{prompt}'. " \
                                  "Return only the key topic or search query, without any additional text."
        response = model.generate_content(topic_extraction_prompt)
        return response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting topic: {str(e)}")


def extract_video_details(results: List[Dict]) -> List[VideoResult]:
    """
    Extract specific details from YouTube search results
    """
    processed_results = []
    for video in results:
        try:
            # Convert views to string if it's not already
            views = str(video.get('views', 'N/A')) if isinstance(video.get('views'), (int, str)) else 'N/A'

            # Extract only the details we need
            video_info = VideoResult(
                title=video.get('title', 'Untitled Video'),
                link=video.get('link', ''),
                channel=video.get('channel', {}).get('name', 'Unknown Channel'),
                channel_link=video.get('channel', {}).get('link', ''),
                thumbnail=video.get('thumbnail', {}).get('static', ''),
                views=views,
                published_date=video.get('published_date', 'N/A'),
                length=video.get('length', 'N/A')
            )
            processed_results.append(video_info)
        except Exception as e:
            print(f"Error processing video: {e}")

    return processed_results

def search_youtube(query: str) -> List[VideoResult]:
    """
    Search YouTube using SerpAPI
    """
    try:
        params = {
            "engine": "youtube",
            "search_query": query,
            "api_key": SERPAPI_KEY
        }
        search = serpapi.search(params)
        results = search.get("video_results", [])

        # Process and extract specific details
        return extract_video_details(results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching YouTube: {str(e)}")


@app.post("/search", response_model=List[VideoResult])
async def youtube_search(request: SearchRequest):
    """
    Endpoint to search YouTube videos

    - Takes a text prompt
    - Extracts the main search topic using Gemini
    - Searches YouTube and returns top results
    """
    # Extract search topic using Gemini
    search_topic = extract_search_topic(request.prompt)

    # Search YouTube and return results
    results = search_youtube(search_topic)

    return results


# Optional: Add a simple health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
