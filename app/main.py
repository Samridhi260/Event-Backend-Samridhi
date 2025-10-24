""" from fastapi import FastAPI, Depends
from pydantic import BaseModel
from datetime import datetime
from app.db import db
from app.auth import get_current_user
from app.analytics import router as analytics_router
app.include_router(analytics_router)


app = FastAPI()

class EventIn(BaseModel):
    title: str
    description: str | None = None

@app.post("/events/")
async def create_event(event: EventIn, user=Depends(get_current_user)):
    uid = user["uid"]
    data = {
        "title": event.title,
        "description": event.description,
        "user_id": uid,
        "created_at": datetime.utcnow().isoformat()
    }
    _, doc = db.collection("events").add(data)
    return {"id": doc.id, "data": data}

@app.get("/events/")
async def list_events(user=Depends(get_current_user)):
    uid = user["uid"]
    docs = db.collection("events").where("user_id", "==", uid).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]
 """


# app/main.py
from fastapi import FastAPI, Depends, WebSocket
from pydantic import BaseModel
from datetime import datetime, timezone
from app.db import db
from app.analytics import router as analytics_router
from app.auth import get_current_user
from app.analytics import router as analytics_router
from app.ws import manager

# 1) Define the FastAPI app FIRST
app = FastAPI(title="Event API", version="1.0.0")
app.include_router(analytics_router)


# 2) Then include routers
app.include_router(analytics_router)

# 3) Models
class EventIn(BaseModel):
    title: str
    description: str | None = None

# 4) Endpoints
@app.post("/events/")
async def create_event(event: EventIn, user=Depends(get_current_user)):
    uid = user["uid"]
    data = {
        "title": event.title,
        "description": event.description,
        "user_id": uid,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    # You can keep .add(data) if you prefer; both are fine.
    _, doc = db.collection("events").add(data)

    # Broadcast to any connected WebSocket clients
    await manager.broadcast({
        "type": "event_created",
        "id": doc.id,
        **data
    })

    return {"id": doc.id, "data": data}


@app.get("/events/")
async def list_events(user=Depends(get_current_user)):
    uid = user["uid"]
    docs = db.collection("events").where("user_id", "==", uid).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]


# Simple WebSocket endpoint (no auth for PoC)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # keep alive; we don't use inbound messages for this PoC
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        manager.disconnect(websocket)

