# Task & Habit Tracker (FocusTrack)

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-success?style=for-the-badge&logo=vercel)](https://task-habit-tracker-tau.vercel.app)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Database](https://img.shields.io/badge/Neon-PostgreSQL-00E599?style=for-the-badge&logo=postgresql)](https://neon.tech/)

> 🚀 **Live Production Deployment**: [https://task-habit-tracker-tau.vercel.app](https://task-habit-tracker-tau.vercel.app)

A clean, lightweight, secure, and production-quality Django web application for task management, habit tracking, and personal productivity analytics.

Built with Python 3.12 and Django 4.2, following modular architecture and modern UI/UX principles.

---

## Features

### 1. Task Management
- **Full CRUD**: Create, view, edit, and delete tasks with confirmation dialogs.
- **Priority Levels**: Color-coded badges for Low, Medium, High, and Urgent.
- **Categories**: Organize tasks by customizable categories with custom color badges.
- **Due Dates & Overdue Alerts**: Automatic detection of overdue tasks with visual alerts and dedicated filters.
- **Search & Filter**: Search by keywords; filter by status (All, Pending, Completed, Overdue) and priority; sort by due date, priority, or creation date.
- **HTMX In-Place Toggles**: Check off tasks instantly without full page reloads.
- **Pagination**: Scalable pagination preserving all active search and filter parameters.

### 2. Habit Tracker & Streaks Engine
- **Flexible Habits**: Configure habits with daily or weekly frequencies and target days per week.
- **Accurate Streak Engine**:
  - **Current Streak**: Tracks consecutive days; intelligently preserves streak if today is still pending but yesterday was completed.
  - **Longest Streak**: Computes all-time record consecutive days across your full history.
  - **Consistency Rates**: 7-day and 30-day percentage completion calculations.
- **Interactive 7-Day Grid**: Visual bubbles showing recent days with one-click HTMX checkoffs that update streak counts and progress bars in real time.

### 3. Dashboard & Analytics
- **Today's Action Center**: Centralized list of today's pending tasks and daily habits.
- **Productivity Pulse**: Overview cards for completed tasks, pending items, active habits, and streak leaders.
- **Interactive Charts (Chart.js)**:
  - 7-day productivity trend (tasks completed vs. created).
  - Priority distribution doughnut chart.
  - 30-day habit consistency performance bar chart.
  - Habit streak summary table.

### 4. Authentication & Customization
- **User Isolation**: Strict data isolation ensuring each user only accesses their own tasks, habits, and categories.
- **Profile Management**: Bio, name, and email editing.
- **Light & Dark Mode**: Seamless theme switching with instant DOM toggle and server/cookie persistence. Zero Flash of Unstyled Content (FOUC).

---

## Architecture & Technology Stack

- **Backend**: Python 3.12, Django 4.2.30, Django ORM
- **Database**: SQLite (preserving existing migrations and data)
- **Frontend**: Bootstrap 5.3.3, Bootstrap Icons 1.11.3, Vanilla JavaScript
- **Dynamic Interactions**: HTMX 1.9.12 (lightweight, ~14KB gzip)
- **Visual Analytics**: Chart.js 4.4.2
- **Zero Heavy Infrastructure**: No Node.js, React, Redis, or Celery overhead needed.

### Project Layout

```text
├── config/
│   ├── settings.py           # Settings with modular apps, static/templates, and auth config
│   ├── urls.py               # Root URL configuration
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── accounts/             # Authentication, Profile, and Theme persistence
│   ├── tasks/                # Task & Category models, views, and HTMX toggles
│   ├── habits/               # Habit models, streak calculation engine, 7-day grid
│   ├── dashboard/            # Dashboard KPIs, analytics, and Chart.js JSON API
│   └── core/                 # Shared context processors and utilities
│
├── templates/
│   ├── base.html             # Responsive layout with sidebar, navbar, and theme support
│   ├── components/           # Reusable partials (sidebar, navbar, alerts, pagination)
│   ├── accounts/             # Login, registration, profile, password change
│   ├── tasks/                # Task list, forms, confirmation dialogs, partials
│   ├── habits/               # Habit list, forms, interactive cards
│   └── dashboard/            # Dashboard and analytics pages
│
├── static/
│   ├── css/style.css         # Modern SaaS CSS with light/dark theme variables
│   └── js/
│       ├── app.js            # Theme toggle, mobile drawer, HTMX CSRF handling
│       └── analytics.js      # Chart.js initialization & theme-aware styling
│
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md
```

---

## Running the Application

### 1. In WSL / Linux

```bash
# Activate your existing virtual environment
source .venv/bin/activate

# Apply migrations
python manage.py migrate

# Run system checks
python manage.py check

# Run tests
python manage.py test

# Start the development server
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Verification & Testing

The test suite covers:
- Registration, login, profile signals, and theme persistence.
- Task CRUD, filtering, overdue calculation, HTMX toggle, and user data isolation.
- Habit streak calculations (today active, yesterday active, broken streaks, longest streak).
- Dashboard and analytics JSON endpoints.

Run the automated tests:
```bash
python manage.py test
```
All 17 automated tests pass with 0 failures and 0 errors.

---

## Deployment (Vercel & Neon PostgreSQL)

The application is deployed on Vercel with a Neon serverless PostgreSQL database:

- **Live URL**: [https://task-habit-tracker-tau.vercel.app](https://task-habit-tracker-tau.vercel.app)
- **WSGI Entry Point**: `api/index.py`
- **Configuration**: `vercel.json`
- **Static Asset Serving**: WhiteNoise (`whitenoise.middleware.WhiteNoiseMiddleware`)

