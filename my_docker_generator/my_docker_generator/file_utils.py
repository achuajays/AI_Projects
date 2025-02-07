# my_docker_generator/file_utils.py
import os

def build_file_list(directory):
    """
    Walks through the given directory and builds a list of file objects.
    Each file is represented as a dict with keys 'name' and 'path' (relative to the directory).
    """
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), directory)
            file_list.append({"name": file, "path": rel_path})
    return file_list

def generate_docker_ignore(project_dir, file_list, groq_query):
    """
    Generates a .dockerignore file using common directory patterns.
    """
    ignore_entries = [".git", "__pycache__"]

    # If a package.json exists, ignore node_modules.
    if groq_query(file_list, '*[name == "package.json"]'):
        ignore_entries.append("node_modules")

    # Ignore build directories if present.
    if any("build" in f.get("path", "").split(os.sep) for f in file_list):
        ignore_entries.append("build")

    # For Python projects, ignore virtual environment directories.
    if groq_query(file_list, '*[name == "requirements.txt"]'):
        ignore_entries.extend(["venv", ".venv"])

    dockerignore_content = "\n".join(ignore_entries) + "\n"
    output_path = os.path.join(project_dir, ".dockerignore")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(dockerignore_content)
    print(f".dockerignore generated at: {output_path}")
