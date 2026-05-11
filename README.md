# Traveloop - Odoo
An app used for traveller for creating their plans to shown easily.

A full-stack travel planning web application built with **Flask + SQLite + HTML/CSS/JS**.

---

## 📁 Project Structure

```
traveloop/
├── backend/
│   └── app.py              ← Flask app, all routes, database models
├── templates/
│   ├── base.html           ← Shared layout with sidebar nav
│   ├── login.html          ← Login page
│   ├── signup.html         ← Sign up page
│   ├── dashboard.html      ← Home dashboard
│   ├── my_trips.html       ← All trips list
│   ├── create_trip.html    ← New trip form
│   ├── itinerary_builder.html  ← Add stops & activities
│   ├── itinerary_view.html ← View / share trip
│   ├── budget.html         ← Budget & cost breakdown
│   ├── checklist.html      ← Packing checklist
│   ├── notes.html          ← Trip notes/journal
│   └── profile.html        ← User profile settings
├── static/
│   ├── css/
│   │   └── style.css       ← All styles + design system
│   └── js/
│       └── main.js         ← Shared JS utilities
├── requirements.txt        ← Python packages
└── README.md
```

---

## 🚀 Setup & Run

### 1. Create a virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
cd backend
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

---

## 🔑 Features

| Screen | Description |
|--------|-------------|
| Login / Signup | Secure authentication with hashed passwords |
| Dashboard | Stats overview, recent trips, popular destinations |
| My Trips | Full trip list with edit/view/delete actions |
| Create Trip | Name, dates, budget, public/private setting |
| Itinerary Builder | Add city stops + activities with city/activity search |
| Itinerary View | Timeline view of full trip with cost summary |
| Budget Screen | Category breakdowns, per-city costs, donut chart |
| Packing Checklist | Add items, mark as packed, categorized by type |
| Trip Notes | Freeform notes tied to trips or cities |
| Profile | Edit name/language, view trip stats |

---

## 🎨 Design System

- **Fonts**: Playfair Display (headings) + DM Sans (body)
- **Colors**: Warm sand/cream backgrounds, amber accents, teal primary
- **Style**: Editorial travel magazine aesthetic
- **Responsive**: Works on mobile (sidebar hidden, bottom nav shown)

---

## 🛠️ How to Customize

### Add new cities to search:
Edit the `cities` list in `backend/app.py` inside `/api/cities/search`

### Change colors/fonts:
Edit `:root` variables in `static/css/style.css`

### Add new pages:
1. Create a new route in `backend/app.py`
2. Create a new template in `templates/` extending `base.html`
3. Add a nav link in `templates/base.html`

### Database:
- SQLite file auto-created at `backend/traveloop.db`
- To reset: delete `traveloop.db` and restart

---

## 📦 Tech Stack

- **Backend**: Python 3 + Flask + Flask-SQLAlchemy
- **Database**: SQLite (easy to swap to PostgreSQL/MySQL)
- **Frontend**: Vanilla HTML + CSS + JavaScript (no framework needed)
- **Fonts**: Google Fonts (loaded via CDN)

---

*Built for Odoo Hackathon — Traveloop Problem Statement*