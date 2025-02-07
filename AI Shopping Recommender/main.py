import os
import streamlit as st
import serpapi
from groq import Groq
import json
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Smart Shopping Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main {
        padding: 2rem;
    }
    .stButton>button {
        background-color: #4a90e2;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        border: none;
    }
    .product-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ"))


def search_products(query, location):
    """Search for products using SerpAPI"""
    params = {
        "api_key": os.getenv("SERPAPI_KEY"),
        "engine": "google_shopping",
        "google_domain": "google.com",
        "q": query,
        "hl": "hi",
        "gl": "in",
        "location": location
    }

    try:
        results = serpapi.search(params)
        return results.get('shopping_results', [])
    except Exception as e:
        st.error(f"Error searching products: {str(e)}")
        return []


def analyze_products(products, preferences):
    """Analyze products using Groq based on user preferences"""
    if not products:
        return "No products found to analyze."

    product_data = json.dumps(products[:5], indent=2)
    prompt = f"""Given these products:
{product_data}

And these user preferences:
{preferences}

Please provide a structured analysis in the following format:
1. Top Recommendation: [Product Name]
   - Key Features
   - Match with Preferences
   - Price Analysis

2. Alternative Options (2-3 products)
   - Brief comparison
   - Unique advantages

3. Overall Summary and Buying Advice"""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a knowledgeable shopping assistant skilled in product analysis and comparison."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_completion_tokens=1024,
            top_p=1
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error analyzing products: {str(e)}"


# Main UI
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("🛍️ Smart Shopping Assistant")

# Input section with columns
col1, col2 = st.columns(2)
with col1:
    product_query = st.text_input("🔍 What product are you looking for?",
                                  placeholder="e.g., wireless headphones")
with col2:
    location = st.text_input("📍 Enter your location",
                             placeholder="e.g., Mumbai, India")

preferences = st.text_area("💭 What are your preferences?",
                           placeholder="e.g., budget under ₹5000, noise cancellation, long battery life",
                           height=100)

if st.button("🔍 Search and Analyze", use_container_width=True):
    if product_query and preferences and location:
        with st.spinner("🔎 Searching for products..."):
            products = search_products(product_query, location)

            if products:
                # Display products in a grid
                st.subheader("📦 Found Products")
                for i in range(0, len(products[:6]), 2):
                    col1, col2 = st.columns(2)

                    # First product in row
                    with col1:
                        with st.container():
                            st.markdown(f"""
                            <div class="product-card">
                                <h3>{products[i].get('title')}</h3>
                                <p>💰 Price: {products[i].get('price', 'N/A')}</p>
                                <p>⭐ Rating: {products[i].get('rating', 'N/A')}</p>
                            </div>
                            """, unsafe_allow_html=True)

                    # Second product in row (if exists)
                    if i + 1 < len(products[:6]):
                        with col2:
                            with st.container():
                                st.markdown(f"""
                                <div class="product-card">
                                    <h3>{products[i + 1].get('title')}</h3>
                                    <p>💰 Price: {products[i + 1].get('price', 'N/A')}</p>
                                    <p>⭐ Rating: {products[i + 1].get('rating', 'N/A')}</p>
                                </div>
                                """, unsafe_allow_html=True)

                with st.spinner("🤖 Analyzing products based on your preferences..."):
                    analysis = analyze_products(products, preferences)

                    st.subheader("🎯 Analysis and Recommendations")
                    st.markdown(f"""
                    <div class="product-card">
                        {analysis}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ No products found. Please try a different search term.")
    else:
        st.warning("⚠️ Please fill in all the fields to continue.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Your Smart Shopping Assistant")