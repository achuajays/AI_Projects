# my_docker_generator/ai_utils.py
import os

try:
    from groq import Groq

    groq_client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )

    def groq_query(data, query):
        """Return a list of file objects from data matching the filename in the query."""
        if query.startswith('*[name == "') and query.endswith('"]'):
            target = query[len('*[name == "'): -2]
            return [item for item in data if item.get("name") == target]
        return []

    def ai_generate(prompt):
        """
        Uses the Groq client's chat completion API to generate text based on a prompt.
        """
        try:
            response = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that writes configuration files.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_completion_tokens=1024,
                top_p=1,
                stop=None,
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling AI: {e}")
            return None

except ImportError:
    print("Warning: Groq package not found. Using built-in implementations.")

    def groq_query(data, query):
        """Simple GROQ-like query implementation."""
        if query.startswith('*[name == "') and query.endswith('"]'):
            target = query[len('*[name == "'): -2]
            return [item for item in data if item.get("name") == target]
        return []

    def ai_generate(prompt):
        """Fallback AI generator returning default text."""
        print("Warning: AI generation not available; using default text.")
        if "docker-compose" in prompt:
            return (
                'version: "3.8"\n'
                "services:\n"
                "  app:\n"
                "    build: .\n"
                "    ports:\n"
                "      - \"80:80\"\n"
            )
        elif "dockerreadme" in prompt.lower():
            return (
                "# Docker Project README\n\n"
                "This project uses Docker to containerize the application.\n\n"
                "## Running the Containers\n\n"
                "1. Build the images: `docker-compose build`\n"
                "2. Start the services: `docker-compose up`\n"
                "3. Stop the services: `docker-compose down`\n"
            )
        else:
            return "Generated text."
