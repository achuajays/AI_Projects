import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ"))

# Streamlit app configuration
st.set_page_config(page_title="AI Recipe Generator", page_icon="🍳")

# App header
st.header("🍳 AI-Powered Recipe Generator")
st.write("Enter ingredients you have, and get instant recipe suggestions!")

# User inputs
with st.form("recipe_form"):
    ingredients = st.text_area(
        "List ingredients (comma-separated):",
        placeholder="e.g., chicken, broccoli, rice, garlic..."
    )
    diet = st.selectbox(
        "Dietary Preference (optional):",
        ["None", "Vegetarian", "Vegan", "Gluten-Free", "Low-Carb", "Dairy-Free"]
    )
    submitted = st.form_submit_button("Generate Recipe")

# When form is submitted
if submitted:
    if not ingredients.strip():
        st.warning("Please enter at least one ingredient!")
    else:
        # Construct the prompt
        prompt = f"Create a detailed recipe using: {ingredients}. "
        if diet != "None":
            prompt += f"The recipe must be {diet}. "
        prompt += """Include a creative recipe title, list of ingredients with 
                    measurements, and step-by-step instructions. Use only 
                    the provided ingredients unless common pantry staples 
                    (salt, pepper, oil). Format clearly with headings."""

        # System message to guide the AI
        system_prompt = """You are an expert chef and recipe creator. 
                        Generate creative, practical recipes based on 
                        user's ingredients and dietary needs. Provide 
                        clear measurements and cooking instructions."""

        # Create chat completion
        with st.spinner("🧑🍳 Generating recipe..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama3-70b-8192",
                    temperature=0.7,
                    max_tokens=1024,
                    top_p=1,
                    stop=None,
                )

                # Display the generated recipe
                recipe = chat_completion.choices[0].message.content
                st.markdown("## Your AI-Generated Recipe")
                st.markdown(recipe.replace("$", "\$").replace("**", ""))  # Escape markdown formatting

            except Exception as e:
                st.error(f"Error generating recipe: {str(e)}")

# Sidebar with instructions
with st.sidebar:
    st.markdown("## How to Use")
    st.write("1. Enter ingredients you have (comma-separated)")
    st.write("2. Select dietary preference if needed")
    st.write("3. Click 'Generate Recipe'")
    st.markdown("---")
    st.markdown("**Example Input:**")
    st.code("chicken, broccoli, garlic, rice\nDiet: None")
    st.markdown("---")
    st.caption("Powered by Groq & Llama3-70B")

# Add some styling
st.markdown("""
    <style>
    .stTextArea textarea {
        min-height: 100px;
    }
    .stMarkdown h2 {
        color: #2e7d32;
    }
    </style>
""", unsafe_allow_html=True)
