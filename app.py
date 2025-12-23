# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db, get_db_connection
from db_helpers import (
    add_user, get_user_by_email, update_stock_units,
    add_request, get_requests_by_user, add_donation, get_donations_by_user,
    add_notification, get_all_requests, get_user_by_id,
    get_total_pending_requests, get_total_donors, get_active_donors_today,
    search_users, calculate_eligibility, get_all_stock, add_stock,
    search_stock, update_request_status,
    get_total_users, get_total_blood_units, get_total_locations,
    set_user_donor_status, update_user_profile, get_notifications_by_user, search_blood_stock, delete_user_by_id, toggle_admin_status
)

from datetime import datetime
from functools import wraps

# -----------------------------
# Flask App Initialization
# -----------------------------
app = Flask(__name__)
app.secret_key = "fiuageroisdtgqoiwogg8g" 

init_db()

# -----------------------------
# Decorators
# -----------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please login to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Access denied. Admins only.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# -----------------------------
# FRONTEND ROUTES
# -----------------------------
@app.route("/")
def index():
    total_users = get_total_users()
    total_units = get_total_blood_units()
    total_locations = get_total_locations()

    return render_template(
        "index.html",
        total_users=total_users,
        total_units=total_units,
        total_locations=total_locations
    )


@app.route("/admin/toggle-admin/<int:user_id>", methods=["POST"])
def toggle_admin(user_id):
    if not session.get("is_admin"):
        flash("Unauthorized", "error")
        return redirect(url_for("login"))

    if user_id == session.get("user_id"):
        flash("You cannot change your own admin role.", "error")
        return redirect(url_for("admin_user"))

    toggle_admin_status(user_id)
    flash("Admin role updated successfully!", "success")
    return redirect(url_for("admin_user"))
@app.route("/admin/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if not session.get("is_admin"):
        flash("Unauthorized", "error")
        return redirect(url_for("login"))

    if user_id == session.get("user_id"):
        flash("You cannot delete your own account.", "error")
        return redirect(url_for("admin_user"))

    delete_user_by_id(user_id)
    flash("User deleted successfully!", "success")
    return redirect(url_for("admin_user"))


@app.route("/search", methods=["GET"])
def search():
    blood_group = request.args.get("blood_group")
    location = request.args.get("location")
    results = []

    if blood_group:
        results = search_blood_stock(blood_group, location)

    return render_template("search.html", results=results)

@app.route("/user_requests")
@login_required
def user_requests():
    requests = get_requests_by_user(session["user_id"])
    return render_template("user_requests.html", requests=requests)

@app.route("/new_request", methods=["GET", "POST"])
@login_required
def new_request():
    if request.method == "POST":
        blood_group = request.form["blood_group"]
        location = request.form["location"]
        units = int(request.form["units"])
        message = request.form.get("message")
        add_request(session["user_id"], blood_group, location, units, message)
        flash("Blood request submitted successfully!", "success")
        return redirect(url_for("user_requests"))

    return render_template("new_request.html")

@app.route("/donate_blood", methods=["GET", "POST"])
@login_required
def donate_blood():
    if request.method == "POST":
        blood_group = request.form["blood_group"]
        donation_type = request.form["donation_type"]
        donation_date = request.form["donation_date"]
        notes = request.form.get("notes")
        add_donation(session["user_id"], blood_group, donation_type, donation_date, notes)
        flash("Thank you for your donation!", "success")
        return redirect(url_for("profile"))

    return render_template("donate_blood.html")

# -----------------------------
# ADMIN ROUTES
# -----------------------------
@app.route("/dashboard_admin")
@admin_required
def dashboard_admin():
    all_requests = get_all_requests()
    top_requests = all_requests[:10]

    requests_with_user = []
    for r in top_requests:
        user = get_user_by_id(r["user_id"])
        requests_with_user.append({
            "id": r["id"],
            "user_name": user["name"] if user else "Unknown",
            "blood_group": r["blood_group"],
            "units": r["units"],
            "location": r["location"],
            "status": r["status"],
            "request_date": r["request_date"],
            "contact": user["phone"] if user else "-"
        })

    return render_template(
        "dashboard_admin.html",
        requests=requests_with_user,
        total_requests=len(all_requests),
        pending_requests=get_total_pending_requests(),
        total_donors=get_total_donors(),
        active_donors_today=get_active_donors_today()
    )

@app.route("/admin_user", methods=["GET"])
@admin_required
def admin_user():
    blood_group = request.args.get("blood_group")
    location = request.args.get("location")

    users = search_users(blood_group, location)
    processed_users = []

    for u in users:
        eligibility = calculate_eligibility(u["last_donation"])
        processed_users.append({
            "id": u["id"],                 
            "name": u["name"],
            "phone": u["phone"],
            "blood_group": u["blood_group"],
            "is_donor": u["is_donor"],
            "is_admin": u["is_admin"],     
            "last_donation": u["last_donation"],
            "eligibility": eligibility,
            "location": u["location"]
        })


    return render_template("admin_user.html", users=processed_users)

@app.route("/stock", methods=["GET", "POST"])
@admin_required
def stock():
    if request.method == "POST":
        stock_id = request.form.get("stock_id")
        blood_group = request.form.get("blood_group")
        units = request.form.get("units")
        location = request.form.get("location")

        if stock_id:
            update_stock_units(stock_id, units)
            flash("Stock updated successfully!", "success")
        elif blood_group and units and location:
            add_stock(blood_group, units, location)
            flash("Stock added successfully!", "success")
        return redirect(url_for("stock"))

    blood_group_filter = request.args.get("blood_group")
    location_filter = request.args.get("location")
    stock = search_stock(blood_group_filter, location_filter) if blood_group_filter or location_filter else get_all_stock()

    return render_template("stock.html", stock=stock)

@app.route("/approve_request/<int:request_id>", methods=["POST"])
@admin_required
def approve_request(request_id):
    update_request_status(request_id, "Approved")

    conn = get_db_connection()
    req = conn.execute("SELECT * FROM blood_requests WHERE id = ?", (request_id,)).fetchone()
    conn.close()

    if not req:
        flash("Request not found", "error")
        return redirect(url_for("dashboard_admin"))

    user = get_user_by_id(req["user_id"])
    admin_name = session.get("user_name", "RedConnect Admin")
    session["contact"] = user["phone"]
    print("session[\"contact\"]:", session["contact"])
    admin_phone = session.get("contact", "012345678910")

    add_notification(
        user_id=user["id"],
        title="Blood Request Approved",
        message=f"Your request for {req['units']} unit(s) of {req['blood_group']} blood has been approved.",
        n_type="approved",
        admin_name=admin_name,
        admin_phone=admin_phone
    )

    flash("Request approved & user notified!", "success")
    return redirect(url_for("dashboard_admin"))

@app.route("/reject_request/<int:request_id>", methods=["POST"])
@admin_required
def reject_request(request_id):
    update_request_status(request_id, "Rejected")
    flash("Request rejected!", "info")
    return redirect(url_for("dashboard_admin"))

# -----------------------------
# AUTHENTICATION
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        flash("You are already logged in.", "info")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        blood_group = request.form.get("blood_group")
        location = request.form.get("location")
        phone = request.form.get("phone")

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("register"))

        if get_user_by_email(email):
            flash("Email already registered", "error")
            return redirect(url_for("register"))

        add_user(name, email, password, blood_group, location, phone)
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        flash("You are already logged in.", "info")
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = get_user_by_email(email)

        if user and user["password"] == password:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["contact"] = user["phone"]
            session["is_admin"] = user["is_admin"]
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("index"))

# -----------------------------
# PROFILE
# -----------------------------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    user = get_user_by_id(user_id)

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        blood_group = request.form["blood_group"]
        location = request.form["location"]

        update_user_profile(user_id, name, email, phone, blood_group, location)
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    donations = get_donations_by_user(user_id)
    notifications = get_notifications_by_user(user_id)

    return render_template(
        "profile.html",
        user=user,
        donations=donations[:2],
        notifications=notifications
    )

@app.route("/toggle_donor", methods=["POST"])
@login_required
def toggle_donor():
    user_id = session["user_id"]
    is_donor = request.form.get("is_donor") == "on"
    set_user_donor_status(user_id, is_donor)
    flash("Donor status updated!", "success")
    return redirect(url_for("profile"))

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
