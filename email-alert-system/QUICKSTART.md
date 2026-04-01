# Email Alert System - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
cd ..
```

### Step 2: Configure Email Settings
```bash
# Copy example config
cp backend/.env.example backend/.env

# Edit the .env file with your email credentials
# For Gmail: use App Password (not your regular password)
```

**Gmail Setup:**
1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Copy the 16-character password to `SMTP_PASSWORD` in `.env`

### Step 3: Start Backend
```bash
cd backend
python run.py
```

Backend will be available at: http://localhost:8000

### Step 4: Open Frontend
Open `frontend/index.html` in your browser or use:
```bash
cd frontend
python -m http.server 8080
```

Then visit: http://localhost:8080

## 📖 Documentation

- **Full README:** See `README.md`
- **API Docs:** http://localhost:8000/docs (Swagger)
- **API Docs:** http://localhost:8000/redoc (ReDoc)

## 🎯 Quick Usage

### Send Alert via Web UI
1. Go to "Send Alert" tab
2. Enter recipient email
3. Write subject and message
4. Click "Send Alert"

### Send Bulk Alert via Web UI
1. Go to "Bulk Send" tab
2. Paste email list (one per line)
3. Write subject and message
4. Click "Send Bulk Alerts"

### Add Subscriber
1. Go to "Subscribers" tab
2. Enter email address
3. Click "Add Subscriber"

### View Alert History
1. Go to "Alert History" tab
2. Filter by status if needed
3. See delivery status and sent time

### Check Statistics
1. Go to "Statistics" tab
2. View overall metrics

## 🔧 Troubleshooting

### Backend won't start
```
Error: Address already in use port 8000
→ Solution: Change port in `backend/run.py` or kill existing process on port 8000
```

### Emails not sending
```
Error: SMTP authentication failed
→ Solution: Check .env file credentials, verify Gmail app password
```

### CORS errors
```
Error: Access to XMLHttpRequest blocked by CORS policy
→ Solution: Ensure backend is running on http://localhost:8000
```

### Database errors
```
Error: sqlite3.OperationalError: database is locked
→ Solution: Delete `alerts.db` and restart backend
```

## 📁 Project Structure

```
email-alert-system/
├── backend/           # Python FastAPI backend
├── frontend/          # HTML/CSS/JavaScript UI
├── README.md          # Full documentation
├── docker-compose.yml # Docker setup (optional)
└── setup.py          # One-click setup script
```

## 🌐 API Examples

### Send Single Alert
```bash
curl -X POST "http://localhost:8000/api/alerts/send" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "user@example.com",
    "subject": "Hello",
    "message": "Test message"
  }'
```

### List All Alerts
```bash
curl "http://localhost:8000/api/alerts?limit=10"
```

### Get System Stats
```bash
curl "http://localhost:8000/api/stats"
```

## 🎨 Features

✅ Send individual email alerts
✅ Send bulk emails to multiple recipients
✅ Schedule emails for future delivery
✅ Manage email subscribers
✅ View complete alert history
✅ Track delivery status (Sent, Failed, Pending)
✅ System statistics dashboard
✅ Responsive web interface
✅ RESTful API with documentation
✅ SQLite database (easily swap for PostgreSQL/MySQL)

## 🚢 Deployment

### Docker
```bash
docker-compose up -d
```

### Python (Production)
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

## ❓ Need Help?

- Check `README.md` for full documentation
- Check `backend/.env.example` for all config options
- Review API docs at http://localhost:8000/docs
- Check browser console for frontend errors

## 💡 Next Steps

1. **Customize Emails:** Modify `app/email_service.py` for HTML emails
2. **Add Authentication:** Add JWT tokens to protect API endpoints
3. **Setup Cron Job:** Schedule periodic alert checking
4. **Database Migration:** Switch to PostgreSQL for production
5. **Email Templates:** Create reusable email templates

---

**Happy sending! 📧**
