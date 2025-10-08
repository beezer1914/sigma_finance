# Sigma Finance - Dues Payment Management System

A modern, high-performance web application for managing fraternity chapter dues and payments. Built with Flask, PostgreSQL, Redis, and Stripe integration.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎯 Overview

Sigma Finance is a comprehensive dues management platform designed specifically for Sigma Delta Sigma fraternity chapters. It provides members with an intuitive interface to view their payment status, make payments, and enroll in payment plans, while giving treasurers powerful tools to track finances and manage members.

### Key Features

- 💳 **Payment Processing** - Integrated Stripe checkout for secure online payments
- 📊 **Payment Plans** - Quarterly installment plans with automatic tracking
- 👥 **Member Management** - Role-based access control (Member, Treasurer, Admin)
- 📈 **Financial Dashboard** - Real-time overview of chapter finances
- 🔐 **Secure Authentication** - Password hashing, password reset, and invite-only registration
- ⚡ **High Performance** - Optimized database queries and Redis caching (98% faster)
- 🛡️ **Rate Limiting** - Protection against brute force and abuse
- 📧 **Email Notifications** - SendGrid integration for invites and password resets
- 📜 **Payment History** - Full audit trail with historical data import

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
   - Login: 5 attempts per minute
   - Registration: 3 per hour
   - Payment endpoints: 10 per minute

## 🛠️ Tech Stack

**Backend:**
- Flask 3.0+ (Python web framework)
- PostgreSQL (Production database)
- SQLite (Local development)
- Redis (Caching & rate limiting)
- SQLAlchemy (ORM)
- Flask-Login (Authentication)
- Flask-Migrate (Database migrations)

**Frontend:**
- Jinja2 Templates
- Tailwind CSS
- Vanilla JavaScript

**Payment Processing:**
- Stripe Checkout
- Webhook handling for payment verification

**Email:**
- SendGrid API

**Deployment:**
- Render (Web service, PostgreSQL, Redis)

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL (production) or SQLite (development)
- Redis (production) or SimpleCache (development)
- Stripe account
- SendGrid account (for emails)

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

### 6. Run Development Server

```bash
flask run
```

Visit http://localhost:5000

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
├── migrations/              # Database migrations
├── sigma_finance/
│   ├── forms/              # WTForms form definitions
│   ├── routes/             # Flask blueprints/routes
│   │   ├── auth.py         # Authentication routes
│   │   ├── payments.py     # Payment processing
│   │   ├── treasurer.py    # Treasurer dashboard
│   │   ├── webhooks.py     # Stripe webhook handler
│   │   └── ...
│   ├── services/           # Business logic
│   │   └── stats.py        # Statistics & analytics
│   ├── templates/          # Jinja2 templates
│   ├── utils/              # Helper functions
│   ├── app.py             # Application factory
│   ├── config.py          # Configuration classes
│   ├── extensions.py      # Flask extensions
│   └── models.py          # Database models
├── instance/               # Instance-specific files (gitignored)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

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

- **Password Hashing** - bcrypt with salt
- **CSRF Protection** - Flask-WTF
- **Rate Limiting** - Protection against brute force
- **Invite-Only Registration** - Controlled access
- **SQL Injection Prevention** - SQLAlchemy ORM
- **Stripe Webhook Verification** - Signature validation
- **Session Management** - Secure cookie handling
- **Role-Based Access Control** - Decorator-based permissions

## 👥 User Roles

### Member
- View personal dashboard
- Make one-time payments
- Enroll in payment plans
- View payment history

### Treasurer
- All member permissions
- View all member payments
- Manage members (add, edit, deactivate)
- Generate invite codes
- View financial statistics
- Reset payment records

### Admin
- All treasurer permissions
- System configuration
- Advanced administrative functions

## 💳 Payment Features

### One-Time Payments
- Full dues payment ($200)
- Stripe Checkout integration
- Instant confirmation
- Automatic status updates

### Payment Plans
- **Quarterly Plan**: 2 installments of $100
- Automatic calculation
- Progress tracking with visual indicators
- Auto-archival on completion

### Payment Methods
- Credit/Debit Card (Stripe)
- Manual entry (Cash, Check, etc.)
- Historical import

## 📊 Treasurer Dashboard

### Features
- Total dues collected
- Unpaid members list
- Active payment plans overview
- Outstanding balances
- Payment history with pagination
- Member management interface
- Invite code generation

### Statistics
- Payment summaries by type
- Payment method breakdown
- Monthly trends
- Per-member financial status

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