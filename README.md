
---

```markdown
# Sigma Finance Portal 🏛️

A modern Flask-based web application designed to streamline dues collection, payment plans, and financial transparency for the Sigma Delta Sigma chapter of Phi Beta Sigma Fraternity, Inc.

---

## ✨ Purpose

This portal empowers chapter leadership with:
- **Secure payment workflows** for one-time and installment-based dues
- **Role-based dashboards** for treasurers and officers
- **Automated tracking** of member payments and balances
- **Modern UI/UX** using Tailwind CSS for a clean, accessible experience
- **Future-proofed architecture** for easy onboarding and maintenance

Built with stewardship, clarity, and operational excellence in mind.

---

## 🛠️ Tech Stack

| Layer         | Tools Used                          |
|--------------|-------------------------------------|
| Backend       | Flask (Python), Jinja2 templates    |
| Frontend      | Tailwind CSS, HTML forms            |
| Automation    | Python scripts, Power Query logic   |
| Deployment    | GitHub, Render (optional)           |
| Environment   | Virtualenv or Anaconda (documented) |

---

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/sigma-finance.git
cd sigma-finance
```

### 2. Set Up Environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Run the App

```bash
flask run
```

App will be available at `http://localhost:5000`

---

## 🔐 Role-Based Access

- **Treasurer Dashboard**: View member payments, manage dues, reconcile balances
- **Officer Dashboard**: View chapter financial summaries (read-only)
- **Member Portal**: Submit payments, view history

---

## 📦 Folder Structure

```
sigma-finance/
├── app/                 # Flask blueprints and routes
│   ├── templates/       # Jinja2 HTML templates
│   ├── static/          # Tailwind CSS and assets
│   └── forms.py         # WTForms setup
├── migrations/          # (optional) DB migrations
├── requirements.txt     # Python dependencies
├── README.md            # You're here!
└── .gitignore
```

---

## 🧠 For Future Treasurers

This project includes:
- Clear documentation and modular code
- Environment setup guides to avoid Python path issues
- Scaffolding for new features (e.g. Stripe integration, payment reminders)
- Easy migration to Google Sheets or Render

---

## 📌 Roadmap

- [x] One-time and installment payment logic
- [x] Role-based dashboards
- [x] Tailwind UI integration
- [ ] Stripe payment integration
- [ ] Admin panel for member management
- [ ] Automated email receipts

---

## 🤝 Acknowledgments

Built with pride and purpose by Brandon, Treasurer of Sigma Delta Sigma chapter. Designed to empower future leaders and uphold the values of Phi Beta Sigma Fraternity, Inc.

---

```

---

