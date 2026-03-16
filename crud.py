import sqlite3
from database import get_connection

# --- ТАБЛИЦА: children ---

def add_child(first_name, last_name, birth_date, parent_name, parent_phone, enrollment_date, status='активный'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO children (first_name, last_name, birth_date, parent_name, parent_phone, enrollment_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (first_name, last_name, birth_date, parent_name, parent_phone, enrollment_date, status))
    conn.commit()
    conn.close()

def get_all_children():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM children ORDER BY last_name, first_name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_child(child_id, first_name, last_name, birth_date, parent_name, parent_phone, enrollment_date, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE children 
        SET first_name=?, last_name=?, birth_date=?, parent_name=?, parent_phone=?, enrollment_date=?, status=?
        WHERE id=?
    ''', (first_name, last_name, birth_date, parent_name, parent_phone, enrollment_date, status, child_id))
    conn.commit()
    conn.close()

def delete_child(child_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM children WHERE id=?", (child_id,))
    conn.commit()
    conn.close()


# --- ТАБЛИЦА: attendance ---

def add_attendance(child_id, date, status):
    conn = get_connection()
    cursor = conn.cursor()
    # Check if record already exists for this date, if so, update
    cursor.execute("SELECT id FROM attendance WHERE child_id=? AND date=?", (child_id, date))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE attendance SET status=? WHERE id=?", (status, row['id']))
    else:
        cursor.execute("INSERT INTO attendance (child_id, date, status) VALUES (?, ?, ?)", (child_id, date, status))
    conn.commit()
    conn.close()

def get_attendance_by_date(date):
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT a.id, a.child_id, a.date, a.status, c.first_name, c.last_name 
        FROM attendance a
        JOIN children c ON a.child_id = c.id
        WHERE a.date = ?
    '''
    cursor.execute(query, (date,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
    
def get_all_attendance():
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT a.id, a.child_id, a.date, a.status, c.first_name, c.last_name 
        FROM attendance a
        JOIN children c ON a.child_id = c.id
        ORDER BY a.date DESC
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# --- ТАБЛИЦА: products ---

def add_product(name, unit, min_stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, unit, min_stock) VALUES (?, ?, ?)", (name, unit, min_stock))
    conn.commit()
    conn.close()

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()


# --- ТАБЛИЦА: product_income ---

def add_product_income(product_id, date, quantity, price, supplier):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO product_income (product_id, date, quantity, price, supplier) 
        VALUES (?, ?, ?, ?, ?)
    ''', (product_id, date, quantity, price, supplier))
    conn.commit()
    conn.close()


# --- ТАБЛИЦА: product_expense ---

def add_product_expense(product_id, date, quantity, purpose):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO product_expense (product_id, date, quantity, purpose) 
        VALUES (?, ?, ?, ?)
    ''', (product_id, date, quantity, purpose))
    conn.commit()
    conn.close()

def get_product_inventory():
    conn = get_connection()
    cursor = conn.cursor()
    # Calculate real-time stock = Income - Expense
    query = '''
        SELECT 
            p.id, p.name, p.unit, p.min_stock,
            COALESCE((SELECT SUM(quantity) FROM product_income WHERE product_id = p.id), 0) as total_income,
            COALESCE((SELECT SUM(quantity) FROM product_expense WHERE product_id = p.id), 0) as total_expense
        FROM products p
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    
    inventory = []
    for row in rows:
        r = dict(row)
        r['current_stock'] = r['total_income'] - r['total_expense']
        r['is_low_stock'] = r['current_stock'] <= r['min_stock']
        inventory.append(r)
        
    conn.close()
    return inventory


# --- ТАБЛИЦА: expenses ---

def add_expense(date, category, description, amount, comment):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (date, category, description, amount, comment) 
        VALUES (?, ?, ?, ?, ?)
    ''', (date, category, description, amount, comment))
    conn.commit()
    conn.close()

def get_all_expenses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()
