from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import requests
from dotenv import load_dotenv
import os
from typing import Optional

# Load environment variables
load_dotenv()

app = FastAPI()

# In-memory storage for the content
content_store = []


async def make_bolna_call():
    """Make a call to the Bolna API"""
    url = "https://api.bolna.dev/call"

    payload = {
        "agent_id": os.getenv("agent_id"),
        "recipient_phone_number":os.getenv("recipient_phone_number"),
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('Authorization')}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API call failed: {str(e)}")


@app.post("/make-call")
async def initiate_call(request: Request):
    """Endpoint to initiate a call"""
    try:


        result = await make_bolna_call()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming webhook data"""
    try:
        data = await request.json()

        # Process extracted data if available
        if "extracted_data" in data:
            print("*" * 100)
            print(data["extracted_data"])
            print("*" * 100)
            # Store the content
            content_store.append(data["extracted_data"])



        return {"status": "success", "message": "Webhook received"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")


@app.get("/display", response_class=HTMLResponse)
async def display_content():
    """Display stored content in HTML format"""
    html_content = """
    <html>
        <head>
            <title>Received Content</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .content-item { margin: 10px 0; padding: 10px; border: 1px solid #ccc; }
            </style>
        </head>
        <body>
            <h1>Received Content</h1>
            <div>
    """

    for item in content_store:
        html_content += f'<div class="content-item"><pre>{str(item)}</pre></div>'

    html_content += """
            </div>
        </body>
    </html>
    """

    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)