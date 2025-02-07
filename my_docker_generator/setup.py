# setup.py
from setuptools import setup, find_packages

setup(
    name="my_docker_generator",
    version="0.1.0",
    description="A tool to generate Dockerfiles, docker-compose.yml, and other configuration files based on project structure using AI assistance.",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "groq",
        # List your package dependencies here.
        # For example, if you use the Groq package:
        # "groq>=<version>",
    ],
    entry_points={
        "console_scripts": [
            "docker-gen=my_docker_generator.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)