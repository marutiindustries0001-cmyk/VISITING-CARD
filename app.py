import io, base64, qrcode, os
from flask import Flask, render_template_string, request, Response, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "maruti_industries_ultra_secret"

# ================= MONGODB SETUP =================
# Apna MongoDB link yahan dalein
MONGO_URI = "mongodb+srv://myvisitingcard01:Gs111994@cluster0.ydu8lor.mongodb.net/?appName=Cluster0&tlsAllowInvalidCertificates=true"
client = MongoClient(MONGO_URI)
db = client['vcard_db']
users_col = db['users']

# Master Admin Setup
if not users_col.find_one({"role": "admin"}):
    users_col.insert_one({
        "email": "admin@maruti.com",
        "password": "admin786",
        "name": "Master Admin",
        "role": "admin",
        "business_name": "Maruti Industries Admin"
    })

# ================= UI DESIGN (Mobile Optimized) =================
UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #0f172a; --accent: #3b82f6; --text: #1e293b; }
        * { margin:0; padding:0; box-sizing:border-box; font-family: 'Poppins', sans-serif; }
        body { background: #f1f5f9; display: flex; justify-content: center; color: var(--text); }
        .app-container { width: 100%; max-width: 450px; background: #fff; min-height: 100vh; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
        .hero { background: linear-gradient(135deg, var(--primary), #1e293b); height: 180px; position: relative; border-radius: 0 0 40px 40px; }
        .profile-img { width: 110px; height: 110px; border-radius: 50%; border: 4px solid #fff; position: absolute; bottom: -55px; left: 50%; transform: translateX(-50%); object-fit: cover; background: #fff; box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
        .content { margin-top: 65px; padding: 20px; text-align: center; }
        h1 { font-size: 22px; color: var(--primary); margin-bottom: 5px; }
        .biz-name { color: var(--accent); font-weight: 600; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
        .grid-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 20px 0; }
        .btn { padding: 14px; border-radius: 12px; text-decoration: none; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 14px; border:none; cursor:pointer; transition: 0.3s; }
        .btn-save { background: var(--accent); color: #fff; grid-column: span 2; }
        .btn-outline { border: 2px solid #e2e8f0; color: var(--primary); background: transparent; }
        .section-title { text-align: left; font-weight: 700; margin: 20px 0 10px; font-size: 17px; border-left: 4px solid var(--accent); padding-left: 10px; }
        .gallery { display: flex; overflow-x: auto; gap: 12px; padding-bottom: 10px; scroll-snap-type: x mandatory; }
        .product-card { min-width: 180px; background: #f8fafc; border-radius: 12px; overflow: hidden; scroll-snap-align: start; border: 1px solid #eee; }
        .product-img { width: 100%; height: 130px; object-fit: cover; }
        .social-box { display: flex; justify-content: center; gap: 12px; margin: 15px 0; }
        .social-box a { width: 42px; height: 42px; background: #f1f5f9; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: var(--primary); font-size: 18px; text-decoration: none; }
        input, textarea { width: 100%; padding: 12px; border: 1.5px solid #e2e8f0; border-radius: 10px; margin-top: 5px; margin-bottom: 15px; }
        label { font-weight: 600; font-size: 13px; display: block; text-align: left; }
    </style>
    <title>{{ title }}</title>
</head>
<body>
    <div class="app-container">{% block content %}{% endblock %}</div>
</body>
</html>
"""

# ================= ROUTES =================

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/card/<email>')
def view_card(email):
    user = users_col.find_one({"email": email})
    if not user: return "<h1>User Not Found</h1>", 404
    
    # --- UNIQUE QR CODE GENERATION ---
    # Ye QR code user ke specific card URL ko point karta hai (Hamesha Unique)
    card_url = request.url_root.rstrip('/') + url_for('view_card', email=email)
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(card_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf)
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    # Gallery Logic
    gallery_html = ""
    if user.get('products'):
        for p_url in user['products'].split(','):
            if p_url.strip():
                gallery_html += f'<div class="product-card"><img src="{p_url.strip()}" class="product-img"></div>'

    return render_template_string(UI_TEMPLATE, title=user['name'], content=f"""
        <div class="hero"><img src="{user.get('logo', '')}" class="profile-img"></div>
        <div class="content">
            <h1>{user['name']}</h1>
            <p class="biz-name">{user.get('business_name', 'Maruti Industries')}</p>
            <p style="font-size:13px; color:#64748b; margin-top:8px;">{user.get('services', '')}</p>
            
            <div class="social-box">
                <a href="https://wa.me/{user.get('whatsapp', '')}"><i class="fab fa-whatsapp"></i></a>
                <a href="{user.get('instagram', '#')}"><i class="fab fa-instagram"></i></a>
                <a href="tel:{user.get('phone', '')}"><i class="fas fa-phone"></i></a>
            </div>

            <div class="grid-actions">
                <a href="/download_vcf/{email}" class="btn btn-save"><i class="fas fa-user-plus"></i> Save Contact</a>
                <a href="{user.get('location', '#')}" class="btn btn-outline"><i class="fas fa-map-marker-alt"></i> Location</a>
                <a href="mailto:{user['email']}" class="btn btn-outline"><i class="fas fa-envelope"></i> Email</a>
            </div>

            <h3 class="section-title">Product Showcase</h3>
            <div class="gallery">{gallery_html if gallery_html else '<p style="font-size:12px; color:#ccc;">No products added</p>'}</div>

            <h3 class="section-title">Unique QR Code</h3>
            <div style="background:#f8fafc; padding:15px; border-radius:20px; display:inline-block; margin-top:10px;">
                <img src="data:image/png;base64,{qr_b64}" style="width:160px; display:block;">
                <p style="font-size:10px; margin-top:5px; color:#94a3b8;">Scan to view my digital card</p>
            </div>
        </div>
    """)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = users_col.find_one({"email": request.form['email'], "password": request.form['password']})
        if user:
            session['user'] = user['email']
            session['role'] = user.get('role', 'user')
            return redirect(url_for('dashboard'))
    return render_template_string(UI_TEMPLATE, title="Login", content="""
        <div style="padding:40px; text-align:center;">
            <i class="fas fa-id-card" style="font-size:50px; color:#3b82f6; margin-bottom:20px;"></i>
            <h2>Partner Login</h2>
            <form method="POST" style="margin-top:20px;">
                <input name="email" type="email" placeholder="Email Address" required>
                <input name="password" type="password" placeholder="Password" required>
                <button type="submit" class="btn btn-save" style="width:100%; margin-top:20px;">Login Now</button>
            </form>
        </div>
    """)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Admin Action: Create New Unique User
        if session['role'] == 'admin' and 'new_email' in request.form:
            if not users_col.find_one({"email": request.form['new_email']}):
                users_col.insert_one({
                    "email": request.form['new_email'],
                    "password": request.form['new_pass'],
                    "name": request.form['new_name'],
                    "role": "user",
                    "business_name": request.form['new_biz'],
                    "logo": "https://cdn-icons-png.flaticon.com/512/1160/1160358.png"
                })
        
        # Self Update Action
        if 'name' in request.form:
            users_col.update_one({"email": session['user']}, {"$set": {
                "name": request.form['name'],
                "business_name": request.form['business_name'],
                "phone": request.form['phone'],
                "whatsapp": request.form['whatsapp'],
                "instagram": request.form['instagram'],
                "location": request.form['location'],
                "logo": request.form['logo'],
                "services": request.form['services'],
                "products": request.form['products']
            }})

    user = users_col.find_one({"email": session['user']})
    admin_panel = ""
    if session['role'] == 'admin':
        all_users = list(users_col.find({"role": "user"}))
        user_items = "".join([f"<div style='background:#f8fafc; padding:10px; margin-bottom:8px; border-radius:10px; display:flex; justify-content:space-between; align-items:center;'><div><b>{u['name']}</b><br><small>{u['email']}</small></div><a href='/card/{u['email']}' target='_blank' style='font-size:12px; color:#3b82f6;'>View Card</a></div>" for u in all_users])
        admin_panel = f"""
            <h3 class="section-title">Admin: Create New Profile</h3>
            <form method="POST">
                <input name="new_name" placeholder="Full Name" required>
                <input name="new_biz" placeholder="Company Name" required>
                <input name="new_email" placeholder="Email (Unique ID)" required>
                <input name="new_pass" placeholder="Password" required>
                <button type="submit" class="btn btn-save" style="width:100%; margin-top:5px;">Generate Unique Card</button>
            </form>
            <h3 class="section-title">All Registered Cards</h3>
            <div style="max-height:300px; overflow-y:auto;">{user_items if user_items else '<p>No users yet</p>'}</div>
        """

    return render_template_string(UI_TEMPLATE, title="Dashboard", content=f"""
        <div style="padding:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3>Dashboard</h3>
                <a href="/logout" style="color:#ef4444; text-decoration:none; font-size:14px; font-weight:600;">Logout</a>
            </div>
            <form method="POST" style="margin-top:20px;">
                <label>Display Name</label><input name="name" value="{user.get('name','')}">
                <label>Company Name</label><input name="business_name" value="{user.get('business_name','')}">
                <label>Phone Number</label><input name="phone" value="{user.get('phone','')}">
                <label>WhatsApp (with 91)</label><input name="whatsapp" value="{user.get('whatsapp','')}">
                <label>Instagram URL</label><input name="instagram" value="{user.get('instagram','')}">
                <label>Google Maps URL</label><input name="location" value="{user.get('location','')}">
                <label>Logo/Profile Image URL</label><input name="logo" value="{user.get('logo','')}">
                <label>Services/About</label><textarea name="services" rows="3">{user.get('services','')}</textarea>
                <label>Product Image URLs (Comma separated)</label><textarea name="products" rows="3">{user.get('products','')}</textarea>
                <button type="submit" class="btn btn-save" style="width:100%; margin-bottom:10px;">Update My Card</button>
                <a href="/card/{session['user']}" target="_blank" class="btn btn-outline">Preview My Live Card</a>
            </form>
            {admin_panel}
        </div>
    """)

@app.route('/download_vcf/<email>')
def download_vcf(email):
    u = users_col.find_one({"email": email})
    vcf = f"BEGIN:VCARD\\nVERSION:3.0\\nFN:{u.get('business_name', u['name'])}\\nORG:{u.get('business_name','')}\\nTEL:{u.get('phone','')}\\nEMAIL:{u['email']}\\nEND:VCARD"
    return Response(vcf, mimetype="text/vcard", headers={"Content-disposition": f"attachment; filename={u['name']}.vcf"})

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login'))

if __name__ == '__main__':
    # Render Port Binding
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
