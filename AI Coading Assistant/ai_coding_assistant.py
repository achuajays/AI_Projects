import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
# Initialize the Groq client using your environment variable.
# Make sure you have set the GROQ environment variable appropriately.
client = Groq(api_key = os.getenv("GROQ"))


def analyze_code(code: str, analysis_type: str) -> str:
    """
    Analyze the provided code using the Groq LLM.

    Parameters:
        code (str): The code snippet to analyze.
        analysis_type (str): Type of analysis ("bug_finder" or "pep8_checker").

    Returns:
        str: The response from the LLM.
    """
    if analysis_type == "bug_finder":
        prompt = (
                "Analyze the following code snippet for bugs, spelling mistakes, "
                "and provide suggestions to optimize and improve the code:\n\n" + code
        )
    elif analysis_type == "pep8_checker":
        prompt = (
                "Analyze the following Python code for compliance with PEP8 guidelines. "
                "Identify any violations and suggest improvements:\n\n" + code
        )
    else:
        prompt = "Analyze the following code:\n\n" + code

    # Prepare the message payload for the Groq API.
    messages = [
        {"role": "system", "content": "you are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_completion_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error calling Groq API: {e}"


def bug_finder_page():
    st.title("Code Bug Finder & Optimizer")
    st.write("Enter your code snippet below to detect bugs, spelling errors, and receive optimization suggestions.")

    code_input = st.text_area("Enter your code here", height=300)

    if st.button("Analyze Code"):
        if not code_input.strip():
            st.error("Please enter some code before analyzing.")
        else:
            with st.spinner("Analyzing code..."):
                result = analyze_code(code_input, analysis_type="bug_finder")
            st.subheader("Analysis Result")
            st.code(result, language="python")


def pep8_checker_page():
    st.title("PEP8 Guidelines Checker")
    st.write("Enter your Python code below to check for PEP8 compliance and receive improvement suggestions.")

    code_input = st.text_area("Enter your Python code here", height=300)

    if st.button("Check PEP8 Guidelines"):
        if not code_input.strip():
            st.error("Please enter some code before checking.")
        else:
            with st.spinner("Checking code..."):
                result = analyze_code(code_input, analysis_type="pep8_checker")
            st.subheader("PEP8 Analysis Result")
            st.code(result, language="python")


def main():
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox(
        "Choose the functionality",
        ("Code Bug Finder & Optimizer", "PEP8 Guidelines Checker")
    )

    if app_mode == "Code Bug Finder & Optimizer":
        bug_finder_page()
    elif app_mode == "PEP8 Guidelines Checker":
        pep8_checker_page()


if __name__ == "__main__":
    main()