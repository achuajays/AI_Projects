from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

# In-memory storage for the content
content_store = []

@app.post("/webhook")
async def webhook(request: Request):
    # Parse the incoming JSON data
    try:
        data = await request.json()

        try:
            if data["extracted_data"]:
                print("*"*100)
                print(data["extracted_data"])
                print("*"*100)
        except Exception as e:
            print(e)

    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON data")

    # Store the content
    content_store.append(data)

    return {"status": "success", "message": "Webhook received"}

@app.get("/display", response_class=HTMLResponse)
async def display_content():
    # Generate HTML to display the content
    html_content = "<html><body><h1>Received Content</h1><ul>"
    for item in content_store:
        html_content += f"<li>{item}</li>"
    html_content += "</ul></body></html>"

    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)