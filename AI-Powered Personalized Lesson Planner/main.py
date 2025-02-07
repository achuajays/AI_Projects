import streamlit as st
import json
from datetime import datetime, timedelta
import groq
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Setup page configuration
st.set_page_config(
    page_title="AI-Powered Lesson Planner",
    page_icon="📚",
    layout="wide"
)

# Application styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'lesson_plans' not in st.session_state:
    st.session_state.lesson_plans = []
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

# Initialize Groq client
groq_api_key = os.getenv("GROQ")
if not groq_api_key:
    st.error("Please set the GROQ API key in your .env file as GROQ=your-api-key")
    st.stop()

client = groq.Client(api_key=groq_api_key)


def generate_lesson_plan_prompt(subject: str, grade_level: str, duration: str,
                                learning_style: List[str], objectives: str) -> str:
    """Generate a prompt for the Groq API"""
    example_plan = {
        "subject": subject,
        "grade_level": grade_level,
        "duration": duration,
        "learning_style": learning_style,
        "objectives": objectives,
        "sections": [
            {
                "title": "Introduction",
                "duration": "10 minutes",
                "activities": [
                    "Hook activity related to real-world applications",
                    "Review of prerequisites",
                    "Setting lesson objectives"
                ]
            },
            {
                "title": "Main Content",
                "duration": "20 minutes",
                "activities": [
                    "Direct instruction with visual aids",
                    "Guided practice with examples",
                    "Interactive demonstration"
                ]
            },
            {
                "title": "Practice",
                "duration": "15 minutes",
                "activities": [
                    "Individual problem-solving",
                    "Group work activities",
                    "Hands-on application"
                ]
            },
            {
                "title": "Assessment & Closure",
                "duration": "15 minutes",
                "activities": [
                    "Exit ticket assessment",
                    "Summary discussion",
                    "Preview of next lesson"
                ]
            }
        ],
        "resources": [
            "Digital presentation",
            "Worksheets",
            "Manipulatives",
            "Assessment materials",
            "Reference guides"
        ],
        "differentiation": {
            "visual_learners": "Use diagrams and visual aids",
            "auditory_learners": "Include discussions and verbal explanations",
            "kinesthetic_learners": "Incorporate hands-on activities"
        }
    }

    return f"""Create a detailed lesson plan using this exact JSON structure:

{json.dumps(example_plan, indent=2)}

Requirements:
1. Follow the exact JSON structure shown above
2. Each section should have 3-5 specific activities
3. Include at least 5 relevant resources
4. Provide detailed differentiation strategies
5. Ensure all content is appropriate for {grade_level} level
6. Focus on meeting these objectives: {objectives}
7. Incorporate these learning styles: {', '.join(learning_style)}

Return only the JSON object, no additional text or explanations."""


def extract_json_from_response(text: str) -> Dict:
    """Extract and validate JSON from the response text"""
    try:
        # First try direct JSON parsing
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            # Try to extract JSON if there's additional text
            start_idx = text.find('{')
            end_idx = text.rindex('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
        except Exception:
            st.error("Failed to parse response as JSON. Raw response:")
            st.code(text)
            return None


def validate_lesson_plan(plan: Dict) -> bool:
    """Validate the lesson plan structure and content"""
    required_fields = ["subject", "grade_level", "duration", "sections", "resources", "differentiation"]
    if not all(field in plan for field in required_fields):
        return False

    if not isinstance(plan["sections"], list) or len(plan["sections"]) < 3:
        return False

    if not isinstance(plan["resources"], list) or len(plan["resources"]) < 3:
        return False

    return True


def generate_lesson_plan(subject: str, grade_level: str, duration: str,
                         learning_style: List[str], objectives: str) -> Dict:
    """Generate a lesson plan using Groq API"""
    prompt = generate_lesson_plan_prompt(
        subject, grade_level, duration, learning_style, objectives
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system",
                 "content": "You are an expert educator who creates lesson plans. Always respond with valid JSON only, no additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=4000,
            top_p=1,
            stream=False
        )

        response_text = completion.choices[0].message.content

        if st.session_state.debug_mode:
            st.subheader("Debug: Raw API Response")
            st.code(response_text)

        lesson_plan = extract_json_from_response(response_text)

        if lesson_plan and validate_lesson_plan(lesson_plan):
            return lesson_plan
        else:
            st.error("Generated lesson plan is invalid or missing required fields")
            return None

    except Exception as e:
        st.error(f"Error generating lesson plan: {str(e)}")
        return None


# Sidebar for input parameters
st.sidebar.title("Lesson Parameters")

# Debug mode toggle
st.sidebar.checkbox("Debug Mode", key="debug_mode")

subject = st.sidebar.text_input("Subject", placeholder="e.g., Mathematics")
grade_level = st.sidebar.selectbox("Grade Level",
                                   ["Elementary (K-5)", "Middle School (6-8)", "High School (9-12)"])
duration = st.sidebar.selectbox("Lesson Duration",
                                ["30 minutes", "45 minutes", "60 minutes", "90 minutes"])
learning_style = st.sidebar.multiselect("Learning Styles",
                                        ["Visual", "Auditory", "Kinesthetic", "Reading/Writing"],
                                        default=["Visual"])
objectives = st.sidebar.text_area("Learning Objectives",
                                  placeholder="Enter the main objectives for this lesson...")

# Main content area
st.title("📚 AI-Powered Lesson Planner")
st.caption("Powered by Groq AI")

if st.sidebar.button("Generate Lesson Plan"):
    if not subject or not objectives:
        st.error("Please fill in both Subject and Learning Objectives fields.")
    else:
        with st.spinner("Generating your personalized lesson plan using Groq AI..."):
            lesson_plan = generate_lesson_plan(
                subject, grade_level, duration, learning_style, objectives
            )
            if lesson_plan:
                st.session_state.current_plan = lesson_plan
                if lesson_plan not in st.session_state.lesson_plans:
                    st.session_state.lesson_plans.append(lesson_plan)

# Display current lesson plan
if st.session_state.current_plan:
    plan = st.session_state.current_plan

    # Lesson overview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("📘 Subject")
        st.write(plan["subject"])
    with col2:
        st.subheader("👥 Grade Level")
        st.write(plan["grade_level"])
    with col3:
        st.subheader("⏱️ Duration")
        st.write(plan["duration"])

    st.subheader("🎯 Learning Objectives")
    st.write(plan["objectives"])

    # Lesson sections
    st.subheader("📝 Lesson Structure")
    for section in plan["sections"]:
        with st.expander(f"{section['title']} ({section['duration']})"):
            for activity in section["activities"]:
                st.write(f"- {activity}")

    # Resources and differentiation
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📚 Resources")
        for resource in plan["resources"]:
            st.write(f"- {resource}")

    with col2:
        st.subheader("🔄 Differentiation Strategies")
        for learner_type, strategy in plan["differentiation"].items():
            st.write(f"- **{learner_type}:** {strategy}")

    # Export options
    if st.button("Export Lesson Plan"):
        json_str = json.dumps(plan, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f"lesson_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# History of generated plans
if st.session_state.lesson_plans:
    st.sidebar.subheader("Previously Generated Plans")
    for i, plan in enumerate(st.session_state.lesson_plans):
        if st.sidebar.button(f"Plan {i + 1}: {plan['subject']}", key=f"history_{i}"):
            st.session_state.current_plan = plan