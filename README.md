<div align="center">

#  Maison Rouge — Smart Expense Tracker

> **Spend smart. Live well.**  
> A luxury-grade personal expense tracker built with Django 5, Chart.js, and ReportLab — featuring AI-powered category prediction, beautiful analytics, and one-click PDF/CSV exports.

[![Django](https://img.shields.io/badge/Django-5.1-092E20?style=for-the-badge&logo=django&logoColor=white)](https://docs.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
[![ReportLab](https://img.shields.io/badge/ReportLab-5.0-B3001B?style=for-the-badge)](https://www.reportlab.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

---

</div>

## 📋 Table of Contents

- [✨ Features](#-features)
- [🗂️ Project Structure](#️-project-structure)
- [🏗️ Architecture Overview](#️-architecture-overview)
- [🔄 User Flow](#-user-flow)
- [🗄️ Database Schema](#️-database-schema)
- [🌐 URL Map](#-url-map)
- [🧠 AI Category Prediction Flow](#-ai-category-prediction-flow)
- [📊 Chart Data Pipeline](#-chart-data-pipeline)
- [📄 PDF Export Pipeline](#-pdf-export-pipeline)
- [🚀 Getting Started](#-getting-started)
- [⚙️ Configuration](#️-configuration)
- [🧪 Running Tests](#-running-tests)
- [🛠️ Tech Stack](#️-tech-stack)
- [📁 Key Files Reference](#-key-files-reference)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **Auth System** | Signup, Login, Logout with Django's built-in auth + session storage |
| 📊 **Dashboard** | Hero card, stat chips, doughnut + bar/line charts — all period-filtered |
| ➕ **Expense CRUD** | Add, Edit, Delete with floating-label form UI and validation |
| 🤖 **AI Prediction** | Keyword-based live category suggestion as you type (debounced, 350ms) |
| 📅 **Period Filters** | Today / This Week / This Month — segmented pill control |
| 📂 **Category Filter** | Filter expense list by category with inline dropdown |
| 📄 **CSV Export** | One-click download of filtered expenses as `.csv` |
| 🖨️ **PDF Export** | Branded ReportLab PDF with red header, alternating rows, summary total |
| 📱 **Responsive UI** | Mobile-first bottom tab bar + desktop FAB + glassmorphism cards |
| 🎨 **Design System** | 1,300+ line `luxury.css` — CSS custom properties, spring animations, floating labels |
| ♿ **Accessibility** | ARIA roles, labels, keyboard navigation, reduced-motion support |

---

## 🗂️ Project Structure

```
mo3-2/                              ← project root
│
├── manage.py                       ← Django management CLI
├── requirements.txt                ← pip dependencies
├── db.sqlite3                      ← SQLite database (dev)
│
├── expense_tracker/                ← Django project config
│   ├── settings.py                 ← All settings (DB, auth, static, TZ)
│   ├── urls.py                     ← Root URL dispatcher
│   └── wsgi.py                     ← WSGI entry point
│
├── accounts/                       ← Auth app
│   ├── views.py                    ← landing, signup, login, logout
│   ├── urls.py                     ← /, /signup/, /login/, /logout/
│   ├── forms.py                    ← SignupForm, LoginForm
│   └── templates/accounts/
│       ├── landing.html
│       ├── signup.html
│       └── login.html
│
├── expenses/                       ← Core app
│   ├── models.py                   ← Category, Expense models
│   ├── views.py                    ← All 9 views + 2 API endpoints
│   ├── urls.py                     ← 9 URL patterns
│   ├── forms.py                    ← ExpenseForm (with validation)
│   ├── utils.py                    ← predict_category() keyword engine
│   ├── admin.py                    ← Django admin registration
│   ├── tests.py                    ← Unit + integration tests
│   └── migrations/
│       ├── 0001_initial.py         ← Category + Expense tables
│       └── 0002_seed_categories.py ← Seeds 9 default categories
│
├── templates/                      ← Global template root
│   ├── base.html                   ← Shared layout (nav, toast, tab bar)
│   └── expenses/
│       ├── dashboard.html
│       ├── expense_list.html
│       ├── expense_form.html       ← Add & Edit (shared)
│       ├── expense_confirm_delete.html
│       └── reports.html
│
└── static/
    ├── css/
    │   └── luxury.css              ← Maison Rouge design system (1,362 lines)
    └── js/
        ├── app.js                  ← UI interactions (segmented, toasts, forms)
        └── charts.js               ← Chart.js doughnut + timeseries renderer
```

---

## 🏗️ Architecture Overview

```mermaid
graph TB
    subgraph CLIENT["🖥️  Browser Client"]
        direction LR
        HTML["HTML Templates"]
        CSS["luxury.css<br/>Design System"]
        JS_APP["app.js<br/>UI Logic"]
        JS_CHART["charts.js<br/>Chart.js Renderer"]
    end

    subgraph DJANGO["⚙️  Django Application"]
        direction TB
        URL_ROOT["expense_tracker/urls.py<br/>Root URL Dispatcher"]

        subgraph ACCOUNTS["👤 accounts app"]
            ACC_URLS["urls.py"]
            ACC_VIEWS["views.py<br/>landing · signup · login · logout"]
            ACC_FORMS["forms.py<br/>SignupForm · LoginForm"]
        end

        subgraph EXPENSES["💸 expenses app"]
            EXP_URLS["urls.py"]
            EXP_VIEWS["views.py<br/>dashboard · list · add · edit · delete<br/>reports · export_csv · export_pdf<br/>api_predict · api_chart"]
            EXP_FORMS["forms.py<br/>ExpenseForm"]
            EXP_UTILS["utils.py<br/>predict_category()"]
            EXP_MODELS["models.py<br/>Category · Expense"]
        end
    end

    subgraph DATA["🗄️  Data Layer"]
        DB[("SQLite<br/>db.sqlite3")]
        MIGRATIONS["migrations/<br/>0001_initial<br/>0002_seed_categories"]
    end

    subgraph EXPORTS["📤  Export Layer"]
        CSV["csv module<br/>CSV Export"]
        PDF["ReportLab<br/>PDF Export"]
    end

    CLIENT -->|HTTP Requests| URL_ROOT
    URL_ROOT --> ACC_URLS --> ACC_VIEWS
    URL_ROOT --> EXP_URLS --> EXP_VIEWS
    ACC_VIEWS --> ACC_FORMS
    EXP_VIEWS --> EXP_FORMS
    EXP_VIEWS --> EXP_UTILS
    EXP_VIEWS --> EXP_MODELS
    EXP_MODELS --> DB
    MIGRATIONS --> DB
    EXP_VIEWS --> CSV
    EXP_VIEWS --> PDF
    JS_CHART -->|"GET /api/chart-data/"| EXP_VIEWS
    JS_APP  -->|"GET /api/predict-category/"| EXP_VIEWS
```

---

## 🔄 User Flow

```mermaid
flowchart TD
    A([🌐 Visit /]) --> B{Logged In?}
    B -- No --> C[Landing Page]
    B -- Yes --> D[🏠 Dashboard]

    C --> E[Sign Up /signup/]
    C --> F[Log In /login/]

    E --> G{Form Valid?}
    G -- No --> E
    G -- Yes --> H[Auto-Login]
    H --> D

    F --> I{Credentials OK?}
    I -- No --> F
    I -- Yes --> D

    D --> J[Period Filter<br/>Today / Week / Month]
    J --> D

    D --> K[📋 View All Expenses]
    D --> L[➕ Add Expense]
    D --> M[📊 Reports]

    K --> N{Filter by Category?}
    N -- Yes --> O[Filtered List]
    N -- No --> P[Full Paginated List]
    O & P --> Q[Edit ✏️]
    O & P --> R[Delete 🗑️]

    L --> S{Form Valid?}
    S -- No --> L
    S -- Yes --> T[💾 Save & Redirect to Dashboard]

    Q --> U{Form Valid?}
    U -- No --> Q
    U -- Yes --> T

    R --> V[Confirm Delete]
    V -- Confirm --> W[Delete and Go to Expenses]
    V -- Cancel --> K

    M --> X[📥 Download CSV]
    M --> Y[📄 Download PDF]

    D --> Z[Sign Out]
    Z --> C
```

---

## 🗄️ Database Schema

```mermaid
erDiagram
    AUTH_USER {
        int id PK
        string username
        string email
        string password
        bool is_active
        datetime date_joined
    }

    CATEGORY {
        int id PK
        string name "unique, max 100 chars"
        string color "hex RRGGBB, default B3001B"
    }

    EXPENSE {
        int id PK
        int user_id FK
        int category_id FK "nullable"
        string description "max 255"
        decimal amount "10,2 must be gt 0"
        date date "default today"
        text notes "optional"
        datetime created_at "auto_now_add"
    }

    AUTH_USER ||--o{ EXPENSE : "owns"
    CATEGORY  ||--o{ EXPENSE : "classifies"
```

### 🌱 Seeded Categories

| # | Category | Hex Color |
|---|---|---|
| 1 | 🍕 Food | `#E63946` |
| 2 | 🛒 Groceries | `#2E7D5B` |
| 3 | 🚕 Travel | `#F59E0B` |
| 4 | 💊 Health | `#7C3AED` |
| 5 | 🎬 Entertainment | `#DB2777` |
| 6 | 📚 Education | `#0891B2` |
| 7 | ⚡ Bills | `#B3001B` |
| 8 | 🛍️ Shopping | `#EA580C` |
| 9 | 📦 Others | `#6B6B6B` |

---

## 🌐 URL Map

```mermaid
graph LR
    ROOT["/ root"]

    ROOT --> LAND["/ → landing"]
    ROOT --> SIGNUP["/signup/ → signup_view"]
    ROOT --> LOGIN["/login/ → login_view"]
    ROOT --> LOGOUT["/logout/ → logout_view"]

    ROOT --> DASH["/dashboard/ → dashboard"]
    ROOT --> LIST["/expenses/ → expense_list"]
    ROOT --> ADD["/expenses/add/ → expense_add"]
    ROOT --> EDIT["/expenses/pk/edit/ → expense_edit"]
    ROOT --> DEL["/expenses/pk/delete/ → expense_delete"]

    ROOT --> RPT["/reports/ → reports"]
    ROOT --> CSV["/reports/export/csv/ → export_csv"]
    ROOT --> PDF["/reports/export/pdf/ → export_pdf"]

    ROOT --> API1["/api/predict-category/ → api_predict_category"]
    ROOT --> API2["/api/chart-data/ → api_chart_data"]

    style API1 fill:#B3001B,color:#fff
    style API2 fill:#B3001B,color:#fff
    style DASH fill:#2E7D5B,color:#fff
```

| Method | Endpoint | View | Auth Required |
|---|---|---|---|
| `GET` | `/` | `landing` | ❌ |
| `GET POST` | `/signup/` | `signup_view` | ❌ |
| `GET POST` | `/login/` | `login_view` | ❌ |
| `POST` | `/logout/` | `logout_view` | ✅ |
| `GET` | `/dashboard/` | `dashboard` | ✅ |
| `GET` | `/expenses/` | `expense_list` | ✅ |
| `GET POST` | `/expenses/add/` | `expense_add` | ✅ |
| `GET POST` | `/expenses/<pk>/edit/` | `expense_edit` | ✅ |
| `GET POST` | `/expenses/<pk>/delete/` | `expense_delete` | ✅ |
| `GET` | `/reports/` | `reports` | ✅ |
| `GET` | `/reports/export/csv/` | `export_csv` | ✅ |
| `GET` | `/reports/export/pdf/` | `export_pdf` | ✅ |
| `GET` | `/api/predict-category/` | `api_predict_category` | ❌ |
| `GET` | `/api/chart-data/` | `api_chart_data` | ✅ |

---

## 🧠 AI Category Prediction Flow

```mermaid
sequenceDiagram
    participant User as 👤 User (browser)
    participant JS as app.js
    participant API as /api/predict-category/
    participant Utils as utils.py
    participant Form as Expense Form

    User->>JS: Types in description field
    JS->>JS: Debounce 350ms
    JS->>API: GET ?q=description text
    API->>Utils: predict_category(description)
    Utils->>Utils: Lowercase then scan CATEGORY_KEYWORDS dict
    alt Match found
        Utils-->>API: Food or Travel or etc.
        API-->>JS: category Food
        JS->>Form: Auto-select matching option
        JS->>User: Show Suggested Food badge
    else No match
        Utils-->>API: Others
        API-->>JS: category Others
        JS->>User: Badge hidden
    end
    User->>Form: Can override category manually
```

### Keyword Dictionary (excerpt)

```python
CATEGORY_KEYWORDS = {
    'Food':          ['pizza', 'burger', 'swiggy', 'zomato', 'restaurant', ...],
    'Groceries':     ['bigbasket', 'blinkit', 'zepto', 'dmart', 'milk', ...],
    'Travel':        ['uber', 'ola', 'petrol', 'metro', 'flight', 'bus', ...],
    'Health':        ['doctor', 'medicine', 'gym', 'hospital', 'pharmacy', ...],
    'Entertainment': ['netflix', 'spotify', 'movie', 'concert', 'gaming', ...],
    'Bills':         ['electricity', 'rent', 'wifi', 'emi', 'insurance', ...],
    'Shopping':      ['amazon', 'flipkart', 'myntra', 'clothes', 'shoes', ...],
    'Education':     ['udemy', 'coursera', 'book', 'tuition', 'college', ...],
}
```

---

## 📊 Chart Data Pipeline

```mermaid
flowchart LR
    subgraph BROWSER["🖥️ Browser"]
        A["DOMContentLoaded\ncharts.js"]
        B["Read period from\nbody data-period"]
        C["fetch /api/chart-data/\nperiod=month"]
    end

    subgraph SERVER["⚙️ Django"]
        D["api_chart_data view"]
        E["Filter Expense queryset\nby user and date range"]
        F["Category totals\nvalues then annotate Sum"]
        G["Daily totals\nTruncDate then annotate Sum"]
        H["Return JSON\ndoughnut timeseries total"]
    end

    subgraph RENDER["📊 Chart.js"]
        I["renderDoughnut\n65 pct cutout legend bottom"]
        J["renderTimeSeries\nbar le 7 labels line gt 7"]
    end

    A --> B --> C --> D
    D --> E --> F --> G --> H
    H --> I
    H --> J
```

---

## 📄 PDF Export Pipeline

```mermaid
flowchart TD
    A["User clicks Download PDF\n/reports/export/pdf/"] --> B["export_pdf view"]
    B --> C["Filter Expense queryset\nby user and period"]
    C --> D["Create HttpResponse\ncontent_type=application/pdf"]
    D --> E["SimpleDocTemplate\nA4 with 2cm margins"]

    E --> F["Build Story list"]
    F --> G1["Paragraph: Title\nSmart Expense Tracker"]
    F --> G2["Paragraph: Subtitle\nSpend smart. Live well."]
    F --> G3["Paragraph: User and Date range"]
    F --> G4["Table: expense rows\nDate Desc Category Amount Notes"]
    F --> G5["Total row\nDEEP_RED background"]
    F --> G6["Footer: Generated on date"]

    G4 --> H["TableStyle\nMAISON_RED header\nAlternating rows\n0.5pt grid lines"]
    H --> I["doc.build story"]
    I --> J["Browser downloads PDF"]
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10+**
- `pip`
- `git`

### 1 — Clone the repository

```bash
git clone <your-repo-url>
cd mo3-2
```

### 2 — Create & activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Apply migrations & seed categories

```bash
python manage.py migrate
```

> The migration `0002_seed_categories` automatically seeds 9 default categories.

### 5 — Create a superuser *(optional — for Django admin panel)*

```bash
python manage.py createsuperuser
```

### 6 — Run the development server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser — you should see the Maison Rouge landing page. Sign up for a new account and start tracking!

---

## ⚙️ Configuration

All settings live in `expense_tracker/settings.py`:

| Setting | Default Value | Description |
|---|---|---|
| `DEBUG` | `True` | Disable in production |
| `TIME_ZONE` | `Asia/Kolkata` | IST — change to your TZ |
| `LANGUAGE_CODE` | `en-us` | Localisation |
| `CURRENCY_SYMBOL` | `₹` | Displayed across templates |
| `LOGIN_URL` | `/login/` | Redirect for `@login_required` |
| `LOGIN_REDIRECT_URL` | `/dashboard/` | After successful login |
| `LOGOUT_REDIRECT_URL` | `/` | After logout |
| `DATABASE.ENGINE` | `sqlite3` | Switch to `postgresql` for production |
| `STATIC_URL` | `/static/` | Static files URL prefix |
| `MESSAGE_STORAGE` | `session.SessionStorage` | Toast message backend |

---

## 🧪 Running Tests

```bash
python manage.py test expenses
```

The test suite in `expenses/tests.py` covers:

```mermaid
mindmap
  root((🧪 Test Suite))
    Models
      Category creation
      Expense creation
      User ownership
      Str representation
    Views
      Dashboard GET
      Expense list filtering
      Add expense POST
      Edit expense POST
      Delete expense POST
      CSV export
      PDF export
    API
      predict-category endpoint
      chart-data endpoint
    Utils
      predict_category keywords
      Default fallback
    Auth
      Login required redirects
      User isolation
```

---

## 🛠️ Tech Stack

```mermaid
graph LR
    subgraph BACKEND["⚙️ Backend"]
        B1["Python 3.10+"]
        B2["Django 5.1"]
        B3["SQLite 3"]
        B4["ReportLab 5.0"]
        B5["Pillow 12"]
        B1 --> B2 --> B3
        B2 --> B4
        B2 --> B5
    end

    subgraph FRONTEND["🎨 Frontend"]
        F1["Django Templates"]
        F2["luxury.css"]
        F3["Bootstrap 5.3"]
        F4["Chart.js 4.4"]
        F5["Google Fonts"]
        F6["Vanilla JS"]
        F1 --> F2
        F2 --> F3
        F6 --> F4
    end

    BACKEND --- FRONTEND
```

| Layer | Technology | Version |
|---|---|---|
| Web Framework | Django | `>=5.0, <6.0` |
| Language | Python | `3.10+` |
| Database | SQLite | built-in |
| PDF Generation | ReportLab | `>=4.0` |
| Image Processing | Pillow | `>=10.0` |
| Charts | Chart.js | `4.4.0` (CDN) |
| CSS Framework | Bootstrap | `5.3.2` (CDN, grid only) |
| Typography | Google Fonts | Inter + Playfair Display |

---

## 📁 Key Files Reference

| File | Lines | Purpose |
|---|---|---|
| `expense_tracker/settings.py` | 106 | Project-wide settings |
| `expense_tracker/urls.py` | 21 | Root URL configuration |
| `expenses/models.py` | 66 | `Category` and `Expense` models |
| `expenses/views.py` | 551 | All views + API endpoints |
| `expenses/forms.py` | 69 | `ExpenseForm` with amount validation |
| `expenses/utils.py` | 90 | `predict_category()` keyword engine |
| `expenses/urls.py` | 28 | All URL patterns for the expenses app |
| `accounts/views.py` | 83 | Auth views: landing, signup, login, logout |
| `templates/base.html` | 146 | Shared layout: navbar, toast, tab bar, FAB |
| `templates/expenses/dashboard.html` | 173 | Main dashboard template |
| `static/css/luxury.css` | 1,362 | Maison Rouge design system |
| `static/js/app.js` | 265 | Segmented control, toasts, AI badge, forms |
| `static/js/charts.js` | 202 | Chart.js doughnut + timeseries renderer |

---

## 🚀 Deploying to Vercel

This repository is pre-configured for seamless deployment on [Vercel](https://vercel.com):

1. **Import to Vercel**:
   - Log in to [vercel.com](https://vercel.com) and click **"Add New Project"**.
   - Select and import your GitHub repository: `akashvoffi-design/Smart-Expense-Tracker`.

2. **Configure Environment Variables** (in Vercel Settings > Environment Variables):
   - `SECRET_KEY`: A secure random secret key.
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `*` (or your Vercel domain e.g. `.vercel.app`)
   - `DATABASE_URL`: *(Recommended for production)* PostgreSQL connection string (from Neon, Supabase, or Railway). If omitted, an ephemeral SQLite database in `/tmp` is automatically initialized for demonstration.

3. **Deploy**:
   - Click **Deploy**. Vercel will execute `build_files.sh`, collect static assets with WhiteNoise, and serve the WSGI application serverlessly.

---

<div align="center">

**Made with ❤️ and ₹ in mind**

*Maison Rouge — Smart Expense Tracker*

`Spend smart. Live well.`

</div>

