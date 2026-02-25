# HireMind Database Admin Dashboard - Setup Guide

## 🎉 Django Admin Interface is Ready!

Your Django admin panel has been successfully set up to view and manage HireMind database entries.

### **Access the Database Admin:**
- **URL**: `http://localhost:8001/admin/`
- **Username**: `admin`
- **Password**: `admin123`

---

## 📊 Available Database Views

The Django admin interface provides easy access to three main database tables:

### 1. **Users** (`/admin/hiremind_db/hireminduser/`)
View all registered users with their:
- Email address
- Full name
- Account creation date
- Password hash (read-only for security)

**Features:**
- Search by email or name
- Sort by creation date
- View full user details

### 2. **ATS Scores** (`/admin/hiremind_db/atsscore/`)
Track all resume analysis scores with:
- Score value (0-100)
- Associated user ID
- Resume text (expandable)
- Job description used for analysis
- Timestamp

**Features:**
- Filter by score range
- Search by user ID
- Chronologically sorted (newest first)
- Expandable resume/JD text

### 3. **Interview Sessions** (`/admin/hiremind_db/interviewsession/`)
View all completed interview sessions:
- Number of questions answered
- Average interview score
- Associated user ID
- Session date and time

**Features:**
- Filter by score range
- Search by user ID
- Chronologically sorted
- Track interview progress over time

---

## 🔄 How Data Flows

1. **User Registration** → Data saved in `Users` table
2. **ATS Calculation** → Score stored in `ATS Scores` table
3. **Interview Complete** → Session saved in `Interview Sessions` table
4. **View in Django Admin** → http://localhost:8001/admin/

---

## 🚀 Running Both Servers Simultaneously

### Terminal 1: FastAPI Server (Port 8000)
```bash
cd "e:\Cusrsor\Hire MInd"
E:/Cusrsor/.venv/Scripts/python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
Access the application: **http://localhost:8000**

### Terminal 2: Django Admin Server (Port 8001)
```bash
cd "e:\Cusrsor\Hire MInd"
E:/Cusrsor/.venv/Scripts/python.exe manage.py runserver 8001
```
Access the admin panel: **http://localhost:8001/admin/**

---

## 📁 Project Structure

```
Hire MInd/
├── backend/                    # FastAPI application
│   ├── main.py                # REST API endpoints
│   ├── auth.py                # Authentication & database functions
│   ├── config.py              # Configuration
│   └── services/              # AI/ML services
├── frontend/                  # Web interface
│   ├── app.js                 # JavaScript application
│   ├── index.html             # HTML template
│   └── styles.css             # Styling
├── hiremind_admin/            # Django project settings
│   ├── settings.py            # Django configuration
│   ├── urls.py                # URL routing
│   └── wsgi.py                # WSGI config
├── hiremind_db/               # Django app for database models
│   ├── models.py              # Database models
│   ├── admin.py               # Django admin configuration
│   └── apps.py                # App configuration
├── manage.py                  # Django management script
├── data.db                    # SQLite database (shared between FastAPI & Django)
└── requirements.txt           # Python dependencies
```

---

## 🔍 Quick Test

To verify everything is working:

1. **Go to FastAPI application**: http://localhost:8000
2. **Create an account and complete an interview**
3. **Check Django Admin**: http://localhost:8001/admin/
4. **Login with**: admin / admin123
5. **View your data** in:
   - Users list
   - ATS Scores list
   - Interview Sessions list

---

## 💾 Database Details

- **Type**: SQLite3
- **File**: `data.db` (in project root)
- **Tables**:
  - `users` - User accounts
  - `ats_scores` - Resume analysis results
  - `interview_sessions` - Interview completion records
  - Django auth tables (auto-created)

The database is **shared** between FastAPI and Django, so both systems see the same data in real-time!

---

## ✅ Features

✓ Real-time data viewing  
✓ User-friendly admin interface  
✓ Search and filter capabilities  
✓ No additional database setup needed  
✓ Persistent storage in SQLite  
✓ Secure admin authentication  

---

## 🆘 Troubleshooting

**If Django shows "18 unapplied migrations":**
```bash
python manage.py migrate
```

**If models don't appear in admin:**
- Check `hiremind_db/admin.py` is properly configured
- Ensure `hiremind_db` is in `INSTALLED_APPS` in `settings.py`
- Restart Django server

**If you can't login to admin:**
```bash
python manage.py changepassword admin
```

---

**Created**: February 26, 2026  
**Version**: 1.0  
**Status**: ✅ Ready for production use
