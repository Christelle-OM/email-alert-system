from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

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
    
    # Send email if not scheduled
    if not alert.scheduled_for or alert.scheduled_for <= datetime.utcnow():
        success, error_msg = await EmailService.send_email(
            alert.recipient_email,
            alert.subject,
            alert.message
        )
        
        if success:
            db_alert.status = AlertStatusEnum.SENT
            db_alert.sent_at = datetime.utcnow()
        else:
            db_alert.status = AlertStatusEnum.FAILED
            db_alert.error_message = error_msg
        
        db.commit()
        db.refresh(db_alert)
    
    return db_alert

@app.post("/api/alerts/send-bulk", response_model=dict)
async def send_bulk_alerts(
    bulk_alert: BulkAlertCreate,
    db: Session = Depends(get_db)
):
    """Send alerts to multiple recipients"""
    
    results = {
        "total": len(bulk_alert.recipient_emails),
        "sent": 0,
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
        if not bulk_alert.scheduled_for or bulk_alert.scheduled_for <= datetime.utcnow():
            success, error_msg = await EmailService.send_email(
                email,
                bulk_alert.subject,
                bulk_alert.message
            )
            
            if success:
                db_alert.status = AlertStatusEnum.SENT
                db_alert.sent_at = datetime.utcnow()
                results["sent"] += 1
            else:
                db_alert.status = AlertStatusEnum.FAILED
                db_alert.error_message = error_msg
                results["failed"] += 1
            
            db.commit()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
