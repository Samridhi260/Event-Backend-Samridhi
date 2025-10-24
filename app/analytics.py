# app/analytics.py
from fastapi import APIRouter, Depends
from app.db import db
from app.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/me")
def my_analytics(user=Depends(get_current_user)):
    doc = db.collection("analytics").document(user["uid"]).get()
    if not doc.exists:
        return {"totalEvents": 0}
    data = doc.to_dict() or {}
    return {"totalEvents": data.get("totalEvents", 0)}
