from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from .models import AlertStatus

class AlertCreate(BaseModel):
    """Schema for creating an alert"""
    recipient_email: EmailStr
    subject: str
    message: str
    scheduled_for: Optional[datetime] = None

class AlertUpdate(BaseModel):
    """Schema for updating an alert"""
    subject: Optional[str] = None
    message: Optional[str] = None
    status: Optional[AlertStatus] = None

class AlertResponse(BaseModel):
    """Schema for alert response"""
    id: int
    recipient_email: str
    subject: str
    message: str
    status: AlertStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SubscriberCreate(BaseModel):
    """Schema for creating a subscriber"""
    email: EmailStr

class SubscriberUpdate(BaseModel):
    """Schema for updating a subscriber"""
    is_active: Optional[bool] = None

class SubscriberResponse(BaseModel):
    """Schema for subscriber response"""
    id: int
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BulkAlertCreate(BaseModel):
    """Schema for sending alerts to multiple recipients"""
    recipient_emails: List[EmailStr]
    subject: str
    message: str
    scheduled_for: Optional[datetime] = None
