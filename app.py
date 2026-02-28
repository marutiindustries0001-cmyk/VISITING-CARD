import io
import base64
import qrcode
import os
import sys
from flask import Flask, render_template_string, request, Response, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId

# =================================================
# FLASK APP CONFIGURATION
# =================================================
app = Flask(__name__)
app.secret_key = os.urandom(24)

# =================================================
# DATABASE CONNECTION (MONGODB)
# =================================================
# YAHAN APNA PASSWORD BHAREIN (No special chars like @ or #)
MONGO_URI = "mongodb+srv://myvisitingcard01:APNA_PASSWORD_YAHAN@cluster0.ydu8lor.mongodb.net/?appName=Cluster0&tlsAllowInvalidCertificates=true"

try:
    # Render ke liye timeout badha diya gaya hai
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=30000, connectTimeoutMS=30000)
    db = client['vcard_db']
    users_col = db['users']
    client.admin.command('ping')
    print("✅ DATABASE: Connected Successfully")
except Exception as e:
    print(f"❌ DATABASE ERROR: {e}")
    users_col = None

# Admin Setup Function
def ensure_admin():
    if users_col is not None:
        try:
            admin_exists = users_col.find_one({"role": "admin"})
            if not admin_exists:
                users_col.insert_one({
                    "email": "admin@maruti.com",
                    "password": "admin786",
                    "name": "Master Admin",
                    "role": "admin",
                    "business_name": "Maruti Industries Admin",
                    "phone": "9100000000",
                    "whatsapp": "9100000000",
                    "logo": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                    "services": "Administrator Account",
                    "products": "",
                    "instagram": "#",
                    "location": "#"
                })
                print("✅ ADMIN: Default admin created")
        except Exception as e:
            print(f"❌ SETUP ERROR: {e}")

# =================================================
# UI DESIGN (CSS & HTML)
# =================================================
UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #0f172a; --accent: #3b82f6; --bg: #f1f5f9; --white: #ffffff; }
        * { margin:0; padding:0; box-sizing:border-box; font-family: 'Poppins', sans-serif; }
        body { background: #cbd5e1; display: flex; justify-content: center; min-height: 100vh; }
        .app-container { width: 100%; max-width: 480px; background: var(--bg); min-height: 100vh; box-shadow: 0 0 30px rgba(0,0,0,0.2); position: relative; }
        
        /* Header & Profile Section */
        .header-banner { background: linear-gradient(135deg, #1e293b, #0f172a); height: 200px; border-radius: 0 0 40px 40px; position: relative; }
        .profile-container { position: absolute; bottom: -55px; left: 50%; transform: translateX(-50%); text-align: center; width: 100%; }
        .profile-img { width: 120px; height: 120px; border-radius: 50%; border: 5px solid white; object-fit: cover; background: white; box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
        
        /* Content Area */
        .card-content { margin-top: 70px; padding: 20px; text-align: center; }
        .user-name { font-size: 24px; font-weight: 700; color: var(--primary); }
        .biz-label { font-size: 14px; color: var(--accent); font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
        .user-bio { font-size: 13px; color: #64748b; line-height: 1.5; margin-bottom: 20px; }
        
        /* Buttons */
        .action-btns { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 25px; }
        .btn { padding: 14px; border-radius: 12px; font-weight: 600; font-size: 14px; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 8px; border: none; transition: 0.3s; cursor: pointer; }
        .btn-main { background: var(--accent); color: white; grid-column: span 2; box-shadow: 0 5px 15px rgba(59,130,246,0.3); }
        .btn-sub { background: white; color: var(--primary); border: 2px solid #e2e8f0; }
        
        /* Social Icons */
        .social-row { display: flex; justify-content: center; gap: 15px; margin-bottom: 25px; }
        .social-btn { width: 45px; height: 45px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: var(--primary); font-size: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-decoration: none; }
        
        /* Products Gallery */
        .section-title { text-align: left; font-size: 16px; font-weight: 700; color: var(--primary); margin: 20px 0 10px; border-left: 4px solid var(--accent); padding-left: 10px; }
        .product-scroll { display: flex; overflow-x: auto; gap: 12px; padding-bottom: 15px; }
        .product-item { min-width: 180px; background: white; border-radius: 15px; overflow: hidden; border: 1px solid #eee; }
        .product-img { width: 100%; height: 120px; object-fit: cover; }
        
        /* QR Section */
        .qr-box { background: white; padding: 20px; border-radius: 20px; display: inline-block; margin-top: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }
        .qr-image { width: 160px; height: 160px; }

        /* Form Controls */
        .form-area { padding: 20px; text-align: left; }
        .field { margin-bottom: 15px; }
        .field label { display: block; font-size: 12px; font-weight: 600; color: #64748b; margin-bottom: 5px; }
        input, textarea { width: 100%; padding: 12px; border: 2px solid #e2e8f0; border-radius: 10px; background: #f8fafc; font-size: 14px; }
        input:focus { border-color: var(--accent); outline: none; }
    </style>
    <title>{{ title }}</title>
</head>
<body>
    <div class="app-container">{% block content %}{% endblock %}</div>
</body>
</html>
"""

# =================================================
# MAIN ROUTES
# =================================================

@app.route('/')
def home():
    ensure_admin()
    return redirect(url_for('login'))

@app.route('/card/<email>')
def view_card(email):
    user = users_col.find_one({"email": email}) if users_col else None
    if not user:
        return "<h1>User Not Found</h1>", 404
    
    # 1. UNIQUE QR GENERATION
    card_url = request.url_root.rstrip('/') + url_for('view_card', email=email)
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(card_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf)
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    # 2. GALLERY LOGIC
    gallery_html = ""
    if user.get('products'):
        for p_url in user['products'].split(','):
            if p_url.strip():
                gallery_html += f'<div class="product-item"><img src="{p_url.strip()}" class="product-img"></div>'

    return render_template_string(UI_TEMPLATE, title=user['name'], content=f"""
        <div class="header-banner"><div class="profile-container"><img src="{user.get('logo', 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png')}" class="profile-img"></div></div>
        <div class="card-content">
            <h1 class="user-name">{user['name']}</h1>
            <p class="biz-label">{user.get('business_name', 'Maruti Industries')}</p>
            <p class="user-bio">{user.get('services', 'Digital Visiting Card')}</p>
            
            <div class="social-row">
                <a href="tel:{user.get('phone', '')}" class="social-btn"><i class="fas fa-phone"></i></a>
                <a href="https://wa.me/{user.get('whatsapp', '')}" class="social-btn"><i class="fab fa-whatsapp"></i></a>
                <a href="{user.get('instagram', '#')}" class="social-btn"><i class="fab fa-instagram"></i></a>
                <a href="{user.get('location', '#')}" class="social-btn"><i class="fas fa-map-marker-alt"></i></a>
            </div>

            <div class="action-btns">
                <a href="/download_vcf/{email}" class="btn btn-main"><i class="fas fa-user-plus"></i> SAVE TO CONTACTS</a>
                <a href="mailto:{user['email']}" class="btn btn-sub"><i class="fas fa-envelope"></i> EMAIL</a>
                <a href="https://wa.me/{user.get('whatsapp', '')}?text=Hi" class="btn btn-sub"><i class="fab fa-whatsapp"></i> CHAT</a>
            </div>

            <h3 class="section-title">Product Showcase</h3>
            <div class="product-scroll">{gallery_html if gallery_html else 'No products added'}</div>

            <h3 class="section-title">Unique Scan QR</h3>
            <div class="qr-box">
                <img src="data:image/png;base64,{qr_b64}" class="qr-image">
                <p style="font-size:10px; color:#94a3b8; margin-top:8px;">Scan to share this card</p>
            </div>
        </div>
    """)

@app.route('/login', methods=['GET', 'POST'])
def login():
    ensure_admin()
    error = ""
    if request.method == 'POST':
        u = users_col.find_one({"email": request.form['email'], "password": request.form['password']}) if users_col else None
        if u:
            session['uid'] = u['email']
            session['role'] = u.get('role', 'user')
            return redirect(url_for('dashboard'))
        error = "Invalid Credentials!"

    return render_template_string(UI_TEMPLATE, title="Login", content=f"""
        <div style="padding:60px 30px; text-align:center;">
            <i class="fas fa-user-circle" style="font-size:60px; color:#3b82f6; margin-bottom:20px;"></i>
            <h2>Secure Login</h2>
            <form method="POST" style="margin-top:20px;">
                <input name="email" type="email" placeholder="Email" required style="margin-bottom:10px;">
                <input name="password" type="password" placeholder="Password" required style="margin-bottom:10px;">
                <button type="submit" class="btn btn-main">LOGIN NOW</button>
                <p style="color:red; margin-top:10px; font-size:12px;">{error}</p>
            </form>
        </div>
    """)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'uid' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Admin Action: Create
        if session['role'] == 'admin' and 'new_email' in request.form:
            users_col.insert_one({
                "email": request.form['new_email'], "password": request.form['new_pass'],
                "name": request.form['new_name'], "role": "user", "business_name": request.form['new_biz']
            })
        
        # Profile Update
        if 'name' in request.form:
            users_col.update_one({"email": session['uid']}, {"$set": {
                "name": request.form['name'], "business_name": request.form['business_name'],
                "phone": request.form['phone'], "whatsapp": request.form['whatsapp'],
                "instagram": request.form['instagram'], "location": request.form['location'],
                "logo": request.form['logo'], "services": request.form['services'], "products": request.form['products']
            }})

    curr = users_col.find_one({"email": session['uid']})
    admin_html = ""
    if session['role'] == 'admin':
        others = list(users_col.find({"role": "user"}))
        user_list = "".join([f"<div style='background:white; padding:10px; margin-bottom:5px; border-radius:8px; display:flex; justify-content:space-between;'><span>{u['name']}</span><a href='/card/{u['email']}' style='font-size:12px; color:#3b82f6;'>VIEW</a></div>" for u in others])
        admin_html = f"""
            <h3 class="section-title">Create New Unique QR Card</h3>
            <form method="POST" class="field">
                <input name="new_name" placeholder="Name"><input name="new_email" placeholder="Email">
                <input name="new_pass" placeholder="Password"><input name="new_biz" placeholder="Business">
                <button type="submit" class="btn btn-main" style="margin-top:10px;">CREATE CARD</button>
            </form>
            <h3 class="section-title">Managed Cards</h3>{user_list}
        """

    return render_template_string(UI_TEMPLATE, title="Dashboard", content=f"""
        <div class="form-area">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3>Dashboard</h3><a href="/logout" style="color:red; font-size:12px;">LOGOUT</a>
            </div>
            <form method="POST" style="margin-top:15px;">
                <div class="field"><label>Name</label><input name="name" value="{curr.get('name','')}"></div>
                <div class="field"><label>Business</label><input name="business_name" value="{curr.get('business_name','')}"></div>
                <div class="field"><label>Phone</label><input name="phone" value="{curr.get('phone','')}"></div>
                <div class="field"><label>WhatsApp</label><input name="whatsapp" value="{curr.get('whatsapp','')}"></div>
                <div class="field"><label>Logo URL</label><input name="logo" value="{curr.get('logo','')}"></div>
                <div class="field"><label>About</label><textarea name="services">{curr.get('services','')}</textarea></div>
                <div class="field"><label>Products (Image URLs comma separated)</label><textarea name="products">{curr.get('products','')}</textarea></div>
                <button type="submit" class="btn btn-main">UPDATE MY CARD</button>
            </form>
            {admin_html}
        </div>
    """)

@app.route('/download_vcf/<email>')
def download_vcf(email):
    u = users_col.find_one({"email": email})
    vcf = f"BEGIN:VCARD\nVERSION:3.0\nFN:{u['name']}\nORG:{u.get('business_name','')}\nTEL:{u.get('phone','')}\nEMAIL:{u['email']}\nEND:VCARD"
    return Response(vcf, mimetype="text/vcard", headers={"Content-disposition": f"attachment; filename={u['name']}.vcf"})

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login'))

if __name__ == '__main__':
    p = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=p)
