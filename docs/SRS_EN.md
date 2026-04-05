# Software Requirements Specification (SRS)
# Kindergarten Management System (KMS)

**Version:** 1.0  
**Date:** April 2026  
**Author:** aittrial  

---

## 1. Introduction

### 1.1 Purpose
This document describes the functional and non-functional requirements for the Kindergarten Management System (KMS). It is intended for developers, testers, and project stakeholders.

### 1.2 Scope
KMS automates the management of one or multiple kindergartens: children records, attendance tracking, product warehouse, expenses, parent payments, and report generation.

### 1.3 Definitions and Abbreviations
| Term | Definition |
|------|------------|
| KMS | Kindergarten Management System |
| Superadmin | System-wide administrator managing multiple kindergartens |
| Admin | Staff member managing a single assigned kindergarten |
| Kindergarten | Structural unit of the system |
| Debtor | A child whose parents have not paid or partially paid the monthly fee |

---

## 2. Overall Description

### 2.1 Product Perspective
KMS is a multi-user web application. The system is deployed in the cloud (Streamlit Cloud) and uses a cloud database (PostgreSQL on Neon.tech). Access is via browser with no additional software required.

### 2.2 Product Features (Summary)
- Multi-tenant architecture (multiple kindergartens)
- Children management (groups, parent data)
- Attendance journal
- Product warehouse with minimum stock alerts
- Expense tracking by category
- Parent payment tracking (full/partial)
- Automatic debtor detection
- Report generation and Excel export
- Bilingual interface (Russian / English)
- Multi-currency support (ILS / USD / EUR)

### 2.3 User Classes

| Role | Description |
|------|-------------|
| **Superadmin** | One instance. Manages all kindergartens: create, edit, delete. Assigns admins to kindergartens. Can enter any kindergarten. |
| **Admin** | Linked to one kindergarten. Sees only their kindergarten's data. Manages children, attendance, warehouse, expenses, payments. |

### 2.4 Operating Environment
| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit ≥ 1.35.0 |
| Backend | Python 3.10+ |
| ORM | SQLAlchemy ≥ 1.4, < 3.0 |
| Database | PostgreSQL (Neon.tech) / SQLite (local) |
| Deployment | Streamlit Cloud |
| Repository | GitHub |
| Export | pandas + xlsxwriter |

---

## 3. Functional Requirements

### 3.1 Authentication Module

| ID | Requirement |
|----|-------------|
| AUTH-01 | System must support login via email and password |
| AUTH-02 | Passwords stored as bcrypt hash |
| AUTH-03 | If no superadmin exists, a registration tab is displayed |
| AUTH-04 | After superadmin creation, public registration is disabled |
| AUTH-05 | Users can log out at any time |
| AUTH-06 | Language and currency are saved in profile and restored on next login |

### 3.2 Kindergarten Management (Superadmin only)

| ID | Requirement |
|----|-------------|
| KG-01 | Superadmin can create a new kindergarten (name, address, phone, logo URL) |
| KG-02 | Superadmin can edit kindergarten details |
| KG-03 | Superadmin can delete a kindergarten (cascades to all related data) |
| KG-04 | Superadmin sees a list of all kindergartens and can enter any |
| KG-05 | When inside a kindergarten, superadmin sees all its data |
| KG-06 | Superadmin can return to the kindergarten list from any page |

### 3.3 Admin Management (Superadmin only)

| ID | Requirement |
|----|-------------|
| ADM-01 | Superadmin can create a new admin |
| ADM-02 | Admin creation requires email, password, and kindergarten assignment |
| ADM-03 | Superadmin can change an admin's password |
| ADM-04 | Superadmin can delete an admin |
| ADM-05 | Admin can only see data belonging to their assigned kindergarten |

### 3.4 Children Management

| ID | Requirement |
|----|-------------|
| CH-01 | System stores: first name, last name, birth date, parent name, parent phone, enrollment date, group, monthly fee, status |
| CH-02 | Groups: junior (младшая), middle (средняя), senior (старшая) |
| CH-03 | Statuses: active (активный), inactive (неактивный) |
| CH-04 | Filtering by group and status |
| CH-05 | Add, edit, and deactivate children |
| CH-06 | Display child age in years and months |
| CH-07 | Data is isolated per kindergarten |

### 3.5 Attendance Journal

| ID | Requirement |
|----|-------------|
| ATT-01 | Daily attendance marking for each child |
| ATT-02 | Statuses: present (присутствовал), absent (отсутствовал), sick (болел) |
| ATT-03 | Filter by group and date |
| ATT-04 | Daily summary (present/absent counts) |
| ATT-05 | Duplicate attendance record for same child and date is prevented |

### 3.6 Product Warehouse

| ID | Requirement |
|----|-------------|
| PRD-01 | System stores: product name, unit of measure, minimum stock level |
| PRD-02 | Transaction types: income (receipt) and expense (consumption) |
| PRD-03 | Current stock calculated automatically (income − expense) |
| PRD-04 | Dashboard alert when stock falls below minimum |
| PRD-05 | Transaction history per product |
| PRD-06 | Products isolated per kindergarten |

### 3.7 Expense Tracking

| ID | Requirement |
|----|-------------|
| EXP-01 | Expense record: date, category, amount, description, comment |
| EXP-02 | Categories: Food, Transport, Housing, Communications, Other |
| EXP-03 | Filter by month and category |
| EXP-04 | Monthly and per-category totals |
| EXP-05 | Expenses isolated per kindergarten |

### 3.8 Parent Payment Tracking

| ID | Requirement |
|----|-------------|
| PAY-01 | Payment record: child, year, month, amount, payment date, comment |
| PAY-02 | A child can have multiple payments per month (partial payments) |
| PAY-03 | Child is a debtor if sum of all payments for a month < monthly fee |
| PAY-04 | Debt amount displayed (fee − total paid) |
| PAY-05 | Debtor list filterable by month |
| PAY-06 | Payment history per child |
| PAY-07 | Dashboard alert when debtors exist |

### 3.9 Reports

| ID | Requirement |
|----|-------------|
| REP-01 | Attendance report for selected month |
| REP-02 | Financial report: income (payments) vs expenses for a month |
| REP-03 | Export reports to Excel (.xlsx) |
| REP-04 | Reports isolated per kindergarten |

### 3.10 Interface and Localization

| ID | Requirement |
|----|-------------|
| I18N-01 | Interface supports Russian and English languages |
| I18N-02 | Language selection available before and after login |
| I18N-03 | Supported currencies: ILS (₪), USD ($), EUR (€) |
| I18N-04 | Language and currency saved in user profile |
| I18N-05 | All amounts displayed in selected currency |

---

## 4. Non-Functional Requirements

### 4.1 Security
- Passwords stored exclusively as bcrypt hash
- Each user sees only their kindergarten's data
- Superadmin features inaccessible to regular admins
- Database connection via SSL (Neon.tech)

### 4.2 Performance
- Page load time ≤ 3 seconds under standard load
- Excel export ≤ 10 seconds for monthly reports

### 4.3 Reliability
- Application uses try/finally for proper DB session closing
- Falls back to SQLite when cloud DB is unavailable (local development only)

### 4.4 Scalability
- Architecture supports unlimited number of kindergartens
- Each kindergarten fully isolated via kindergarten_id

### 4.5 Availability
- Web interface accessible from any device via browser
- Mobile browser supported (Streamlit responsive layout)

---

## 5. System Architecture

### 5.1 File Structure
```
kindergarden_advanced/
├── main.py                 # Entry point, routing
├── database.py             # DB connection, engine, Base
├── models.py               # SQLAlchemy models
├── crud.py                 # CRUD operations
├── auth.py                 # Password hashing
├── auth_guard.py           # Page guards, sidebar
├── i18n.py                 # Translations, currencies, lookups
├── seed.py                 # Test data population
├── requirements.txt
└── pages/
    ├── kindergartens.py    # Kindergarten management
    ├── 1_Дети.py           # Children management
    ├── 2_Посещаемость.py   # Attendance journal
    ├── 3_Продукты.py       # Warehouse
    ├── 4_Расходы.py        # Expenses
    ├── 5_Отчеты.py         # Reports
    ├── 6_Админы.py         # Admin management
    └── 7_Оплата.py         # Payments
```

### 5.2 Data Model (ERD)
```
Kindergarten
  └─< User (admins)
  └─< Child
        └─< Attendance
        └─< Payment
  └─< Product
        └─< ProductTransaction
  └─< Expense
```

### 5.3 Database Tables

**kindergartens:** id, name, address, phone, logo_url

**users:** id, email, password_hash, role, language, currency, kindergarten_id(FK)

**children:** id, kindergarten_id(FK), first_name, last_name, birth_date, parent_name, parent_phone, enrollment_date, status, group, monthly_fee

**attendance:** id, child_id(FK), date, status

**products:** id, kindergarten_id(FK), name, unit, min_stock

**product_transactions:** id, product_id(FK), date, quantity, transaction_type

**expenses:** id, kindergarten_id(FK), date, category, amount, description, comment

**payments:** id, child_id(FK), year, month, amount, paid_date, comment

---

## 6. External Interfaces

### 6.1 User Interface
- Streamlit web UI, adapted for desktop and mobile browsers
- Navigation via sidebar (st.navigation)
- Language/currency selectable in sidebar and on login page

### 6.2 Database
- Production: PostgreSQL on Neon.tech via DATABASE_URL in Streamlit Cloud Secrets
- Development: SQLite file `local_storage.db`

### 6.3 Data Export
- Format: Microsoft Excel (.xlsx)
- Library: pandas + xlsxwriter

---

## 7. Constraints and Assumptions

- System designed for small concurrent user count (up to 20)
- All dates stored in UTC
- Financial calculations use float, rounded to 2 decimal places
- Kindergarten logos stored as URLs (not file uploads)
- No email/SMS notification functionality

---

## 8. Future Enhancements (out of scope for v1.0)

- Push notifications or email/SMS for parents
- Mobile application
- Banking integration for automatic payment reconciliation
- Child photos
- PDF document generation
- Digital meal journal
- Class schedule management
