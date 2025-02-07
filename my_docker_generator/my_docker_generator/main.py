# my_docker_generator/main.py
import os
import sys
from my_docker_generator.file_utils import build_file_list, generate_docker_ignore
from my_docker_generator.framework_detector import detect_project_framework
from my_docker_generator.docker_generator import (
    generate_dockerfile,
    generate_docker_compose_ai,
    generate_docker_readme_ai,
)
from my_docker_generator.ai_utils import groq_query  # Import groq_query

def main():
    """
    Usage:
      python -m my_docker_generator.main [project_directory] [python_variant]

    - project_directory: Optional. Defaults to the current directory.
    - python_variant: Optional. For Python projects, specify "flask" or "django" to generate an appropriate Dockerfile.
    """
    project_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    python_variant = sys.argv[2].lower() if len(sys.argv) > 2 else None

    if not os.path.isdir(project_dir):
        print(f"Error: '{project_dir}' is not a valid directory.")
        sys.exit(1)

    # Build the file list.
    file_list = build_file_list(project_dir)

    # Detect the project framework.
    framework = detect_project_framework(file_list)
    print(f"Detected project framework: {framework}")

    # If the detected framework is Python and a variant was provided, override accordingly.
    if framework == "python" and python_variant in ["flask", "django"]:
        print(f"Overriding Python framework to: {python_variant}")
        framework = "python"

    # Generate the Dockerfile.
    dockerfile_content = generate_dockerfile(project_dir, framework, python_variant)

    # Generate the docker-compose.yml using AI (based on the Dockerfile content).
    compose_content = generate_docker_compose_ai(project_dir, dockerfile_content)

    # Generate the .dockerignore file.
    generate_docker_ignore(project_dir, file_list, groq_query)

    # Generate dockerreadme.md using AI (based on the docker-compose.yml content).
    if compose_content:
        generate_docker_readme_ai(project_dir, compose_content)

if __name__ == "__main__":
    main()
