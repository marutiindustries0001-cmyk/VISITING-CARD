import io, base64, qrcode, os
from flask import Flask, render_template_string, request, Response, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "maruti_industries_ultra_secret"

# ================= MONGODB SETUP =================
# Yahan apni MongoDB Connection String dalein
MONGO_URI = "YOUR_MONGODB_CONNECTION_STRING_HERE"
client = MongoClient(MONGO_URI)
db = client['vcard_db']
users_col = db['users']

# Default Admin Setup
if not users_col.find_one({"role": "admin"}):
    users_col.insert_one({
        "email": "admin@maruti.com",
        "password": "admin786",
        "name": "Master Admin",
        "role": "admin",
        "business_name": "Maruti Industries Admin"
    })

# ================= UI DESIGN (Ultra Attractive) =================
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
        
        /* Card Header */
        .hero { background: linear-gradient(135deg, var(--primary), #1e293b); height: 200px; position: relative; border-radius: 0 0 40px 40px; }
        .profile-img { width: 120px; height: 120px; border-radius: 50%; border: 5px solid #fff; position: absolute; bottom: -60px; left: 50%; transform: translateX(-50%); object-fit: cover; background: #fff; box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
        
        /* Content */
        .content { margin-top: 70px; padding: 20px; text-align: center; }
        h1 { font-size: 24px; color: var(--primary); margin-bottom: 5px; }
        .biz-name { color: var(--accent); font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
        
        /* Action Buttons */
        .grid-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 25px 0; }
        .btn { padding: 15px; border-radius: 12px; text-decoration: none; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px; transition: 0.3s; font-size: 14px; }
        .btn-save { background: var(--accent); color: #fff; grid-column: span 2; }
        .btn-outline { border: 2px solid #e2e8f0; color: var(--primary); }
        
        /* Product Gallery */
        .section-title { text-align: left; font-weight: 700; margin: 20px 0 10px; font-size: 18px; border-left: 4px solid var(--accent); padding-left: 10px; }
        .gallery { display: flex; overflow-x: auto; gap: 15px; padding-bottom: 10px; scroll-snap-type: x mandatory; }
        .product-card { min-width: 200px; background: #f8fafc; border-radius: 15px; overflow: hidden; scroll-snap-align: start; }
        .product-img { width: 100%; height: 150px; object-fit: cover; }
        
        /* Social Links */
        .social-box { display: flex; justify-content: center; gap: 15px; margin: 20px 0; }
        .social-box a { width: 45px; height: 45px; background: #f1f5f9; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: var(--primary); font-size: 20px; transition: 0.3s; }
        .social-box a:hover { background: var(--accent); color: #fff; }

        /* Admin Forms */
        .form-group { text-align: left; margin-bottom: 15px; }
        input, textarea { width: 100%; padding: 12px; border: 1.5px solid #e2e8f0; border-radius: 10px; margin-top: 5px; }
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
    if not user: return "User Not Found", 404
    
    # QR Code
    qr = qrcode.make(request.url)
    buf = io.BytesIO(); qr.save(buf)
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    # Product Gallery Logic
    products = user.get('products', "").split(',')
    gallery_html = ""
    if products[0]:
        for p_url in products:
            gallery_html += f'<div class="product-card"><img src="{p_url.strip()}" class="product-img"></div>'

    return render_template_string(UI_TEMPLATE, title=user['name'], content=f"""
        <div class="hero">
            <img src="{user.get('logo', '')}" class="profile-img">
        </div>
        <div class="content">
            <h1>{user['name']}</h1>
            <p class="biz-name">{user.get('business_name', 'Maruti Industries')}</p>
            <p style="font-size:13px; color:#64748b; margin-top:10px;">{user.get('services', '')}</p>
            
            <div class="social-box">
                <a href="https://wa.me/{user.get('whatsapp', '')}"><i class="fab fa-whatsapp"></i></a>
                <a href="{user.get('instagram', '#')}"><i class="fab fa-instagram"></i></a>
                <a href="tel:{user.get('phone', '')}"><i class="fas fa-phone"></i></a>
            </div>

            <div class="grid-actions">
                <a href="/download_vcf/{email}" class="btn btn-save"><i class="fas fa-user-plus"></i> Save Contact to Phone</a>
                <a href="{user.get('location', '#')}" class="btn btn-outline"><i class="fas fa-map-marker-alt"></i> Location</a>
                <a href="mailto:{user['email']}" class="btn btn-outline"><i class="fas fa-envelope"></i> Email</a>
            </div>

            <h3 class="section-title">Our Products</h3>
            <div class="gallery">{gallery_html}</div>

            <h3 class="section-title">Scan QR</h3>
            <img src="data:image/png;base64,{qr_b64}" style="width:150px; margin-top:10px; border:10px solid #f8fafc; border-radius:15px;">
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
            <img src="https://cdn-icons-png.flaticon.com/512/1160/1160358.png" style="width:80px; margin-bottom:20px;">
            <h2>Partner Login</h2>
            <form method="POST" style="margin-top:20px;">
                <input name="email" type="email" placeholder="Email Address" required>
                <input name="password" type="password" placeholder="Password" required>
                <button type="submit" class="btn btn-save" style="width:100%; border:none; margin-top:20px; cursor:pointer;">Access Dashboard</button>
            </form>
        </div>
    """)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Admin: Create New User
        if session['role'] == 'admin' and 'new_email' in request.form:
            users_col.insert_one({
                "email": request.form['new_email'],
                "password": request.form['new_pass'],
                "name": request.form['new_name'],
                "role": "user",
                "business_name": request.form['new_biz']
            })
        
        # User/Admin: Update Details
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
    all_users = list(users_col.find({"role": "user"})) if session['role'] == 'admin' else []

    admin_panel = ""
    if session['role'] == 'admin':
        user_items = "".join([f"<div style='background:#f8fafc; padding:10px; margin:5px; border-radius:8px;'>{u['name']} - <a href='/card/{u['email']}'>View Card</a></div>" for u in all_users])
        admin_panel = f"""
            <h3 class="section-title">Admin: Add New Client</h3>
            <form method="POST">
                <input name="new_name" placeholder="Full Name" required>
                <input name="new_biz" placeholder="Business Name" required>
                <input name="new_email" placeholder="Email" required>
                <input name="new_pass" placeholder="Password" required>
                <button type="submit" class="btn btn-save" style="width:100%; border:none; margin-top:10px;">Create Account</button>
            </form>
            <h3 class="section-title">All Clients</h3>{user_items}
        """

    return render_template_string(UI_TEMPLATE, title="Dashboard", content=f"""
        <div style="padding:20px;">
            <h2>Control Panel</h2>
            <form method="POST" style="margin-top:20px;">
                <div class="form-group"><label>My Name</label><input name="name" value="{user.get('name','')}"></div>
                <div class="form-group"><label>Business Name</label><input name="business_name" value="{user.get('business_name','')}"></div>
                <div class="form-group"><label>Phone</label><input name="phone" value="{user.get('phone','')}"></div>
                <div class="form-group"><label>WhatsApp (e.g. 919999999999)</label><input name="whatsapp" value="{user.get('whatsapp','')}"></div>
                <div class="form-group"><label>Instagram Link</label><input name="instagram" value="{user.get('instagram','')}"></div>
                <div class="form-group"><label>Google Maps Link</label><input name="location" value="{user.get('location','')}"></div>
                <div class="form-group"><label>Profile/Logo URL</label><input name="logo" value="{user.get('logo','')}"></div>
                <div class="form-group"><label>Short Bio</label><textarea name="services">{user.get('services','')}</textarea></div>
                <div class="form-group"><label>Product Image URLs (Comma Separated)</label><textarea name="products">{user.get('products','')}</textarea></div>
                <button type="submit" class="btn btn-save" style="width:100%; border:none; cursor:pointer;">Save All Changes</button>
            </form>
            {admin_panel}
            <a href="/logout" style="color:red; display:block; text-align:center; margin-top:20px;">Logout</a>
        </div>
    """)

@app.route('/download_vcf/<email>')
def download_vcf(email):
    u = users_col.find_one({"email": email})
    # Isme Business Name add kar diya hai taaki phone mein wahi dikhe
    vcf = f"BEGIN:VCARD\\nVERSION:3.0\\nFN:{u.get('business_name', u['name'])}\\nORG:{u.get('business_name','')}\\nTEL:{u.get('phone','')}\\nEMAIL:{u['email']}\\nEND:VCARD"
    return Response(vcf, mimetype="text/vcard", headers={"Content-disposition": f"attachment; filename={u['name']}.vcf"})

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))
