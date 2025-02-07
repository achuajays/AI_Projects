# Setting Up a Custom Agent in Bolna.dev And Extract Data From Call 

This guide will help you set up a custom agent in [Bolna.dev](https://www.bolna.dev/), configure environment variables, run the Docker container, and push execution data to a webhook.

## Prerequisites
- A [Bolna.dev](https://www.bolna.dev/) account
- Docker installed on your machine
- A `.env` file with required environment variables

## Step 1: Create a Custom Agent in Bolna.dev
1. Go to [Bolna.dev](https://www.bolna.dev/)
2. Navigate to **Agents** and create a new agent.
3. Configure your agent's settings as needed.

## Step 2: Create a `.env` File
Create a `.env` file in your project directory and add the following:

```
Authorization=your_api_key_here
recipient_phone_number=phone number
agent_id=agent_id
```

## Step 3: Build and Run the Docker Container
Run the following commands:

```sh
docker build --tag bolna:latest .
docker run -d -p 8000:8000 bolna
```

## Step 4: Configure Webhook in Bolna.dev
1. In Bolna.dev, go to **Agent > Analytics**.
2. Find **Push all execution data to webhook**.
3. Add your hosted link followed by `/webhook` (e.g., `https://your-hosted-link/webhook`).

Your custom agent is now set up and ready to receive execution data from Bolna.dev! 🚀
