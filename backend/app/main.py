from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List
import os

from .config import settings
from .database import get_db, init_db
from .models import Alert, Subscriber, AlertStatus as AlertStatusEnum
from .schemas import (
    AlertCreate, AlertResponse, AlertUpdate,
    SubscriberCreate, SubscriberResponse, SubscriberUpdate,
    BulkAlertCreate
)
from .email_service import EmailService

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler()

async def send_scheduled_alerts_job():
    from .database import SessionLocal
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    pending_alerts = db.query(Alert).filter(
        Alert.status == AlertStatusEnum.PENDING,
        Alert.scheduled_for <= now
    ).all()
    
    for alert in pending_alerts:
        success, error_msg = await EmailService.send_email(
            alert.recipient_email, alert.subject, alert.message
        )
        if success:
            alert.status = AlertStatusEnum.SENT
            alert.sent_at = datetime.now(timezone.utc)
        else:
            alert.status = AlertStatusEnum.FAILED
            alert.error_message = error_msg
        db.commit()
    db.close()

@app.on_event("startup")
async def startup_event():
    scheduler.add_job(send_scheduled_alerts_job, 'interval', minutes=1)
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

async def process_alert(alert_id: int, email: str, subject: str, message: str):
    from .database import SessionLocal
    db = SessionLocal()
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        try:
            success, error_msg = await EmailService.send_email(email, subject, message)
            if success:
                alert.status = AlertStatusEnum.SENT
                alert.sent_at = datetime.now(timezone.utc)
            else:
                alert.status = AlertStatusEnum.FAILED
                alert.error_message = error_msg
            db.commit()
        except Exception as e:
            alert.status = AlertStatusEnum.FAILED
            alert.error_message = str(e)
            db.commit()
    db.close()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= Health Check =============
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Email Alert System"}

# ============= Alert Endpoints =============

@app.post("/api/alerts/send", response_model=AlertResponse)
async def send_alert(
    alert: AlertCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send a single email alert"""
    
    # Create alert record
    db_alert = Alert(
        recipient_email=alert.recipient_email,
        subject=alert.subject,
        message=alert.message,
        scheduled_for=alert.scheduled_for
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    # Send email in background if not scheduled
    if not alert.scheduled_for or alert.scheduled_for <= datetime.now(timezone.utc):
        background_tasks.add_task(
            process_alert,
            db_alert.id,
            alert.recipient_email,
            alert.subject,
            alert.message
        )
    
    return db_alert

@app.post("/api/alerts/send-bulk", response_model=dict)
async def send_bulk_alerts(
    bulk_alert: BulkAlertCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send alerts to multiple recipients"""
    
    results = {
        "total": len(bulk_alert.recipient_emails),
        "sent": 0, # Queued
        "failed": 0,
        "scheduled": 0
    }
    
    for email in bulk_alert.recipient_emails:
        db_alert = Alert(
            recipient_email=email,
            subject=bulk_alert.subject,
            message=bulk_alert.message,
            scheduled_for=bulk_alert.scheduled_for
        )
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        
        # Send if not scheduled
        if not bulk_alert.scheduled_for or bulk_alert.scheduled_for <= datetime.now(timezone.utc):
            background_tasks.add_task(
                process_alert,
                db_alert.id,
                email,
                bulk_alert.subject,
                bulk_alert.message
            )
            results["sent"] += 1
        else:
            results["scheduled"] += 1
    
    return results

@app.get("/api/alerts", response_model=List[AlertResponse])
async def get_alerts(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get all alerts with optional filtering"""
    query = db.query(Alert)
    
    if status:
        query = query.filter(Alert.status == status)
    
    alerts = query.offset(skip).limit(limit).all()
    return alerts

@app.get("/api/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert

@app.put("/api/alerts/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db)
):
    """Update an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    
    if alert_update.subject:
        alert.subject = alert_update.subject
    if alert_update.message:
        alert.message = alert_update.message
    if alert_update.status:
        alert.status = alert_update.status
    
    db.commit()
    db.refresh(alert)
    return alert

@app.delete("/api/alerts/{alert_id}")
async def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    return {"message": "Alert deleted successfully"}

# ============= Subscriber Endpoints =============

@app.post("/api/subscribers", response_model=SubscriberResponse)
async def create_subscriber(
    subscriber: SubscriberCreate,
    db: Session = Depends(get_db)
):
    """Create a new subscriber"""
    # Check if subscriber already exists
    existing = db.query(Subscriber).filter(
        Subscriber.email == subscriber.email
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already subscribed"
        )
    
    db_subscriber = Subscriber(email=subscriber.email)
    db.add(db_subscriber)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber

@app.get("/api/subscribers", response_model=List[SubscriberResponse])
async def get_subscribers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all subscribers"""
    subscribers = db.query(Subscriber).offset(skip).limit(limit).all()
    return subscribers

@app.get("/api/subscribers/{subscriber_id}", response_model=SubscriberResponse)
async def get_subscriber(subscriber_id: int, db: Session = Depends(get_db)):
    """Get a specific subscriber"""
    subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscriber not found"
        )
    return subscriber

@app.put("/api/subscribers/{subscriber_id}", response_model=SubscriberResponse)
async def update_subscriber(
    subscriber_id: int,
    subscriber_update: SubscriberUpdate,
    db: Session = Depends(get_db)
):
    """Update a subscriber"""
    subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscriber not found"
        )
    
    if subscriber_update.is_active is not None:
        subscriber.is_active = subscriber_update.is_active
    
    db.commit()
    db.refresh(subscriber)
    return subscriber

@app.delete("/api/subscribers/{subscriber_id}")
async def delete_subscriber(subscriber_id: int, db: Session = Depends(get_db)):
    """Delete a subscriber"""
    subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscriber not found"
        )
    
    db.delete(subscriber)
    db.commit()
    return {"message": "Subscriber deleted successfully"}

# ============= Stats Endpoints =============

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    total_alerts = db.query(Alert).count()
    sent_alerts = db.query(Alert).filter(Alert.status == AlertStatusEnum.SENT).count()
    failed_alerts = db.query(Alert).filter(Alert.status == AlertStatusEnum.FAILED).count()
    pending_alerts = db.query(Alert).filter(Alert.status == AlertStatusEnum.PENDING).count()
    total_subscribers = db.query(Subscriber).count()
    active_subscribers = db.query(Subscriber).filter(Subscriber.is_active == True).count()
    
    return {
        "alerts": {
            "total": total_alerts,
            "sent": sent_alerts,
            "failed": failed_alerts,
            "pending": pending_alerts
        },
        "subscribers": {
            "total": total_subscribers,
            "active": active_subscribers
        }
    }

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Récupère le chemin absolu du dossier parent du fichier actuel
base_path = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(base_path, "../../frontend")

# Monter le dossier frontend (ce dossier devra être copié à côté de l'app ou lié proprement)
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def serve_frontend():
    index_path = os.path.join(frontend_path, "index.html")
    return FileResponse(index_path)
