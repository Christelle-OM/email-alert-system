import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails"""
    
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        message: str,
        html: bool = False
    ) -> tuple[bool, str]:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            message: Email body
            html: If True, treat message as HTML
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Create email message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            msg["To"] = to_email
            
            # Add message body
            if html:
                msg.attach(MIMEText(message, "html"))
            else:
                msg.attach(MIMEText(message, "plain"))
            
            # Send email
            async with aiosmtplib.SMTP(
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT
            ) as smtp:
                await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                await smtp.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True, "Email sent successfully"
            
        except Exception as e:
            error_msg = f"Failed to send email to {to_email}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    async def send_batch_emails(
        to_emails: list[str],
        subject: str,
        message: str,
        html: bool = False
    ) -> dict:
        """
        Send emails to multiple recipients
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            message: Email body
            html: If True, treat message as HTML
            
        Returns:
            Dictionary with success/failed counts
        """
        results = {
            "total": len(to_emails),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for email in to_emails:
            success, msg = await EmailService.send_email(email, subject, message, html)
            if success:
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({"email": email, "error": msg})
        
        return results
