# Sigma Finance - Dues Payment Management System

A modern, high-performance full-stack web application for managing fraternity chapter dues and payments. Built with React 19, Flask, PostgreSQL, Redis, Stripe, and Twilio integration.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![React](https://img.shields.io/badge/react-19-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎯 Overview

Sigma Finance is a comprehensive dues management platform designed specifically for Sigma Delta Sigma fraternity chapters. Built as a modern single-page application (SPA) with React frontend and Flask REST API backend, it provides members with an intuitive interface to view their payment status, make payments, and enroll in payment plans, while giving treasurers powerful tools to track finances and manage members.

### Key Features

- ⚛️ **Modern React SPA** - Fast, responsive single-page application with React 19
- 💳 **Payment Processing** - Integrated Stripe checkout for secure online payments
- 📊 **Payment Plans** - Flexible installment plans (weekly, bi-weekly, monthly) with automatic tracking
- 👥 **Member Management** - Comprehensive member administration with role editing
- 📈 **Financial Dashboard** - Real-time overview of chapter finances and statistics
- 🔐 **Enhanced Security** - Strong password requirements (12+ chars), session management, CSRF protection
- ⚡ **High Performance** - Optimized database queries and Redis caching (98% faster)
- 🛡️ **Rate Limiting** - Intelligent protection against brute force attacks and abuse
- 📧 **Email Notifications** - SendGrid integration for invites and password resets
- 📞 **SMS Communications** - Twilio integration for member communications
- 🎫 **Invite System** - Secure invite codes with email delivery and expiration
- 📜 **Payment History** - Full audit trail with historical data import
- 💰 **Donation Tracking** - Record and manage organizational donations
- 📊 **Advanced Reporting** - Comprehensive financial reports and member analytics

## 🚀 Performance Optimizations

This application has been heavily optimized for production use:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Dashboard Load Time | 580ms | ~10ms | **98% faster** |
| Treasurer Dashboard | 1,800ms | ~50ms | **97% faster** |
| Unpaid Members Query | 1,200ms | ~5ms | **99.6% faster** |
| Database Queries (typical page) | 150+ | 2-3 | **98% reduction** |

### Optimization Techniques Applied

1. **Database Optimization**
   - Composite indexes on frequently queried columns
   - Eager loading with `joinedload()` to prevent N+1 queries
   - Optimized subqueries for complex filtering
   - Aggregate functions at database level

2. **Redis Caching**
   - Statistics cached for 5-10 minutes
   - Automatic cache invalidation on data changes
   - Shared cache across multiple instances

3. **Rate Limiting**
   - Login: 3 attempts per 15 minutes
   - Registration: 3 per hour
   - API endpoints: Intelligent limits per endpoint

## 🛠️ Tech Stack

**Frontend:**
- React 19 (Modern UI library)
- Vite (Build tool and dev server)
- React Router 7 (Client-side routing)
- Zustand (State management)
- React Hook Form + Zod (Form validation)
- Axios (HTTP client)
- Tailwind CSS (Styling)

**Backend:**
- Flask 3.0+ (Python REST API framework)
- PostgreSQL (Production database)
- SQLite (Local development)
- Redis (Caching & rate limiting)
- SQLAlchemy (ORM)
- Flask-Login (Session-based authentication)
- Flask-Migrate (Database migrations)
- Flask-Limiter (Rate limiting)

**Payment Processing:**
- Stripe Checkout
- Webhook handling for payment verification

**Communications:**
- SendGrid API (Transactional emails)
- Twilio API (SMS notifications)

**Deployment:**
- Render (Web service, PostgreSQL, Redis)
- Static site hosting (React build)

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL (production) or SQLite (development)
- Redis (production) or SimpleCache (development)
- Stripe account
- SendGrid account (for emails)
- Twilio account (for SMS, optional)

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/sigma_finance.git
cd sigma_finance
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_APP=sigma_finance.app:create_app
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///instance/sigma.db

# Redis (optional for local dev)
REDIS_URL=redis://localhost:6379/0

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# SendGrid
SENDGRID_API_KEY=SG....
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com

# Configuration Class
CONFIG_CLASS=sigma_finance.config.LocalConfig
```

### 5. Initialize Database

```bash
# Create database tables
flask db upgrade

# Optional: Create initial admin user
flask shell
>>> from sigma_finance.models import User
>>> admin = User(name="Admin", email="admin@example.com", role="treasurer")
>>> admin.set_password("your-password")
>>> from sigma_finance.extensions import db
>>> db.session.add(admin)
>>> db.session.commit()
>>> exit()
```

### 6. Frontend Setup

```bash
cd react-frontend
npm install
```

### 7. Run Development Servers

**Terminal 1 - Backend (Flask API):**
```bash
flask run
# API runs on http://localhost:5000
```

**Terminal 2 - Frontend (React):**
```bash
cd react-frontend
npm run dev
# Frontend runs on http://localhost:5173
```

Visit http://localhost:5173 to use the application

## 🚢 Production Deployment (Render)

### 1. Prerequisites on Render

Create these services in your Render dashboard:

1. **Web Service** (Python)
2. **PostgreSQL Database**
3. **Redis Key-Value Store**

### 2. Environment Variables (Render)

Add these in your web service's Environment tab:

```
CONFIG_CLASS=sigma_finance.config.ProductionConfig
FLASK_SECRET_KEY=<generate-strong-key>
DATABASE_URL=<from-render-postgres>
REDIS_URL=<from-render-redis>
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
SENDGRID_API_KEY=SG....
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com
TWILIO_ACCOUNT_SID=<your-twilio-sid>
TWILIO_AUTH_TOKEN=<your-twilio-token>
FRONTEND_URL=https://your-frontend.onrender.com
```

**For React Frontend (if hosting separately):**
```
VITE_API_URL=https://your-backend.onrender.com
```

### 3. Build Command

```bash
pip install --upgrade pip && pip install -r requirements.txt && flask db upgrade
```

### 4. Start Command

```bash
gunicorn -w 4 -b 0.0.0.0:$PORT 'sigma_finance.app:create_app()'
```

### 5. Stripe Webhook Setup

1. Go to Stripe Dashboard → Webhooks
2. Add endpoint: `https://your-app.onrender.com/webhook`
3. Select events: `checkout.session.completed`
4. Copy webhook secret to `STRIPE_WEBHOOK_SECRET`

## 📁 Project Structure

```
sigma_finance/
├── react-frontend/          # React SPA Frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Members.jsx
│   │   │   ├── MemberDetailModal.jsx
│   │   │   ├── Register.jsx
│   │   │   └── ...
│   │   ├── stores/         # Zustand state management
│   │   │   └── authStore.js
│   │   ├── services/       # API client
│   │   │   └── api.js      # Axios HTTP client
│   │   ├── utils/          # Helper functions
│   │   ├── App.jsx         # Main app component
│   │   └── main.jsx        # Entry point
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
├── migrations/             # Database migrations
├── sigma_finance/          # Flask Backend
│   ├── forms/             # WTForms form definitions
│   ├── routes/            # Flask blueprints/routes
│   │   ├── api.py         # REST API endpoints
│   │   ├── auth.py        # Legacy auth routes
│   │   ├── treasurer.py   # Treasurer blueprint (debug only)
│   │   ├── webhooks.py    # Stripe webhook handler
│   │   └── ...
│   ├── services/          # Business logic
│   │   └── stats.py       # Statistics & analytics
│   ├── templates/         # Jinja2 templates (debug mode only)
│   ├── utils/             # Helper functions
│   │   ├── password_validator.py
│   │   └── send_invite_email.py
│   ├── app.py            # Application factory
│   ├── config.py         # Configuration classes
│   ├── extensions.py     # Flask extensions
│   └── models.py         # Database models
├── instance/              # Instance-specific files (gitignored)
├── requirements.txt       # Python dependencies
├── USER_GUIDE.md         # End-user documentation
└── README.md             # This file
```

## 🏗️ Application Architecture

### Frontend-Backend Communication

The application follows a **decoupled SPA architecture**:

1. **React Frontend (Port 5173 in dev)**:
   - Single-page application built with Vite
   - Axios HTTP client for API communication
   - Session-based authentication with cookies
   - Client-side routing with React Router

2. **Flask Backend (Port 5000 in dev)**:
   - RESTful API serving JSON responses
   - Session management with Flask-Login
   - CORS configured for React dev server
   - In production: Only API routes registered

3. **Development Mode**:
   - Flask serves API at `/api/*` endpoints
   - Jinja templates available for debugging at other routes
   - React dev server proxies API requests
   - Hot module replacement (HMR) for fast development

4. **Production Mode**:
   - Flask serves only API routes (`/api/*`, `/webhook`)
   - Template blueprints NOT registered (reduces attack surface)
   - React app built and served as static files
   - Session cookies for authentication

### Key API Endpoints

**Authentication**:
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - New user registration
- `POST /api/auth/logout` - User logout
- `GET /api/auth/user` - Get current user

**Payments**:
- `GET /api/payments` - Get user's payment history
- `POST /api/payments/create-checkout` - Create Stripe checkout
- `POST /api/payment-plans` - Create payment plan

**Treasurer**:
- `GET /api/treasurer/members` - List all members (paginated)
- `GET /api/treasurer/members/:id` - Get member details
- `PUT /api/treasurer/members/:id` - Update member details
- `GET /api/treasurer/stats` - Financial statistics
- `GET /api/treasurer/reports/summary` - Financial reports

**Invites**:
- `GET /api/invites` - List invite codes (with stats)
- `POST /api/invites` - Create new invite code
- `DELETE /api/invites/:id` - Delete unused invite

**Donations**:
- `GET /api/donations` - List donations
- `POST /api/donations` - Record new donation
- `GET /api/donations/summary` - Donation statistics

## 🗃️ Database Schema

### Key Models

**User**
- Authentication and profile information
- Role-based permissions (member, treasurer, admin)
- Financial status tracking
- Initiation date for neophyte status

**Payment**
- Individual payment records
- Amount, date, method, type
- Links to payment plans
- Audit trail with notes

**PaymentPlan**
- Recurring payment schedules
- Quarterly, monthly, or weekly
- Automatic installment calculation
- Progress tracking

**InviteCode**
- Secure invite-only registration
- Role assignment
- Expiration and usage tracking

**WebhookEvent**
- Stripe webhook audit log
- Processing status
- Error tracking

## 🔐 Security Features

- **Strong Password Requirements** - Minimum 12 characters with complexity requirements:
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character
- **Password Hashing** - Werkzeug with salt
- **CSRF Protection** - Flask-WTF (API routes exempted for React)
- **Rate Limiting** - Intelligent protection against brute force attacks:
  - Login: 3 attempts per 15 minutes
  - Registration: 3 per hour
  - Per-endpoint rate limits
- **Invite-Only Registration** - Controlled access with expiring invite codes
- **SQL Injection Prevention** - SQLAlchemy ORM with parameterized queries
- **Stripe Webhook Verification** - Cryptographic signature validation
- **Session Management** - Secure cookie handling with session regeneration
- **Role-Based Access Control** - Decorator-based permissions
  - Only treasurers/admins can edit member details
  - Fine-grained access control for sensitive operations
- **Input Validation** - Frontend (Zod) and backend (WTForms) validation

## 👥 User Roles

### Member
- View personal dashboard
- Make one-time payments
- Enroll in flexible payment plans (weekly, bi-weekly, monthly)
- View payment history
- Update personal profile

### President / 1st Vice President
- All member permissions
- View all member payments
- View financial reports
- Access member list
- Create invite codes

### Treasurer
- All member and executive permissions
- Full member management:
  - Edit member details (name, email, role)
  - Update financial status
  - Set initiation dates
  - Activate/deactivate members
- Generate invite codes with email delivery
- View comprehensive financial statistics
- Record donations
- Access advanced reports

### Admin
- All treasurer permissions
- System configuration
- Advanced administrative functions
- Full database access

## 💳 Payment Features

### One-Time Payments
- Custom amount payments
- Stripe Checkout integration
- Instant confirmation and receipt
- Automatic financial status updates
- Notes/descriptions for tracking

### Payment Plans
- **Flexible Schedules**:
  - Weekly installments
  - Bi-weekly (every 2 weeks)
  - Monthly installments
- Custom total amounts and start dates
- Automatic installment calculation
- Progress tracking with visual indicators
- Balance tracking
- One active plan per member

### Payment Methods
- Credit/Debit Card (Stripe)
- Manual entry (Cash, Check, Bank Transfer, etc.)
- Historical import from Excel

## 📊 Treasurer Dashboard

### Features
- **Member Management**:
  - View all members with pagination
  - Filter by financial status, payment plan status
  - Search by name or email
  - View delinquent members
  - Edit member details (role, status, initiation date)
  - Click any member for detailed view
- **Invite System**:
  - Generate invite codes with expiration
  - Email delivery with SendGrid
  - Track invite status (unused, used, expired)
  - View who used each invite
- **Financial Overview**:
  - Total collections and payment counts
  - Active payment plan tracking
  - Outstanding balances
  - Delinquent member alerts
- **Donation Management**:
  - Record donations with details
  - Track donor history
  - View donation statistics
- **Reports**:
  - Comprehensive financial summaries
  - Member financial status breakdown
  - Payment type analysis
  - Export capabilities

## 📥 Historical Data Import

Import previous year's payment data from Excel:

```bash
python import_historical_payments.py
```

Features:
- Matches users by name or email
- Skips unregistered users
- Dry run mode for safety
- Detailed import report
- Marks payments as "historical"

## 🧪 Testing

```bash
# Run database optimization tests
python test_db_optimizations.py

# Check query performance
flask shell
>>> from sigma_finance.services.stats import get_unpaid_members
>>> import time
>>> start = time.time()
>>> members = get_unpaid_members()
>>> print(f"Query took: {(time.time() - start) * 1000:.2f}ms")
```

## 🐛 Troubleshooting

### Common Issues

**Database migrations fail**
```bash
# Reset migrations
flask db downgrade base
flask db upgrade
```

**Redis connection errors**
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG
```

**Stripe webhook not working**
- Verify webhook secret in environment variables
- Check webhook endpoint URL in Stripe dashboard
- Review webhook logs in Render dashboard

**Rate limiting too strict**
- Adjust limits in `extensions.py`
- Clear Redis: `redis-cli FLUSHALL`

## 📈 Performance Monitoring

### Health Check Endpoint

```bash
curl https://your-app.onrender.com/monitoring/health
```

Returns:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-10-07T12:00:00"
}
```

### Monitoring Cache Hit Rates

Check Redis stats:
```bash
redis-cli INFO stats
```

Look for:
- `keyspace_hits` - Cache hits
- `keyspace_misses` - Cache misses

Target: >70% hit rate

## 🔄 Maintenance

### Regular Tasks

**Weekly:**
- Monitor error logs in Render
- Check payment webhook processing
- Review rate limit violations

**Monthly:**
- Database vacuum (PostgreSQL): `VACUUM ANALYZE`
- Clear old webhook events
- Review member financial statuses

**Quarterly:**
- Update dependencies: `pip list --outdated`
- Security audit
- Performance review

### Database Backups

Render automatically backs up PostgreSQL databases. To manually export:

```bash
# From Render dashboard
pg_dump DATABASE_URL > backup.sql
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Brandon Holiday - Treasurer Sigma Delta Sigma Chapter- Phi Beta Sigma

## 🙏 Acknowledgments

- Sigma Delta Sigma Fraternity
- A lil bit of AI
- Stripe for payment processing
- Render for hosting platform

## 📞 Support

For issues, questions, or feature requests:
- Create an issue on GitHub
- Contact the chapter treasurer/developer

---

**Built with ❤️ for Sigma Delta Sigma - "Culture for Service, Service for Humanity"**