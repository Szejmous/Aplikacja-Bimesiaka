from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import os

app = FastAPI()

clients = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients[websocket] = None
    print("Nowy klient podłączony")

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if not clients[websocket]:
                clients[websocket] = message.get("user", "Anonim")
                join_message = json.dumps({"user": "System", "message": f"{clients[websocket]} dołączył do czatu"})
                for client in clients:
                    await client.send_text(join_message)
            else:
                broadcast_message = json.dumps({"user": clients[websocket], "message": message["message"]})
                for client in clients:
                    await client.send_text(broadcast_message)
    except WebSocketDisconnect:
        client_name = clients.get(websocket, "Anonim")
        del clients[websocket]
        leave_message = json.dumps({"user": "System", "message": f"{client_name} opuścił czat"})
        for client in clients:
            await client.send_text(leave_message)
        print(f"Klient {client_name} rozłączony")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Stały port 8000 dla lokalnego testowania