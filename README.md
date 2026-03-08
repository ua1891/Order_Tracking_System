# PulseTrack - Order Tracking System

PulseTrack is a modern, responsive, and secure web application built with Python (Flask) and Tailwind CSS. It allows you to seamlessly track parcels using the TCS ENVIO API, built with premium aesthetics and strong backend architecture.

## Features

- **Modern Dashboard UI:** Built with **Tailwind CSS** featuring a glassmorphism design, interactive hover states, and dynamic status badges.
- **Secure Authentication:** Administrator login powered by **Flask-Login** and hashed passwords to protect the tracking dashboard.
- **Live Tracking Integration:** Connects seamlessly to the TCS ENVIO API to fetch real-time checkpoint updates for tracked parcels.
- **Visual Timelines:** A beautifully styled, animated tracking timeline for visualizing a parcel's journey from origin to destination.
- **Background Synchronization:** Automated background tasks (via APScheduler) to keep parcel statuses up-to-date without manual intervention.
- **Code Quality:** Refactored backend avoiding code smells like hardcoded secrets, fat controllers, and global caching state issues.

## Technology Stack

### Backend
- **Python 3.10+**
- **Flask 3.x**
- **Flask-SQLAlchemy** (Database ORM)
- **Flask-Login** (Session Management & Authentication)
- **APScheduler** (Background Jobs)
- **SQLite** (Default Relational Database)

### Frontend
- **Tailwind CSS** (Utility-first styling via CDN)
- **Alpine.js** (Lightweight interactivity)
- **Phosphor Icons** & **Google Fonts (Inter / Outfit)**
- HTML5 / Jinja2 Templates

## Project Structure

```text
Order_Tracking_System/
├── backend/
│   └── tcs_client.py       # API connection & response parsing logic
├── database/
│   ├── instance/           # SQLite DB storage
│   └── models.py           # SQLAlchemy models (User, Order, Notification)
├── frontend/
│   ├── static/             # CSS, JS assets
│   └── templates/          # Jinja2 HTML views (base, login, dashboard, detail)
├── main/
│   └── app.py              # Flask app factory, Auth routing, and Dashboard logic
├── notifications/
│   └── scheduler.py        # APScheduler configuration
├── Status/
│   └── requirements.txt    # Python dependencies
└── start_app.bat           # Windows startup script
```

## Setup & Installation

Follow these instructions to run the application locally.

### 1. Requirements

Ensure you have Python 3.10+ installed.

### 2. Install Dependencies

Navigate to the project root and install the required packages:

```bash
pip install -r Status/requirements.txt
```

### 3. Environment Variables

Set your TCS API credentials as environment variables.
*On Windows (Command Prompt):*
```cmd
set TCS_CLIENT_ID=your_client_id
set TCS_CLIENT_SECRET=your_client_secret
set SECRET_KEY=your_secure_flask_key
```

### 4. Run the Application

Start the Flask development server:
```bash
python main/app.py
```

### 5. Access the Dashboard

1. Open a browser and navigate to: `http://127.0.0.1:5000`
2. **Default Admin Login:** 
   - **Username:** `admin`
   - **Password:** `admin`
*(Note: These credentials are auto-generated on first run for demonstration purposes.)*

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.
