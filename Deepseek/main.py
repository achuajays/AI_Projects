import streamlit as st
from transformers import pipeline


@st.cache_resource
def load_model():
    # Load the model once and cache it
    return pipeline("text-generation", model="deepseek-ai/deepseek-coder-1.3b-instruct")


# App UI
st.title("🤖 DeepSeek Coder Chat")
st.write("Ask questions to the DeepSeek Coder AI model!")

# User input
user_input = st.text_input("Enter your question:", value="Who are you?")

if st.button("Generate Response"):
    # Format messages in chat format
    messages = [{"role": "user", "content": user_input}]

    # Load cached model
    pipe = load_model()

    # Generate response with loading indicator
    with st.spinner("Generating response..."):
        try:
            response = pipe(messages)

            # Display formatted output
            st.subheader("Response:")
            st.write(response[0]['generated_text'][1]["content"])

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Sidebar with info
with st.sidebar:
    st.markdown("### Model Information")
    st.write("This app uses the deepseek-ai/deepseek-coder-1.3b-instruct model")
    st.markdown("### System Requirements")
    st.write("⚠️ Note: This model requires significant computational resources:")
    st.write("- ~3GB RAM minimum")
    st.write("- ~5GB disk space for model weights")
    st.write("- May take 30-60 seconds to load initially")