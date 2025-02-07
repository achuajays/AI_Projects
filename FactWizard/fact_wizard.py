# fact_wizard.py
import streamlit as st
from groq import Groq
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


# Initialize Groq client
client = Groq(
    api_key = os.getenv("GROQ")
)



def generate_fun_fact(topic: Optional[str], is_random: bool) -> str:
    """Generate a fun fact using Groq API"""
    if is_random:
        prompt = "Generate a random interesting fun fact about any topic. Make it engaging and surprising."
    else:
        prompt = f"Generate an interesting fun fact about {topic}. Make it engaging and surprising."

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a fun fact generator. Provide concise, interesting, and accurate facts."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_completion_tokens=100,
            top_p=1,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating fact: {str(e)}")
        return None


# Set page config
st.set_page_config(
    page_title="FactWizard ✨",
    page_icon="🧙‍♂️",
    layout="centered"
)

# Main UI
st.title("🧙‍♂️ FactWizard: Your AI Knowledge Explorer")
st.write("Let the magic of AI reveal fascinating facts from across the universe!")

# Sidebar for user input
with st.sidebar:
    st.header("Customize Your Knowledge Spell")

    # Topic selection
    topics = ["Science", "History", "Animals", "Space", "Technology", "Random"]
    selected_topic = st.selectbox("Choose your realm of knowledge:", topics)

    is_random = selected_topic == "Random"

    # Generate button
    generate_button = st.button("Cast Knowledge Spell! ✨", use_container_width=True)

# Main content area
if generate_button:
    with st.spinner("🔮 The wizard is conjuring your fact..."):
        fact = generate_fun_fact(
            topic=None if is_random else selected_topic,
            is_random=is_random
        )

        if fact:
            # Display the fun fact in a nice box
            st.success("Your fact has been revealed!")

            # Create a container for the fact with custom styling
            fact_container = st.container()
            with fact_container:
                st.info(fact)




# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Crafted with 🪄 by FactWizard")

# Display a fun tip
st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Wizard's Tip:** Choose 'Random' to explore all realms of knowledge!")