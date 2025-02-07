import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Groq API client
client = Groq(api_key=os.getenv("GROQ"))

# ---- Custom Styling ----
st.set_page_config(page_title="AI Email Rewriter", page_icon="📧", layout="centered")
st.markdown("""
    <style>
        .stTextArea textarea { font-size: 16px; }
        .stRadio label { font-size: 16px; }
        .stButton button { background-color: #4CAF50; color: white; font-size: 16px; }
        .copy-btn { 
            background-color: #008CBA; 
            color: white; 
            padding: 8px 12px; 
            border: none; 
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
        }
        .copy-btn:hover { background-color: #007B9E; }
    </style>
""", unsafe_allow_html=True)

# ---- App Title ----
st.title("📧 AI-Powered Email Rewriter")
st.markdown("### 📝 Rewrite your emails in different **tones** and **lengths** effortlessly!")

# ---- User Input ----
st.subheader("✉️ Your Email")
email_text = st.text_area("Paste your email here:", height=200, placeholder="Type or paste your email...")

# ---- Tone Selection ----
st.subheader("🎭 Choose the Tone")
tone_options = {
    "Professional": "Rewrite the following email in a professional and formal tone.",
    "Friendly": "Rewrite the following email in a warm, friendly, and conversational tone.",
    "Concise": "Rewrite the following email to be more concise and to the point.",
    "Apologetic": "Rewrite the following email with an apologetic and respectful tone.",
    "Persuasive": "Rewrite the following email to be more persuasive and compelling.",
    "Empathetic": "Rewrite the following email in an empathetic and understanding tone."
}
tone = st.radio("", list(tone_options.keys()), horizontal=True)

# ---- Length Adjustment ----
st.subheader("📏 Adjust Length")
length_options = {
    "Default": "",
    "Shorter": "Make it shorter while keeping the key points.",
    "Longer": "Expand the email with more details and elaboration."
}
length = st.radio("", list(length_options.keys()), horizontal=True)

# ---- Process Email Button ----
if st.button("🔄 Rewrite Email", use_container_width=True):
    if not email_text.strip():
        st.warning("⚠️ Please enter an email before rewriting.")
    else:
        with st.spinner("✨ Rewriting your email..."):
            # Prepare AI prompt
            prompt = f"{tone_options[tone]} {length_options[length]}\n\n{email_text}"

            # Call Groq API for email rewriting
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an advanced AI assistant that rewrites emails."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_completion_tokens=512
            )

            # Display the rewritten email
            rewritten_email = chat_completion.choices[0].message.content
            st.subheader("📬 Rewritten Email:")
            rewritten_box = st.text_area("Here's your improved email:", rewritten_email, height=200)

            # Copy Button (New Feature!)
            st.write("✅ Click below to copy the rewritten email:")
            st.code(rewritten_email, language="plaintext")  # Displays the text in a copyable box

            if st.button("📋 Copy to Clipboard"):
                st.session_state.copied_text = rewritten_email
                st.success("✅ Email copied successfully!")

# ---- Footer ----
st.markdown("---")
st.markdown("<p style='text-align:center;'>Built with ❤️ using <a href='https://streamlit.io/' target='_blank'>Streamlit</a> and <a href='https://groq.com/' target='_blank'>Groq API</a>.</p>", unsafe_allow_html=True)
