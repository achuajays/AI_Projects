# my_docker_generator/framework_detector.py
from my_docker_generator.ai_utils import groq_query


def detect_project_framework(file_list):
    """
    Uses GROQ queries on the file list to determine the project framework.

    Detection rules:
      - If "angular.json" exists, assume Angular.
      - If "streamlit_app.py" exists, assume Streamlit.
      - If "pom.xml" exists, assume Java.
      - If "Gemfile" exists, assume Ruby.
      - If "CMakeLists.txt" exists, assume C++.
      - If "requirements.txt" exists, it's a Python project.
      - If "package.json" exists, it's a React project.
      - If both Python and React indicators exist, treat as a fullstack project.

    Returns one of: "python", "react", "streamlit", "angular", "java", "ruby", "cpp", "fullstack", or "unknown".
    """
    # Check for Angular.
    if groq_query(file_list, '*[name == "angular.json"]'):
        return "angular"

    # Check for Streamlit.
    if groq_query(file_list, '*[name == "streamlit_app.py"]'):
        return "streamlit"

    # Check for Java.
    if groq_query(file_list, '*[name == "pom.xml"]'):
        return "java"

    # Check for Ruby.
    if groq_query(file_list, '*[name == "Gemfile"]'):
        return "ruby"

    # Check for C++ (using CMake).
    if groq_query(file_list, '*[name == "CMakeLists.txt"]'):
        return "cpp"

    # Check for Python and React.
    python_files = groq_query(file_list, '*[name == "requirements.txt"]')
    react_files = groq_query(file_list, '*[name == "package.json"]')

    if python_files and react_files:
        return "fullstack"
    elif python_files:
        return "python"
    elif react_files:
        return "react"
    else:
        return "unknown"
