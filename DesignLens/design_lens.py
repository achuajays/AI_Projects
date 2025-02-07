import streamlit as st
from groq import Groq
import base64
from typing import Optional
import json
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
# Initialize Groq client
client = Groq(
    api_key = os.getenv("GROQ")
)


def encode_image(uploaded_file) -> str:
    """Encode uploaded image to base64 string"""
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')


def get_ux_suggestions(image_base64: Optional[str] = None, description: str = "", concerns: str = "") -> dict:
    """Generate UX suggestions using Groq API"""

    # Construct the prompt
    prompt = """You are a UX expert analyzing a user interface. Provide specific, actionable suggestions for improvement.
    Focus on:
    - Layout and visual hierarchy
    - Call-to-action effectiveness
    - Color and contrast
    - Typography and readability
    - Navigation and user flow

    Format suggestions as a JSON object with:
    - high_priority: list of critical improvements
    - medium_priority: list of important but not urgent changes
    - low_priority: list of nice-to-have improvements
    - rationale: explanation for each suggestion
    """

    messages = [{"role": "system", "content": prompt}]

    # Add user input to the message
    user_input = f"Description: {description}"

    if image_base64:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_input},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        })
    else:
        messages.append({
            "role": "user",
            "content": user_input
        })

    # Get suggestions from Groq
    response = client.chat.completions.create(
        messages=messages,
        model="llama-3.2-11b-vision-preview",
        max_tokens=1000,
        temperature=0.7
    )

    # Parse the response into structured format
    try:
        suggestions = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        suggestions = {
            "high_priority": ["Error parsing AI response"],
            "medium_priority": [],
            "low_priority": [],
            "rationale": "Please try again with more specific input"
        }

    return suggestions


def main():
    st.title("AI UX Improvement Suggestions Generator")

    # Sidebar for input options
    st.sidebar.header("Input Options")
    input_type = st.sidebar.radio(
        "Choose input type:",
        ["Upload Screenshot", "Describe Interface"]
    )

    # Main content area
    if input_type == "Upload Screenshot":
        uploaded_file = st.file_uploader("Upload a screenshot of your interface", type=["jpg", "png"])
        image_base64 = encode_image(uploaded_file) if uploaded_file else None
    else:
        st.write("Describe your interface design:")
        description = st.text_area("", height=150)
        image_base64 = None

    # Common inputs
    concerns = st.text_area("Specific concerns or issues (optional):", height=100)

    if st.button("Generate Suggestions"):
        with st.spinner("Analyzing interface..."):
            suggestions = get_ux_suggestions(
                image_base64=image_base64,
                description=description if input_type == "Describe Interface" else "",
                concerns=concerns
            )

            # Display suggestions
            st.header("UX Improvement Suggestions")

            # High priority suggestions
            st.subheader("🔴 High Priority")
            for suggestion in suggestions["high_priority"]:
                st.markdown(f"- {suggestion}")

            # Medium priority suggestions
            st.subheader("🟡 Medium Priority")
            for suggestion in suggestions["medium_priority"]:
                st.markdown(f"- {suggestion}")

            # Low priority suggestions
            st.subheader("🟢 Low Priority")
            for suggestion in suggestions["low_priority"]:
                st.markdown(f"- {suggestion}")

            # Rationale
            st.subheader("💡 Rationale")
            st.write(suggestions["rationale"])


if __name__ == "__main__":
    main()