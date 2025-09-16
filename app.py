import qrcode
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'internship_db' 

mysql = MySQL(app)

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM admins WHERE username = %s", ("admin",))
    existing = cur.fetchone()
    if not existing:
        hashed_password = generate_password_hash("admin123")  # default password
        cur.execute(
            "INSERT INTO admins (username, password) VALUES (%s, %s)",
            ("admin", hashed_password)
        )
        mysql.connection.commit()
        print("✅ Default admin created (username=admin, password=admin123)")
    else:
        print("ℹ️ Admin already exists, skipping insert")
    cur.close()

# Login required decorator
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def verify_page():
    details = None
    if request.method == 'POST':
        emp_id = request.form.get('emp_id')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM interns WHERE emp_id = %s", (emp_id,))
        data = cur.fetchone()
        cur.close()
        if data:
            details = {
                'emp_id': data[0],
                'student_name': data[1],
                'domain': data[2],
                'duration': data[3],
                'start_date': data[4],
                'award_date': data[5],
                'photo': data[6]
            }
        else:
            flash("No record found.")
    return render_template('verify.html', details=details)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admins WHERE username = %s", (username,))
        admin = cur.fetchone()
        cur.close()

        if admin and check_password_hash(admin[2], password):
            session['admin_username'] = username
            return redirect(url_for('admin'))
        else:
            flash("Invalid credentials")
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('admin_username', None)
    return redirect(url_for('login'))


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        domain = request.form.get('domain')
        duration = request.form.get('duration')
        start_date = request.form.get('start_date')
        award_date = request.form.get('award_date')
        photo_file = request.files.get('photo')

        emp_id = os.urandom(4).hex().upper()  # 8 char employee ID
        filename = emp_id + "_" + photo_file.filename
        photo_file.save(os.path.join('static/photos', filename))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO interns (emp_id, student_name, domain, duration, start_date, award_date, photo) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (emp_id, student_name, domain, duration, start_date, award_date, filename))
        mysql.connection.commit()
        cur.close()

        # ✅ QR Code generate karo
        qr_img = qrcode.make(emp_id)
        qr_filename = emp_id + ".png"
        qr_path = os.path.join("static/qr_codes", qr_filename)
        qr_img.save(qr_path)

        flash(f"Intern added successfully! Employee ID: {emp_id}")
        return redirect(url_for('success', emp_id=emp_id))   # Success page pe bhej do
    return render_template('admin.html')


# ✅ Success route with QR code
@app.route('/success')
def success():
    emp_id = request.args.get("emp_id")
    qr_filename = emp_id + ".png"
    return render_template("success.html", emp_id=emp_id, qr_filename=qr_filename)


if __name__ == '__main__':

    app.run(debug=True)
