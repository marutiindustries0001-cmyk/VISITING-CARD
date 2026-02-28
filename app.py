import io
import base64
import qrcode
import os
import sys
from flask import Flask, render_template_string, request, Response, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId

# Initialize Flask App
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "maruti_industries_ultra_premium_key_8877")

# =================================================RAINBOW MONGODB SETUP =================================================
# Password yahan dhyan se bharein (No special characters recommended)
MONGO_URI = "mongodb+srv://myvisitingcard01:Gs111994@cluster0.ydu8lor.mongodb.net/?appName=Cluster0&tlsAllowInvalidCertificates=true"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=15000)
    db = client['vcard_db']
    users_col = db['users']
    # Testing the connection
    client.admin.command('ping')
    print("✅ DATABASE STATUS: Connected Successfully to MongoDB Atlas")
except Exception as e:
    print(f"❌ DATABASE ERROR: Could not connect. Reason: {e}")
    users_col = None

# Admin Creation Logic (Runs every time app starts/refreshes)
def ensure_admin_exists():
    if users_col is not None:
        try:
            admin_user = users_col.find_one({"role": "admin"})
            if not admin_user:
                users_col.insert_one({
                    "email": "admin@maruti.com",
                    "password": "admin786",
                    "name": "Master Admin",
                    "role": "admin",
                    "business_name": "Maruti Industries Official",
                    "phone": "9100000000",
                    "whatsapp": "9100000000",
                    "logo": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                    "services": "Main Admin Account for Managing Clients",
                    "products": "",
                    "instagram": "#",
                    "location": "#"
                })
                print("✅ ADMIN STATUS: Default Admin Created")
        except Exception as e:
            print(f"❌ ADMIN ERROR: {e}")

# ================================================= PREMIMUM UI DESIGN =================================================
UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #0f172a; --accent: #3b82f6; --bg: #f8fafc; --white: #ffffff; }
        * { margin:0; padding:0; box-sizing:border-box; font-family: 'Poppins', sans-serif; }
        body { background-color: #e2e8f0; display: flex; justify-content: center; align-items: flex-start; min-height: 100vh; }
        
        .app-container { width: 100%; max-width: 480px; background: var(--bg); min-height: 100vh; box-shadow: 0 0 40px rgba(0,0,0,0.2); position: relative; padding-bottom: 40px; }
        
        /* Header & Profile */
        .header-bg { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); height: 220px; border-radius: 0 0 50px 50px; position: relative; box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
        .profile-area { position: absolute; bottom: -60px; left: 50%; transform: translateX(-50%); text-align: center; width: 100%; }
        .profile-img { width: 130px; height: 130px; border-radius: 50%; border: 6px solid var(--white); object-fit: cover; background: white; box-shadow: 0 10px 25px rgba(0,0,0,0.15); }
        
        /* Main Content */
        .main-content { margin-top: 75px; padding: 0 25px; text-align: center; }
        .user-name { font-size: 26px; font-weight: 700; color: var(--primary); margin-bottom: 5px; }
        .biz-name { font-size: 15px; color: var(--accent); font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 15px; }
        .user-bio { font-size: 14px; color: #64748b; line-height: 1.6; margin-bottom: 25px; padding: 0 10px; }
        
        /* Action Buttons */
        .action-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 30px; }
        .btn { padding: 15px; border-radius: 15px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 10px; transition: 0.3s; cursor: pointer; text-decoration: none; border: none; font-size: 14px; }
        .btn-primary { background: var(--accent); color: white; box-shadow: 0 8px 15px rgba(59, 130, 246, 0.3); grid-column: span 2; }
        .btn-secondary { background: white; color: var(--primary); border: 2px solid #e2e8f0; }
        .btn:active { transform: scale(0.95); }
        
        /* Social Icons */
        .social-wrapper { display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; }
        .social-icon { width: 50px; height: 50px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: var(--primary); font-size: 22px; text-decoration: none; box-shadow: 0 5px 15px rgba(0,0,0,0.05); transition: 0.3s; }
        .social-icon:hover { background: var(--accent); color: white; transform: translateY(-5px); }
        
        /* Products Gallery */
        .section-header { display: flex; align-items: center; margin-bottom: 15px; }
        .section-header h3 { font-size: 18px; font-weight: 700; color: var(--primary); }
        .section-header .line { flex: 1; height: 2px; background: #e2e8f0; margin-left: 15px; }
        
        .product-slider { display: flex; overflow-x: auto; gap: 15px; padding-bottom: 15px; scrollbar-width: none; }
        .product-slider::-webkit-scrollbar { display: none; }
        .product-card { min-width: 200px; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; }
        .product-img { width: 100%; height: 160px; object-fit: cover; }
        
        /* QR Section */
        .qr-container { background: white; padding: 25px; border-radius: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); display: inline-block; margin-top: 20px; border: 1px solid #f1f5f9; }
        .qr-img { width: 180px; height: 180px; }

        /* Form Styles */
        .form-card { padding: 25px; text-align: left; }
        .input-group { margin-bottom: 18px; }
        .input-group label { display: block; font-size: 13px; font-weight: 600; color: #64748b; margin-bottom: 8px; }
        input, textarea, select { width: 100%; padding: 14px; border: 2px solid #f1f5f9; border-radius: 12px; font-size: 14px; outline: none; transition: 0.3s; background: #f8fafc; }
        input:focus { border-color: var(--accent); background: white; }
    </style>
    <title>{{ title }}</title>
</head>
<body>
    <div class="app-container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

# ================================================= ROUTES =================================================

@app.route('/')
def home():
    ensure_admin_exists()
    return redirect(url_for('login'))

@app.route('/card/<email>')
def view_card(email):
    user = users_col.find_one({"email": email}) if users_col else None
    if not user: 
        return "<div style='text-align:center; padding:50px;'><h1>404</h1><p>User profile not found.</p></div>", 404
    
    # QR Code Generation (Always Unique)
    full_url = request.url_root.rstrip('/') + url_for('view_card', email=email)
    qr_gen = qrcode.QRCode(version=1, box_size=10, border=2)
    qr_gen.add_data(full_url)
    qr_gen.make(fit=True)
    qr_img = qr_gen.make_image(fill_color="#0f172a", back_color="white")
    
    img_io = io.BytesIO()
    qr_img.save(img_io, 'PNG')
    qr_b64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

    # Gallery HTML
    gallery_items = ""
    if user.get('products'):
        for img_url in user['products'].split(','):
            if img_url.strip():
                gallery_items += f'<div class="product-card"><img src="{img_url.strip()}" class="product-img"></div>'

    return render_template_string(UI_TEMPLATE, title=user['name'], content=f"""
        <div class="header-bg">
            <div class="profile-area">
                <img src="{user.get('logo', 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png')}" class="profile-img">
            </div>
        </div>
        
        <div class="main-content">
            <h1 class="user-name">{user['name']}</h1>
            <p class="biz-name">{user.get('business_name', 'Maruti Industries')}</p>
            <p class="user-bio">{user.get('services', 'Welcome to my official digital visiting card.')}</p>
            
            <div class="social-wrapper">
                <a href="tel:{user.get('phone', '')}" class="social-icon"><i class="fas fa-phone"></i></a>
                <a href="https://wa.me/{user.get('whatsapp', '')}" class="social-icon"><i class="fab fa-whatsapp"></i></a>
                <a href="{user.get('instagram', '#')}" class="social-icon"><i class="fab fa-instagram"></i></a>
                <a href="{user.get('location', '#')}" class="social-icon"><i class="fas fa-map-marker-alt"></i></a>
            </div>

            <div class="action-grid">
                <a href="/download_vcf/{email}" class="btn btn-primary"><i class="fas fa-user-plus"></i> SAVE TO CONTACTS</a>
                <a href="mailto:{user['email']}" class="btn btn-secondary"><i class="fas fa-envelope"></i> EMAIL ME</a>
                <a href="https://wa.me/{user.get('whatsapp', '')}?text=Hello, I saw your digital card." class="btn btn-secondary"><i class="fab fa-whatsapp"></i> MESSAGE</a>
            </div>

            <div class="section-header"><h3>Our Products</h3><div class="line"></div></div>
            <div class="product-slider">
                {gallery_items if gallery_items else '<p style="color:#cbd5e1; font-size:12px;">No products showcased yet.</p>'}
            </div>

            <div class="section-header"><h3>Unique QR Code</h3><div class="line"></div></div>
            <div class="qr-container">
                <img src="data:image/png;base64,{qr_b64}" class="qr-img">
                <p style="font-size:11px; color:#94a3b8; margin-top:10px;">Scan this to share my profile</p>
            </div>
        </div>
    """)

@app.route('/login', methods=['GET', 'POST'])
def login():
    ensure_admin_exists()
    msg = ""
    if request.method == 'POST':
        u_email = request.form.get('email')
        u_pass = request.form.get('password')
        found = users_col.find_one({"email": u_email, "password": u_pass}) if users_col else None
        if found:
            session['user_id'] = u_email
            session['role'] = found.get('role', 'user')
            return redirect(url_for('dashboard'))
        msg = "Invalid email or password!"

    return render_template_string(UI_TEMPLATE, title="Secure Login", content=f"""
        <div style="padding:60px 30px; text-align:center;">
            <div style="margin-bottom:30px;">
                <i class="fas fa-shield-alt" style="font-size:60px; color:#3b82f6;"></i>
                <h2 style="margin-top:20px; color:#0f172a;">Partner Login</h2>
                <p style="color:#64748b; font-size:14px;">Enter your credentials to manage your card</p>
            </div>
            <form method="POST">
                <input type="email" name="email" placeholder="Email Address" required style="margin-bottom:15px;">
                <input type="password" name="password" placeholder="Secure Password" required style="margin-bottom:15px;">
                <button type="submit" class="btn btn-primary" style="width:100%;">ACCESS DASHBOARD</button>
            </form>
            <p style="color:red; font-size:12px; margin-top:15px;">{msg}</p>
        </div>
    """)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Admin Action: Create New Client
        if session['role'] == 'admin' and 'new_email' in request.form:
            new_data = {
                "email": request.form['new_email'],
                "password": request.form['new_pass'],
                "name": request.form['new_name'],
                "role": "user",
                "business_name": request.form['new_biz'],
                "logo": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
            }
            if not users_col.find_one({"email": new_data['email']}):
                users_col.insert_one(new_data)
        
        # User/Admin Action: Update Profile
        if 'name' in request.form:
            upd = {
                "name": request.form['name'],
                "business_name": request.form['business_name'],
                "phone": request.form['phone'],
                "whatsapp": request.form['whatsapp'],
                "instagram": request.form['instagram'],
                "location": request.form['location'],
                "logo": request.form['logo'],
                "services": request.form['services'],
                "products": request.form['products']
            }
            users_col.update_one({"email": session['user_id']}, {"$set": upd})

    curr_user = users_col.find_one({"email": session['user_id']})
    admin_section = ""
    if session['role'] == 'admin':
        others = list(users_col.find({"role": "user"}))
        list_html = "".join([f"<div style='display:flex; justify-content:space-between; padding:10px; background:#f1f5f9; border-radius:10px; margin-bottom:8px;'><span>{u['name']}</span><a href='/card/{u['email']}' style='color:#3b82f6; font-size:12px;'>VIEW CARD</a></div>" for u in others])
        admin_section = f"""
            <div class="section-header" style="margin-top:30px;"><h3>Register New Client</h3><div class="line"></div></div>
            <form method="POST">
                <input name="new_name" placeholder="Full Name" required style="margin-bottom:10px;">
                <input name="new_biz" placeholder="Business Name" required style="margin-bottom:10px;">
                <input name="new_email" placeholder="Client Email" required style="margin-bottom:10px;">
                <input name="new_pass" placeholder="Assign Password" required style="margin-bottom:10px;">
                <button type="submit" class="btn btn-primary" style="width:100%;">CREATE UNIQUE CARD</button>
            </form>
            <div class="section-header" style="margin-top:30px;"><h3>All Managed Clients</h3><div class="line"></div></div>
            <div style="max-height:200px; overflow-y:auto;">{list_html if list_html else 'No clients yet.'}</div>
        """

    return render_template_string(UI_TEMPLATE, title="Dashboard", content=f"""
        <div class="form-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:25px;">
                <h2 style="color:#0f172a;">Control Panel</h2>
                <a href="/logout" style="color:#ef4444; font-weight:700; text-decoration:none; font-size:13px;">LOGOUT</a>
            </div>
            
            <form method="POST">
                <div class="input-group"><label>Full Name</label><input name="name" value="{curr_user.get('name','')}"></div>
                <div class="input-group"><label>Business Name</label><input name="business_name" value="{curr_user.get('business_name','')}"></div>
                <div class="input-group"><label>Phone Number</label><input name="phone" value="{curr_user.get('phone','')}"></div>
                <div class="input-group"><label>WhatsApp (with 91)</label><input name="whatsapp" value="{curr_user.get('whatsapp','')}"></div>
                <div class="input-group"><label>Instagram Link</label><input name="instagram" value="{curr_user.get('instagram','')}"></div>
                <div class="input-group"><label>Google Maps Link</label><input name="location" value="{curr_user.get('location','')}"></div>
                <div class="input-group"><label>Profile Image URL</label><input name="logo" value="{curr_user.get('logo','')}"></div>
                <div class="input-group"><label>About / Services</label><textarea name="services" rows="3">{curr_user.get('services','')}</textarea></div>
                <div class="input-group"><label>Product URLs (Comma separated)</label><textarea name="products" rows="3">{curr_user.get('products','')}</textarea></div>
                <button type="submit" class="btn btn-primary" style="width:100%; margin-bottom:15px;">SAVE ALL CHANGES</button>
                <a href="/card/{session['user_id']}" target="_blank" class="btn btn-secondary">VIEW MY LIVE CARD</a>
            </form>
            {admin_section}
        </div>
    """)

@app.route('/download_vcf/<email>')
def download_vcf(email):
    u = users_col.find_one({"email": email})
    if not u: return "Error", 404
    vcf_content = f"BEGIN:VCARD\\nVERSION:3.0\\nFN:{u['name']}\\nORG:{u.get('business_name','')}\\nTEL;TYPE=CELL:{u.get('phone','')}\\nEMAIL:{u['email']}\\nEND:VCARD"
    return Response(vcf_content, mimetype="text/vcard", headers={{"Content-disposition": f"attachment; filename={{u['name']}}.vcf"}})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Using Render's dynamic port or default to 10000
    p = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=p, debug=False)
