# Email Alert System

A complete Python-based email notification system with a modern web interface. Send individual or bulk email alerts, manage subscribers, and track email delivery status.

## Features

✅ **Send Individual Alerts** - Send email notifications to single recipients
✅ **Bulk Alerts** - Send alerts to multiple recipients at once
✅ **Schedule Alerts** - Schedule emails to be sent at a specific time
✅ **Subscriber Management** - Add, manage, and track email subscribers
✅ **Alert History** - View complete history of all sent alerts
✅ **System Statistics** - Monitor alerts and subscriber metrics
✅ **Modern Web UI** - Clean, responsive interface built with vanilla HTML/CSS/JavaScript
✅ **REST API** - Full-featured FastAPI backend

## Project Structure

```
email-alert-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Configuration settings
│   │   ├── models.py         # Database models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── database.py       # Database setup
│   │   └── email_service.py  # Email sending logic
│   ├── requirements.txt      # Python dependencies
│   ├── run.py               # Application entry point
│   └── .env.example         # Environment template
└── frontend/
    ├── index.html           # Main UI
    ├── style.css            # Styling
    └── script.js            # Frontend logic
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A Gmail account (or other SMTP service) for sending emails

## Installation

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Email Settings

Copy `.env.example` to `.env` and update with your email credentials:

```bash
cp .env.example .env
```

Edit `.env` file:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Alert System
```

**Note for Gmail Users:**
- Enable 2-Factor Authentication
- Generate an [App Password](https://support.google.com/accounts/answer/185833)
- Use the App Password in `SMTP_PASSWORD`

### 3. Start Backend Server

```bash
python run.py
```

The API will be available at `http://localhost:8000`

Access API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 4. Frontend Setup

Open `frontend/index.html` in your web browser, or serve it with a local server:

```bash
cd frontend
# Using Python 3
python -m http.server 8080

# Or using Node.js http-server
npx http-server
```

Visit `http://localhost:8080` in your browser

## API Endpoints

### Alerts

- `POST /api/alerts/send` - Send a single alert
- `POST /api/alerts/send-bulk` - Send bulk alerts
- `GET /api/alerts` - Get all alerts
- `GET /api/alerts/{alert_id}` - Get specific alert
- `PUT /api/alerts/{alert_id}` - Update alert
- `DELETE /api/alerts/{alert_id}` - Delete alert

### Subscribers

- `POST /api/subscribers` - Add subscriber
- `GET /api/subscribers` - Get all subscribers
- `GET /api/subscribers/{subscriber_id}` - Get specific subscriber
- `PUT /api/subscribers/{subscriber_id}` - Update subscriber
- `DELETE /api/subscribers/{subscriber_id}` - Delete subscriber

### System

- `GET /health` - Health check
- `GET /api/stats` - System statistics

## Usage Examples

### Send Single Alert (API)

```bash
curl -X POST "http://localhost:8000/api/alerts/send" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "user@example.com",
    "subject": "Important Alert",
    "message": "This is an important notification."
  }'
```

### Send Bulk Alerts (API)

```bash
curl -X POST "http://localhost:8000/api/alerts/send-bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_emails": ["user1@example.com", "user2@example.com"],
    "subject": "Bulk Alert",
    "message": "This message goes to multiple recipients."
  }'
```

### Schedule Alert

```bash
curl -X POST "http://localhost:8000/api/alerts/send" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "user@example.com",
    "subject": "Scheduled Alert",
    "message": "This will be sent at the scheduled time.",
    "scheduled_for": "2024-12-25T10:00:00"
  }'
```

## Web Interface Features

### Send Alert Tab
- Send individual email alerts
- Optional scheduling
- Real-time status feedback

### Bulk Send Tab
- Send to multiple recipients
- Paste email list (one per line)
- Bulk scheduling support

### Subscribers Tab
- Add new email subscribers
- View subscriber list
- Toggle active/inactive status
- Delete subscribers

### Alert History Tab
- View all sent alerts
- Filter by status (Sent, Failed, Pending)
- See error messages for failed sends
- Track sent timestamps

### Statistics Tab
- Total alerts sent
- Delivery success rate
- Subscriber metrics
- Visual dashboard

## Database

By default, SQLite is used. The database file (`alerts.db`) is created automatically in the backend directory.

To use PostgreSQL or MySQL instead, update the `DATABASE_URL` in `.env`:

```env
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/email_alerts

# MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost/email_alerts
```

## CORS Configuration

The backend allows requests from:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://localhost:8080`

To add more origins, edit `app/config.py`:

```python
CORS_ORIGINS: list = ["http://localhost:3000", "http://your-domain.com"]
```

## Troubleshooting

### "Connection refused" error
- Make sure backend is running: `python run.py`
- Check if port 8000 is available

### "Failed to send email"
- Verify SMTP credentials in `.env`
- Check if Gmail 2FA and app password are set up correctly
- Ensure firewall allows connections to SMTP port (usually 587)

### API not responding
- Check backend server logs
- Verify `CORS_ORIGINS` includes your frontend URL
- Test API health: `http://localhost:8000/health`

## Development

### Running Tests

```bash
pytest
```

### Database Migrations (if using Alembic)

```bash
alembic upgrade head
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Use a production SMTP service (SendGrid, Mailgun, etc.)
- [ ] Use a production database (PostgreSQL, MySQL)
- [ ] Set strong `SMTP_PASSWORD`
- [ ] Use HTTPS for frontend
- [ ] Restrict `CORS_ORIGINS` to your domain
- [ ] Set up proper logging
- [ ] Use environment variables for all secrets

### Docker

Create a `Dockerfile` in the backend directory:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

Build and run:
```bash
docker build -t email-alert-system .
docker run -p 8000:8000 --env-file .env email-alert-system
```

## Contributing

Feel free to fork, enhance, and submit pull requests!

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues, questions, or suggestions, please open an issue on the project repository.

---

**Version:** 1.0.0  
**Last Updated:** 2024
