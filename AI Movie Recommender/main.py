import streamlit as st
import json
import serpapi
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
# Initialize Groq client
groq_client = Groq(
    api_key=os.getenv("GROQ")
)


def get_movie_recommendations(category):
    # SerpAPI parameters
    params = {
        "api_key": os.getenv("SERPAPI_KEY"),
        "engine": "google_play_movies",
        "hl": "en",
        "gl": "us",
        "movies_category": category
    }

    # Get movies from SerpAPI
    search = serpapi.search(params)
    results = search

    # Extract first 10 movies
    movies = results.get('organic_results', [])[0].get('items', [])[:10]
    return movies


def get_enhanced_recommendations(movies, user_preferences):
    # Prepare movie descriptions for Groq
    movie_descriptions = "\n".join([f"{m['title']}: {m['description']}" for m in movies])

    # Get enhanced recommendations from Groq with user preferences
    prompt = f"""Given these movies and their descriptions:
    {movie_descriptions}

    User preferences: {user_preferences}

    Based on the user's preferences and these movies, please provide:
    1. Common themes across these movies that align with user preferences
    2. Unique storytelling elements that match the user's interests
    3. Top 3 personalized recommendations from this list and why they would particularly appeal to this user
    4. Additional viewing suggestions based on the user's preferences

    Format your response in clear sections."""

    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a film expert who provides personalized movie analysis and recommendations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_completion_tokens=1024
    )

    return chat_completion.choices[0].message.content


def main():
    st.title("🎬 Smart Movie Recommendations")

    # Category selection
    categories = {
        "18": "Indian Cinema",
        "1": "Action & Adventure",
        "4": "Comedy",
        "5": "Drama",
        "10": "Romance"
    }

    # Sidebar for preferences
    st.sidebar.title("Your Preferences")

    # Multiple preference options
    preference_options = {
        "genre_preference": st.sidebar.multiselect(
            "Preferred Genres",
            ["Action", "Romance", "Drama", "Comedy", "Thriller", "Family", "Adventure"]
        ),
        "mood_preference": st.sidebar.select_slider(
            "Preferred Mood",
            options=["Light & Fun", "Balanced", "Deep & Serious"],
            value="Balanced"
        ),
        "content_rating": st.sidebar.multiselect(
            "Content Rating",
            ["G", "PG", "PG-13", "R"]
        ),
        "story_elements": st.sidebar.multiselect(
            "Story Elements",
            ["Strong Character Development", "Plot Twists", "Social Messages", "Family Values", "Action Sequences",
             "Romance"]
        ),
        "duration_preference": st.sidebar.radio(
            "Movie Length",
            ["Short (< 90 min)", "Medium (90-120 min)", "Long (> 120 min)", "Any"]
        )
    }

    selected_category = st.selectbox(
        "Select Movie Category",
        options=list(categories.keys()),
        format_func=lambda x: categories[x]
    )

    if st.button("Get Recommendations"):
        if not any(preference_options.values()):
            st.warning("Please select at least one preference to get personalized recommendations.")
            return

        with st.spinner("Fetching movies..."):
            # Get initial movies from SerpAPI
            movies = get_movie_recommendations(selected_category)

            # Display movies in a grid
            st.subheader("Top 10 Movies")
            cols = st.columns(2)
            for idx, movie in enumerate(movies):
                col = cols[idx % 2]
                with col:
                    st.image(movie['thumbnail'], width=200)
                    st.markdown(f"**{movie['title']}**")
                    st.write(f"Rating: {movie['rating']} ⭐")
                    st.write(f"Price: {movie['price']}")
                    with st.expander("Plot"):
                        st.write(movie['description'])

        # Get enhanced recommendations from Groq
        with st.spinner("Analyzing movies and personalizing recommendations..."):
            analysis = get_enhanced_recommendations(movies, preference_options)

            st.subheader("🎯 Personalized Analysis")
            st.markdown(analysis)

            # Add a feature to save favorites
            if st.button("Save Recommendations"):
                st.session_state['saved_recommendations'] = analysis
                st.success("Recommendations saved! You can access them in the sidebar.")

    # Display saved recommendations in sidebar if they exist
    if 'saved_recommendations' in st.session_state:
        with st.sidebar.expander("Saved Recommendations"):
            st.write(st.session_state['saved_recommendations'])


if __name__ == "__main__":
    st.set_page_config(
        page_title="Smart Movie Recommendations",
        page_icon="🎬",
        layout="wide"
    )
    main()