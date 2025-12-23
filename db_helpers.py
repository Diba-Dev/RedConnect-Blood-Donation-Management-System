# db_helpers.py
from database import get_db_connection
from datetime import date

# -------- USERS --------
def add_user(name, email, password, blood_group, location, phone, is_admin=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, email, password, blood_group, location, phone, is_admin)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, email, password, blood_group, location, phone, is_admin))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def set_user_donor_status(user_id, is_donor):
    """
    Toggle donor status (requires `is_donor` column in users table)
    """
    conn = get_db_connection()
    conn.execute("UPDATE users SET is_donor = ? WHERE id = ?", (is_donor, user_id))
    conn.commit()
    conn.close()


# -------- REQUESTS --------
def add_request(user_id, blood_group, location, units, message=None):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO blood_requests (user_id, blood_group, location, units, message, status, request_date) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
        (user_id, blood_group, location, units, message, "Pending")
    )
    conn.commit()
    conn.close()

def get_requests_by_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM blood_requests WHERE user_id = ? ORDER BY request_date DESC
    """, (user_id,))
    requests = cursor.fetchall()
    conn.close()
    return requests

def get_all_requests():
    conn = get_db_connection()
    requests = conn.execute("SELECT * FROM blood_requests ORDER BY request_date DESC").fetchall()
    conn.close()
    return requests

def update_request_status(request_id, status):
    """
    Update the status of a blood request (Approved / Rejected)
    """
    conn = get_db_connection()
    conn.execute(
        "UPDATE blood_requests SET status = ? WHERE id = ?",
        (status, request_id)
    )
    conn.commit()
    conn.close()


# -------- DONATIONS --------
def add_donation(user_id, blood_group, donation_type, donation_date, notes=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO donations (user_id, blood_group, donation_type, donation_date, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, blood_group, donation_type, donation_date, notes))
    conn.commit()
    conn.close()

def get_donations_by_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM donations WHERE user_id = ? ORDER BY donation_date DESC
    """, (user_id,))
    donations = cursor.fetchall()
    conn.close()
    return donations


# -------- STOCK --------
def get_all_stock():
    conn = get_db_connection()
    stock = conn.execute("SELECT * FROM blood_stock ORDER BY blood_group ASC").fetchall()
    conn.close()
    return stock


def update_stock_units(stock_id, units):
    conn = get_db_connection()
    conn.execute("UPDATE blood_stock SET units = ? WHERE id = ?", (units, stock_id))
    conn.commit()
    conn.close()


# Total pending requests
def get_total_pending_requests():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM blood_requests WHERE status='Pending'")
    result = cursor.fetchone()
    conn.close()
    return result["count"]

# Total donors
def get_total_donors():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_donor=1")
    result = cursor.fetchone()
    conn.close()
    return result["count"]

# Active donors today (optional: define active as donated today)
def get_active_donors_today():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT user_id) as count FROM donations WHERE donation_date=CURRENT_DATE")
    result = cursor.fetchone()
    conn.close()
    return result["count"]

def add_stock(blood_group, units, location):
    """
    Add new stock or update existing stock for blood_group + location
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if stock already exists
    existing = cursor.execute(
        "SELECT * FROM blood_stock WHERE blood_group = ? AND location = ?",
        (blood_group, location)
    ).fetchone()

    if existing:
        # If exists, update units
        new_units = existing["units"] + int(units)
        cursor.execute(
            "UPDATE blood_stock SET units = ?, last_updated = CURRENT_DATE WHERE id = ?",
            (new_units, existing["id"])
        )
    else:
        # Else, insert new stock
        cursor.execute(
            "INSERT INTO blood_stock (blood_group, units, location) VALUES (?, ?, ?)",
            (blood_group, units, location)
        )

    conn.commit()
    conn.close()

# Add new stock
def add_stock(blood_group, units, location):
    conn = get_db_connection()
    # Check if stock already exists for this blood_group + location
    existing = conn.execute(
        "SELECT * FROM blood_stock WHERE blood_group=? AND location=?",
        (blood_group, location)
    ).fetchone()
    if existing:
        # If exists, just update units
        new_units = existing["units"] + int(units)
        conn.execute("UPDATE blood_stock SET units=? WHERE id=?", (new_units, existing["id"]))
    else:
        conn.execute(
            "INSERT INTO blood_stock (blood_group, units, location) VALUES (?, ?, ?)",
            (blood_group, units, location)
        )
    conn.commit()
    conn.close()

# Search stock by blood group and optionally location
def search_stock(blood_group=None, location=None):
    conn = get_db_connection()
    query = "SELECT * FROM blood_stock WHERE 1=1"
    params = []
    if blood_group:
        query += " AND blood_group=?"
        params.append(blood_group)
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    query += " ORDER BY blood_group ASC"
    stock = conn.execute(query, params).fetchall()
    conn.close()
    return stock

# Update user info
def update_user_profile(user_id, name, email, phone, blood_group, location):
    conn = get_db_connection()
    conn.execute("""
        UPDATE users
        SET name = ?, email = ?, phone = ?, blood_group = ?, location = ?
        WHERE id = ?
    """, (name, email, phone, blood_group, location, user_id))
    conn.commit()
    conn.close()


# Toggle donor status
def set_user_donor_status(user_id, is_donor):
    conn = get_db_connection()
    conn.execute("UPDATE users SET is_donor=? WHERE id=?", (1 if is_donor else 0, user_id))
    conn.commit()
    conn.close()

def toggle_admin_status(user_id):
    conn = get_db_connection()
    user = conn.execute(
        "SELECT is_admin FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    if user:
        new_status = 0 if user["is_admin"] else 1
        conn.execute(
            "UPDATE users SET is_admin = ? WHERE id = ?",
            (new_status, user_id)
        )
        conn.commit()
    conn.close()
def delete_user_by_id(user_id):
    conn = get_db_connection()

    # Delete related data first (IMPORTANT)
    conn.execute("DELETE FROM blood_requests WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM donations WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

    conn.commit()
    conn.close()


# -------- NOTIFICATIONS --------
def add_notification(user_id, title, message, n_type="info", admin_name=None, admin_phone=None):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO notifications (user_id, title, message, type, admin_name, admin_phone)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, title, message, n_type, admin_name, admin_phone))
    conn.commit()
    conn.close()


def get_notifications_by_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM notifications
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    notifications = cursor.fetchall()
    conn.close()
    return notifications


# -------- PUBLIC SEARCH --------
def search_blood_stock(blood_group, location=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if location:
        cursor.execute("""
            SELECT blood_group, units, location
            FROM blood_stock
            WHERE blood_group = ?
            AND location LIKE ?
            AND units > 0
        """, (blood_group, f"%{location}%"))
    else:
        cursor.execute("""
            SELECT blood_group, units, location
            FROM blood_stock
            WHERE blood_group = ?
            AND units > 0
        """, (blood_group,))

    results = cursor.fetchall()
    conn.close()
    return results


from database import get_db_connection
from datetime import datetime

# -----------------------------
# Admin: search users
# -----------------------------
def search_users(blood_group=None, location=None, limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            u.id,
            u.name,
            u.phone,
            u.blood_group,
            u.location,
            u.is_admin,
            u.is_donor,
            MAX(d.donation_date) AS last_donation
        FROM users u
        LEFT JOIN donations d ON u.id = d.user_id
        WHERE 1=1
    """
    params = []

    if blood_group and blood_group.strip():
        query += " AND u.blood_group = ?"
        params.append(blood_group.strip())

    if location and location.strip():
        query += " AND u.location LIKE ?"
        params.append(f"%{location.strip()}%")

    query += """
        GROUP BY u.id
        ORDER BY last_donation DESC
        LIMIT ?
    """
    params.append(limit)

    cursor.execute(query, params)
    users = cursor.fetchall()
    conn.close()

    return users




# -----------------------------
# Calculate donation eligibility
# -----------------------------
def calculate_eligibility(last_donation):
    if not last_donation:
        return {
            "eligible": True,
            "message": "Available"
        }

    last_date = datetime.strptime(last_donation, "%Y-%m-%d")
    days_passed = (datetime.now() - last_date).days

    if days_passed >= 90:
        return {
            "eligible": True,
            "message": "Available"
        }
    else:
        return {
            "eligible": False,
            "message": f"Next donation in {90 - days_passed} days"
        }

from database import get_db_connection

def get_total_users():
    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"]
    conn.close()
    return count

def get_total_blood_units():
    conn = get_db_connection()
    total = conn.execute("SELECT SUM(units) AS total_units FROM blood_stock").fetchone()["total_units"]
    conn.close()
    return total or 0

def get_total_locations():
    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(DISTINCT location) AS total_locations FROM blood_stock").fetchone()["total_locations"]
    conn.close()
    return count

