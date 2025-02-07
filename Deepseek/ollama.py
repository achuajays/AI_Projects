from openai import OpenAI

client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',  # Required but ignored
)

# Example chat completion
chat_completion = client.chat.completions.create(
    messages=[
        {'role': 'user', 'content': 'Say this is a test'},
    ],
    model='deepseek-r1:1.5b',
)

print(chat_completion)
# Example text completion
completion = client.completions.create(
    model="deepseek-r1:7b",
    prompt="Say this is a test",
)


print(completion)
# Example list models
list_completion = client.models.list()
print(list_completion)
# Example get model info
model = client.models.retrieve("deepseek-r1:1.5b")
print(model)