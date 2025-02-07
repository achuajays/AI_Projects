# my_docker_generator/docker_generator.py
import os
from my_docker_generator.ai_utils import ai_generate
from my_docker_generator.file_utils import generate_docker_ignore


def generate_dockerfile(project_dir, framework, python_variant=None):
    """
    Generates a Dockerfile for the specified framework and writes it to project_dir.
    For Python projects, an optional python_variant (e.g. 'flask' or 'django') adjusts the command.
    Returns the Dockerfile content.
    """
    if framework == "python":
        if python_variant == "flask":
            dockerfile_content = (
                "FROM python:3.9-slim\n\n"
                "WORKDIR /app\n"
                "COPY requirements.txt .\n"
                "RUN pip install --no-cache-dir -r requirements.txt\n"
                "COPY . .\n"
                "EXPOSE 5000\n"
                "ENV FLASK_APP=main.py\n"
                'CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]\n'
            )
        elif python_variant == "django":
            dockerfile_content = (
                "FROM python:3.9-slim\n\n"
                "WORKDIR /app\n"
                "COPY requirements.txt .\n"
                "RUN pip install --no-cache-dir -r requirements.txt\n"
                "COPY . .\n"
                "EXPOSE 8000\n"
                'CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]\n'
            )
        else:
            dockerfile_content = (
                "FROM python:3.9-slim\n\n"
                "WORKDIR /app\n"
                "COPY requirements.txt .\n"
                "RUN pip install --no-cache-dir -r requirements.txt\n"
                "COPY . .\n"
                "EXPOSE 80\n"
                'CMD ["python", "main.py"]\n'
            )
    elif framework == "react":
        dockerfile_content = (
            "# Stage 1: Build the React application.\n"
            "FROM node:14 AS builder\n"
            "WORKDIR /app\n"
            "COPY package*.json ./\n"
            "RUN npm install\n"
            "COPY . .\n"
            "RUN npm run build\n"
            "# Stage 2: Serve the React app using Nginx.\n"
            "FROM nginx:stable-alpine\n"
            "COPY --from=builder /app/build /usr/share/nginx/html\n"
            "EXPOSE 80\n"
            'CMD ["nginx", "-g", "daemon off;"]\n'
        )
    elif framework == "streamlit":
        dockerfile_content = (
            "FROM python:3.9-slim\n\n"
            "WORKDIR /app\n"
            "COPY requirements.txt .\n"
            "RUN pip install --no-cache-dir -r requirements.txt\n"
            "COPY . .\n"
            "EXPOSE 8501\n"
            'CMD ["streamlit", "run", "streamlit_app.py", "--server.enableCORS=false"]\n'
        )
    elif framework == "angular":
        dockerfile_content = (
            "# Stage 1: Build the Angular application.\n"
            "FROM node:14 AS builder\n"
            "WORKDIR /app\n"
            "COPY package*.json ./\n"
            "RUN npm install\n"
            "COPY . .\n"
            "RUN npm run build --prod\n"
            "# Stage 2: Serve the Angular app using Nginx.\n"
            "FROM nginx:alpine\n"
            "COPY --from=builder /app/dist/app /usr/share/nginx/html\n"
            "EXPOSE 80\n"
            'CMD ["nginx", "-g", "daemon off;"]\n'
        )
    elif framework == "java":
        dockerfile_content = (
            "FROM openjdk:11-jre-slim\n\n"
            "WORKDIR /app\n"
            "COPY pom.xml .\n"
            "COPY src ./src\n"
            "RUN apt-get update && apt-get install -y maven && mvn package\n"
            "EXPOSE 8080\n"
            'CMD ["java", "-jar", "target/my-app.jar"]\n'
        )
    elif framework == "ruby":
        dockerfile_content = (
            "FROM ruby:2.7\n\n"
            "WORKDIR /app\n"
            "COPY Gemfile Gemfile.lock ./\n"
            "RUN bundle install\n"
            "COPY . .\n"
            "EXPOSE 4567\n"
            'CMD ["ruby", "app.rb"]\n'
        )
    elif framework == "cpp":
        dockerfile_content = (
            "FROM ubuntu:20.04\n\n"
            "RUN apt-get update && apt-get install -y cmake g++ make\n\n"
            "WORKDIR /app\n"
            "COPY . .\n"
            "RUN cmake . && make\n"
            "EXPOSE 8080\n"
            'CMD ["./myapp"]\n'
        )
    elif framework == "fullstack":
        dockerfile_content = (
            "FROM python:3.9-slim\n\n"
            "WORKDIR /app\n"
            "COPY requirements.txt .\n"
            "RUN pip install --no-cache-dir -r requirements.txt\n"
            "COPY . .\n"
            "EXPOSE 80\n"
            'CMD ["python", "main.py"]\n'
        )
    else:
        print("Project framework could not be identified. No Dockerfile generated.")
        return None

    output_path = os.path.join(project_dir, "Dockerfile")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(dockerfile_content)
    print(f"Dockerfile generated at: {output_path}")
    return dockerfile_content


def generate_docker_compose_ai(project_dir, dockerfile_content):
    """
    Uses an AI call to generate a docker-compose.yml file based on the Dockerfile content.
    """
    prompt = (
        "Generate a docker-compose.yml file for a project whose Dockerfile is as follows:\n\n"
        f"{dockerfile_content}\n\n"
        "The compose file should define a service named 'app' that builds the image from the current directory, "
        "exposes the appropriate port, and uses default settings. "
        "Remember to only generate docker compose content with no extra text."
    )
    ai_response = ai_generate(prompt)
    if ai_response:
        output_path = os.path.join(project_dir, "docker-compose.yml")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ai_response)
        print(f"docker-compose.yml generated at: {output_path}")
        return ai_response
    else:
        print("Failed to generate docker-compose.yml via AI.")
        return None


def generate_docker_readme_ai(project_dir, compose_content):
    """
    Uses an AI call to generate a dockerreadme.md file explaining how to run the containers,
    based on the docker-compose.yml content.
    """
    prompt = (
        "Based on the following docker-compose.yml content:\n\n"
        f"{compose_content}\n\n"
        "Generate a README (dockerreadme.md) that explains how to build and run the containers and how to build a docker image, "
        "including commands for building, starting, and stopping the services."
    )
    ai_response = ai_generate(prompt)
    if ai_response:
        output_path = os.path.join(project_dir, "dockerreadme.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ai_response)
        print(f"dockerreadme.md generated at: {output_path}")
    else:
        print("Failed to generate dockerreadme.md via AI.")
