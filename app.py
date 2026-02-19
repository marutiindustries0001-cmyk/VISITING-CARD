import io
import base64
import qrcode
import sqlite3
import os
from flask import Flask, render_template_string, request, Response, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "seth_koyeb_premium_key"

# ================= DATABASE SETUP =================
def init_db():
    conn = sqlite3.connect('mobile_card.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY, password TEXT, name TEXT, phone TEXT, 
        address TEXT, location TEXT, logo TEXT, services TEXT,
        instagram TEXT, linkedin TEXT, whatsapp TEXT)''')
    
    cursor.execute("SELECT * FROM users WHERE email='seth@gmail.com'")
    if not cursor.fetchone():
        cursor.execute("""INSERT INTO users VALUES (
            'seth@gmail.com', '123', 'Seth Saawaliya', '+91 9876543210', 
            'Indore, MP', 'https://maps.google.com', 
            'https://cdn-icons-png.flaticon.com/512/3135/3135715.png', 
            'Trading Bot & AI Specialist',
            'https://instagram.com', 'https://linkedin.com', '919876543210')""")
    conn.commit()
    conn.close()

init_db()

# ================= MOBILE-FIRST UI DESIGN =================
MOBILE_STYLE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #4F46E5; --bg: #F3F4F6; --card: #FFFFFF; }
        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { background-color: var(--bg); font-family: 'Inter', sans-serif; color: #1F2937; }
        .mobile-container { width: 100%; max-width: 480px; margin: 0 auto; min-height: 100vh; background: var(--bg); position: relative; padding-bottom: 40px; }
        .header-bg { background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); height: 160px; width: 100%; border-radius: 0 0 40px 40px; }
        .profile-card { background: var(--card); margin: -80px 20px 20px 20px; border-radius: 24px; padding: 25px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; }
        .avatar { width: 100px; height: 100px; border-radius: 50%; border: 4px solid #FFF; margin-top: -75px; object-fit: cover; background: white; }
        h1 { font-size: 22px; font-weight: 700; margin: 15px 0 5px; }
        .services { font-size: 14px; color: #6B7280; margin-bottom: 20px; }
        .social-row { display: flex; justify-content: center; gap: 15px; margin-bottom: 25px; }
        .social-row a { width: 45px; height: 45px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; color: white; text-decoration: none; }
        .insta { background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fdf497 5%, #fd5949 45%, #d6249f 60%, #285AEB 90%); }
        .linkd { background: #0077b5; }
        .watsp { background: #25D366; }
        .btn { width: 100%; padding: 16px; border-radius: 16px; font-weight: 600; font-size: 15px; display: flex; align-items: center; justify-content: center; gap: 10px; text-decoration: none; margin-bottom: 12px; transition: 0.2s; }
        .btn-primary { background: var(--primary); color: white; }
        .btn-outline { background: white; color: var(--primary); border: 2px solid var(--primary); }
        .qr-card { background: white; margin: 0 20px; border-radius: 24px; padding: 20px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        input { width: 100%; padding: 14px; margin-bottom: 12px; border: 1px solid #D1D5DB; border-radius: 12px; font-size: 16px; }
    </style>
    <title>{{ title }}</title>
</head>
<body>
    <div class="mobile-container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

# ================= ROUTES =================

@app.route('/card/<email>')
def view_card(email):
    conn = sqlite3.connect('mobile_card.db'); conn.row_factory = sqlite3.Row
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone(); conn.close()
    if not user: return "Profile Not Found", 404

    qr = qrcode.make(request.url)
    buf = io.BytesIO(); qr.save(buf)
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template_string(MOBILE_STYLE, title=user['name'], content=f"""
        <div class="header-bg"></div>
        <div class="profile-card">
            <img src="{user['logo']}" class="avatar">
            <h1>{user['name']}</h1>
            <p class="services">{user['services']}</p>
            <div class="social-row">
                <a href="{user['instagram']}" target="_blank" class="insta"><i class="fab fa-instagram"></i></a>
                <a href="{user['linkedin']}" target="_blank" class="linkd"><i class="fab fa-linkedin-in"></i></a>
                <a href="https://wa.me/{user['whatsapp']}" target="_blank" class="watsp"><i class="fab fa-whatsapp"></i></a>
            </div>
            <a href="/download_vcf/{email}" class="btn btn-primary"><i class="fas fa-user-plus"></i> Save Contact</a>
            <a href="{user['location']}" target="_blank" class="btn btn-outline"><i class="fas fa-location-arrow"></i> Directions</a>
        </div>
        <div class="qr-card">
            <img src="data:image/png;base64,{qr_b64}" style="width:140px;">
            <p style="font-size:12px; color:#9CA3AF; margin-top:10px;">Scan to exchange details</p>
        </div>
        <center><a href="/login" style="color:#9CA3AF; text-decoration:none; font-size:12px; margin-top:20px; display:block;">Admin Login</a></center>
    """)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect('mobile_card.db')
        user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (request.form['email'], request.form['password'])).fetchone()
        conn.close()
        if user: session['user'] = request.form['email']; return redirect(url_for('dashboard'))
        return "Invalid Login"
    return render_template_string(MOBILE_STYLE, title="Login", content="""
        <div class="header-bg" style="height:100px;"></div>
        <div class="profile-card">
            <h2>Admin Login</h2><br>
            <form method="POST">
                <input name="email" type="email" placeholder="Email" required>
                <input name="password" type="password" placeholder="Password" required>
                <button type="submit" class="btn btn-primary">Sign In</button>
            </form>
        </div>
    """)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect('mobile_card.db'); conn.row_factory = sqlite3.Row
    if request.method == 'POST':
        conn.execute("UPDATE users SET name=?, phone=?, address=?, location=?, logo=?, services=?, instagram=?, linkedin=?, whatsapp=? WHERE email=?",
                   (request.form['name'], request.form['phone'], request.form['address'], request.form['location'], 
                    request.form['logo'], request.form['services'], request.form['instagram'], request.form['linkedin'], request.form['whatsapp'], session['user']))
        conn.commit(); conn.close()
        return redirect(url_for('view_card', email=session['user']))
    user = conn.execute("SELECT * FROM users WHERE email=?", (session['user'],)).fetchone(); conn.close()
    return render_template_string(MOBILE_STYLE, title="Dashboard", content=f"""
        <div class="header-bg" style="height:80px;"></div>
        <div class="profile-card">
            <h3>Update Card</h3><br>
            <form method="POST">
                <input name="name" value="{user['name']}" placeholder="Name">
                <input name="phone" value="{user['phone']}" placeholder="Phone">
                <input name="whatsapp" value="{user['whatsapp']}" placeholder="WhatsApp No">
                <input name="instagram" value="{user['instagram']}" placeholder="Instagram Link">
                <input name="linkedin" value="{user['linkedin']}" placeholder="LinkedIn Link">
                <input name="location" value="{user['location']}" placeholder="Maps Link">
                <input name="logo" value="{user['logo']}" placeholder="Logo URL">
                <input name="services" value="{user['services']}" placeholder="About You">
                <button type="submit" class="btn btn-primary">Update Profile</button>
            </form>
            <a href="/logout" style="color:red; font-size:12px; display:block; margin-top:10px;">Logout</a>
        </div>
    """)

@app.route('/download_vcf/<email>')
def download_vcf(email):
    conn = sqlite3.connect('mobile_card.db'); conn.row_factory = sqlite3.Row
    u = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone(); conn.close()
    vcf = f"BEGIN:VCARD\\nVERSION:3.0\\nFN:{u['name']}\\nTEL:{u['phone']}\\nEMAIL:{u['email']}\\nEND:VCARD"
    return Response(vcf, mimetype="text/vcard", headers={"Content-disposition": f"attachment; filename={u['name']}.vcf"})

@app.route('/logout')
def logout():
    session.pop('user', None); return redirect(url_for('login'))

# ================= KOYEB DEPLOYMENT LINE =================
if __name__ == '__main__':
    # Koyeb automatic PORT select karega, agar nahi mila toh 8000 use karega
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
