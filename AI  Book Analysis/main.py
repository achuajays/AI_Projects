import streamlit as st
import json
import os
from dotenv import load_dotenv
import serpapi
from groq import Groq

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Book Finder",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 5px;
        height: 3em;
        border: none;
    }
    .stButton > button:hover {
        background-color: #FF6B6B;
    }
    .book-card {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ"))


def fetch_books(query):
    params = {
        "api_key": os.getenv("SERPAPI_KEY"),
        "engine": "google_play_books",
        "q": query,
        "hl": "en",
        "gl": "us"
    }

    search = serpapi.search(params)
    results = search
    books_data = []

    for section in results.get("organic_results", []):
        if "items" in section:
            for item in section["items"]:
                books_data.append({
                    "title": item.get("title", "N/A"),
                    "author": item.get("author", "N/A"),
                    "volume": item.get("extension", {}).get("name", "N/A"),
                    "category": item.get("category", "N/A"),
                    "price": item.get("price", "N/A"),
                    "rating": item.get("rating", "N/A"),
                    "description": item.get("description", "N/A"),
                    "link": item.get("link", "N/A"),
                    "thumbnail": item.get("thumbnail", "N/A"),
                })

    return books_data


def get_best_book(books, preference):
    if not books:
        return "No books found for the given query."

    top_books = books[0:10]
    prompt = f"""
    You are an expert in book recommendations. Given the following books and user preference, 
    recommend the best book.

    User preference: {preference}

    Books:
    {json.dumps(top_books, indent=2)}

    Provide the title of the best book along with a short explanation.
    """

    chat_completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=200
    )

    return chat_completion.choices[0].message.content


# Sidebar for search and preferences
with st.sidebar:
    st.image("https://raw.githubusercontent.com/streamlit/docs/main/public/favicon.svg", width=100)
    st.title("Search Settings")
    query = st.text_input("📝 Search Books", placeholder="E.g., Jujutsu Kaisen, Python Programming")
    preference = st.text_area("🎯 Your Preferences",
                              placeholder="E.g., I like action-packed stories with deep character development.",
                              height=150)
    search_button = st.button("🔍 Search Books")

# Main content area
st.title("📚 AI-Powered Book Finder")
st.markdown("---")

if search_button:
    if not query.strip():
        st.error("⚠️ Please enter a search query.")
    else:
        with st.spinner("🔍 Searching for books..."):
            books = fetch_books(query)

        if not books:
            st.warning("📢 No books found. Try a different query.")
        else:
            # Display results in columns
            st.subheader(f"📖 Found {len(books)} Books")

            # Best recommendation section
            if preference:
                with st.spinner("🤖 AI is finding the best book for you..."):
                    best_book = get_best_book(books, preference)

                st.markdown("""
                    <div style='background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                        <h3>🏆 AI's Top Pick</h3>
                    </div>
                """, unsafe_allow_html=True)
                st.write(best_book)
                st.markdown("---")

            # Display books in a grid
            cols = st.columns(2)
            for idx, book in enumerate(books):
                with cols[idx % 2]:
                    st.markdown("""
                        <div class='book-card'>
                        """, unsafe_allow_html=True)

                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(book['thumbnail'], width=150)
                    with col2:
                        st.markdown(f"### [{book['title']}]({book['link']})")
                        st.markdown(f"**Author:** {book['author']}")
                        st.markdown(f"**Category:** {book['category']}")
                        st.markdown(f"**Price:** {book['price']}")
                        if book['rating'] != 'N/A':
                            st.markdown(f"**Rating:** {'⭐' * int(float(book['rating']))}")

                    with st.expander("📖 Read Description"):
                        st.write(book['description'])

                    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ using Streamlit, SerpAPI, and Groq AI</p>
    </div>
""", unsafe_allow_html=True)