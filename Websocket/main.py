# websocket_server.py
import asyncio
import websockets
import json

clients = set()

async def handler(websocket, path):
    clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            print(data)
            for client in clients:
                if client != websocket:
                    await client.send(json.dumps(data))
    finally:
        clients.remove(websocket)

start_server = websockets.serve(handler, "0.0.0.0", 8000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()