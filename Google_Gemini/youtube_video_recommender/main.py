import streamlit as st
import google.generativeai as genai
import serpapi
import os
from dotenv import load_dotenv

# Set page configuration
st.set_page_config(
    page_title="YouTube Search Assistant",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for improved styling
st.markdown("""
    <style>
    .reportview-container {
        background: linear-gradient(to right, #f0f2f6, #e6e9ef);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 20px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .video-card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    .video-card:hover {
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transform: translateY(-5px);
    }
    </style>
    """, unsafe_allow_html=True)

load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SERPAPI_KEY = os.getenv('SERPAPI_KEY')

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)


def extract_search_topic(prompt):
    """
    Use Gemini to extract the main topic from the user's prompt
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        topic_extraction_prompt = f"Extract the main search topic from this prompt: '{prompt}'. " \
                                  "Return only the key topic or search query, without any additional text."
        response = model.generate_content(topic_extraction_prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Error extracting topic: {e}")
        return prompt


def extract_video_details(results):
    """
    Extract specific details from YouTube search results
    """
    processed_results = []
    for video in results:
        try:
            video_info = {
                'title': video.get('title', 'Untitled Video'),
                'link': video.get('link', ''),
                'channel': video.get('channel', {}).get('name', 'Unknown Channel'),
                'channel_link': video.get('channel', {}).get('link', ''),
                'thumbnail': video.get('thumbnail', {}).get('static', ''),
                'views': video.get('views', 'N/A'),
                'published_date': video.get('published_date', 'N/A'),
                'length': video.get('length', 'N/A')
            }
            processed_results.append(video_info)
        except Exception as e:
            print(f"Error processing video: {e}")

    return processed_results


def search_youtube(query):
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
        processed_results = extract_video_details(results)
        return processed_results
    except Exception as e:
        st.error(f"Error searching YouTube: {e}")
        return []


def main():
    # Title and description
    st.title("🔍 YouTube Search Assistant")
    st.markdown("*Discover videos by describing what you want to see!*")

    # User input with improved styling
    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            user_prompt = st.text_input(
                "What would you like to search on YouTube?",
                placeholder="Enter a detailed description of the content you want to find..."
            )

        with col2:
            st.write("")  # Add some spacing
            search_button = st.button("Search Videos", key="search_btn")

    # Search logic
    if search_button or user_prompt:
        if user_prompt:
            # Extract search topic using Gemini
            with st.spinner("Analyzing your request..."):
                search_topic = extract_search_topic(user_prompt)

            st.markdown(f"**Extracted Search Topic:** `{search_topic}`")

            # Search YouTube
            with st.spinner("Searching YouTube..."):
                results = search_youtube(search_topic)

            # Display results
            if results:
                st.subheader("🎥 Search Results")

                for video in results[:5]:  # Limit to top 5 results
                    # Custom card-like display with reduced image size
                    st.markdown(f"""
                    <div class="video-card">
                        <div class="row">
                            <div class="col-md-3">
                                <img src="{video['thumbnail']}" style="width:200px; height:120px; object-fit:cover; border-radius:10px;">
                            </div>
                            <div class="col-md-9">
                                <h4><a href="{video['link']}" target="_blank">{video['title']}</a></h4>
                                <p>
                                <strong>Channel:</strong> <a href="{video['channel_link']}" target="_blank">{video['channel']}</a><br>
                                <strong>Views:</strong> {video['views']} | 
                                <strong>Published:</strong> {video['published_date']} | 
                                <strong>Length:</strong> {video['length']}
                                </p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Add a small separator
                    st.markdown("---")
            else:
                st.warning("🔍 No YouTube videos found for this topic.")


if __name__ == "__main__":
    main()