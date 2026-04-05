# User Manual
# Kindergarten Management System (KMS)

**Version:** 1.0 | **Date:** April 2026

---

## Table of Contents
1. [Getting Started](#1-getting-started)
2. [Login](#2-login)
3. [Settings (Language and Currency)](#3-settings)
4. [Superadmin: Kindergarten Management](#4-superadmin-kindergarten-management)
5. [Superadmin: Admin Management](#5-superadmin-admin-management)
6. [Dashboard](#6-dashboard)
7. [Children](#7-children)
8. [Attendance](#8-attendance)
9. [Product Warehouse](#9-product-warehouse)
10. [Expenses](#10-expenses)
11. [Parent Payments](#11-parent-payments)
12. [Reports](#12-reports)
13. [Logout](#13-logout)

---

## 1. Getting Started

KMS runs in your browser. No installation required.

**App URL:** provided by your system administrator (Streamlit Cloud URL).

**Supported browsers:** Chrome, Firefox, Safari, Edge (current versions).

**Mobile devices:** supported.

---

## 2. Login

### First Launch (no superadmin exists)
1. Open the application in your browser
2. You will see two tabs: **Login** and **Register**
3. Go to the **Register** tab
4. Enter email and password (minimum 6 characters)
5. Click **Create Superadmin**
6. After creation, log in via the **Login** tab

### Regular Login
1. Open the application
2. Enter your email and password
3. Click **Sign In**

> **Note:** Once a superadmin is created, the Register tab disappears — new users can only be added by the superadmin.

---

## 3. Settings

### Interface Language
- Before login: select language from the dropdown in the top-left corner of the login page
- After login: sidebar → **Settings** section → select language → click **Save**

### Currency
- Same as language — select before or after login
- Available currencies: **Shekel (₪)**, **Dollar ($)**, **Euro (€)**
- All amounts in the system are displayed in the selected currency

> Settings are saved to your profile and restored on next login.

---

## 4. Superadmin: Kindergarten Management

After login, the superadmin sees the **kindergarten list**.

### Viewing Kindergartens
- Each kindergarten is shown as a card with name, address, and phone
- The **Enter →** button opens that kindergarten

### Entering a Kindergarten
1. Click **Enter →** on a kindergarten card
2. The kindergarten's main dashboard opens with full navigation
3. To return to the kindergarten list, click **← Back** at the top of the sidebar

### Adding a Kindergarten
1. In the sidebar, select **Kindergartens (⚙️)**
2. Go to the **Add Kindergarten** tab
3. Fill in: Name (required), Address, Phone, Logo URL
4. Click **Add**

### Editing a Kindergarten
1. In **Kindergartens (⚙️)** → **Kindergarten List** tab
2. Expand the target kindergarten
3. Update the fields in the edit form
4. Click **Save**

### Deleting a Kindergarten
1. In **Kindergartens (⚙️)** → find the kindergarten
2. Click **🗑 Delete «Name»**

> **Warning:** Deleting a kindergarten permanently removes ALL associated data (children, attendance, products, expenses, payments). This action cannot be undone.

### Database Initialization (Reset)
In **Kindergartens (⚙️)** there is a hidden section **🛠 Database Initialization**:
- Completely resets the database
- Creates test data (3 kindergartens with children, attendance, products, expenses, payments)
- Use only for initial setup or testing

---

## 5. Superadmin: Admin Management

In the sidebar: **👤 Administrators**

### Adding an Admin
1. **Add Administrator** tab
2. Enter email, password, and select a kindergarten
3. Click **Create**

### Viewing Admins
- List of all admins with their assigned kindergarten
- Password change and deletion are supported

> Admins can only see their own kindergarten and have no access to the admin management section.

---

## 6. Dashboard

After entering a kindergarten, the main dashboard shows:

### Alerts
- **Debtors:** if any children have incomplete payment for the current month — yellow warning with debtor count
- **Low Stock:** if any product is below minimum stock level — yellow warning with product names

### Navigation
The sidebar menu contains:
- 🏠 Home
- 👦 Children
- 📅 Attendance
- 🍎 Products
- 💰 Expenses
- 📊 Reports
- 💳 Payments
- 👤 Administrators (superadmin only)

---

## 7. Children

Section **👦 Children**

### Viewing Children
- List of children in the current kindergarten
- Filters: group (all / junior / middle / senior), status (active / inactive)
- Displays: full name, age, group, parent contact, monthly fee

### Adding a Child
1. **Add Child** tab
2. Fill in: First Name, Last Name (required), Date of Birth, Parent Name, Parent Phone, Enrollment Date, Group, Monthly Fee, Status
3. Click **Add**

### Editing a Child
1. In the children list, expand the child's card
2. Modify the required fields
3. Click **Save**

### Deactivating a Child
- Set status to **Inactive** when editing
- Inactive children are excluded from attendance and not counted as debtors

---

## 8. Attendance

Section **📅 Attendance**

### Viewing the Journal
- Select a date (defaults to today)
- Optional filter by group
- Table shows all active children and their status for the selected day

### Marking Attendance
1. Select a date
2. For each child, select a status:
   - **Present** — child attended
   - **Absent** — missed without reason
   - **Sick** — missed due to illness
3. Click **Save Attendance**

### Summary
Below the table, a summary shows:
- Number of children present
- Number absent
- Number sick

---

## 9. Product Warehouse

Section **🍎 Products**

### Viewing the Warehouse
- Product list with current stock levels
- Red indicator — stock is below minimum level

### Adding a Product
1. **Add Product** tab
2. Name, unit of measure (kg, liters, pieces, etc.), minimum stock level
3. Click **Add**

### Receiving / Consuming Stock
1. Select a product from the list
2. **Income** or **Expense** tab
3. Enter quantity and date
4. Click **Add Transaction**

### Transaction History
- Select a product — full history of receipts and consumptions is displayed

---

## 10. Expenses

Section **💰 Expenses**

### Viewing Expenses
- Filter by month and category
- Total for the selected period

### Adding an Expense
1. **Add Expense** tab
2. Date, category, amount, description (optional), comment (optional)
3. Click **Add**

**Categories:**
- Food
- Transport
- Housing
- Communications
- Other

---

## 11. Parent Payments

Section **💳 Payments**

### Adding a Payment
1. **Add Payment** tab
2. Select child, year, month
3. Enter amount and payment date
4. Click **Add**

> Multiple payments can be added for the same child and month (partial payments). The system automatically sums them when checking for debt.

### Debtor List
1. **Debtors** tab
2. Select year and month
3. List of children with debt amount (fee − total paid) is displayed

**A child is considered a debtor if:**
- Monthly fee > 0
- Sum of all payments for the month < monthly fee

### Payment History
1. **History** tab
2. Select a child — all their payments are displayed

---

## 12. Reports

Section **📊 Reports**

### Attendance Report
1. **Attendance** tab
2. Select year and month
3. Table shows: child × days of the month
4. **📥 Download Excel** button — export to file

### Financial Report
1. **Finance** tab
2. Select year and month
3. Displays:
   - Total income (sum of payments)
   - Total expenses (by category)
   - Balance (income − expenses)
4. **📥 Download Excel** button — export to file

---

## 13. Logout

At the bottom of the sidebar, click the **Sign Out** button.

The session ends; all data is saved in the database.

---

## Frequently Asked Questions

**Q: I entered a payment but the child is still showing as a debtor.**  
A: Check that the sum of all payments for the month equals or exceeds the child's monthly fee. Partial payments are summed automatically.

**Q: I can't see children from another kindergarten.**  
A: This is by design. Each admin only sees their assigned kindergarten's data.

**Q: How do I add a new admin?**  
A: Only the superadmin can add admins via the **👤 Administrators** section.

**Q: How do I change a child's monthly fee?**  
A: **👦 Children** → find the child → edit the Monthly Fee field → Save.

**Q: Can deleted data be recovered?**  
A: No. Deletions are permanent. Be careful when deleting kindergartens, children, or records.

**Q: How do I export data?**  
A: **📊 Reports** → select report type → click **📥 Download Excel**.
