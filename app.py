import io, base64, qrcode, os
from flask import Flask, render_template_string, request, Response, redirect, url_for, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ================= DATABASE CONNECTION =================
MONGO_URI = "mongodb+srv://myvisitingcard01:Gs111994@cluster0.ydu8lor.mongodb.net/?appName=Cluster0&tlsAllowInvalidCertificates=true"

def get_db_col():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        db = client['vcard_db']
        return db['users']
    except:
        return None

def ensure_admin(col):
    if col is not None:
        try:
            if not col.find_one({"role": "admin"}):
                col.insert_one({
                    "email": "admin@maruti.com", "password": "admin786",
                    "name": "Master Admin", "role": "admin", "business_name": "Maruti Admin"
                })
        except: pass

# ================= UI TEMPLATE (Ultra Modern Design) =================
UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #0f172a; --accent: #3b82f6; --glass: rgba(255, 255, 255, 0.9); }
        * { margin:0; padding:0; box-sizing:border-box; font-family: 'Outfit', sans-serif; }
        body { background: #e2e8f0; display: flex; justify-content: center; min-height: 100vh; }
        
        .app-container { width: 100%; max-width: 450px; background: #f8fafc; min-height: 100vh; position: relative; overflow-x: hidden; padding-bottom: 80px; }
        
        /* Premium Header */
        .header-visual { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); height: 220px; border-radius: 0 0 50px 50px; position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .profile-wrapper { position: absolute; bottom: -60px; left: 50%; transform: translateX(-50%); z-index: 10; }
        .profile-img { width: 130px; height: 130px; border-radius: 35px; border: 6px solid #f8fafc; object-fit: cover; background: white; box-shadow: 0 15px 35px rgba(0,0,0,0.15); transform: rotate(-3deg); transition: 0.3s; }
        .profile-img:hover { transform: rotate(0deg) scale(1.05); }

        .card-body { margin-top: 70px; padding: 25px; text-align: center; }
        .user-name { font-size: 28px; font-weight: 800; color: var(--primary); letter-spacing: -0.5px; }
        .biz-badge { display: inline-block; padding: 4px 15px; background: rgba(59, 130, 246, 0.1); color: var(--accent); border-radius: 20px; font-weight: 700; font-size: 13px; text-transform: uppercase; margin-top: 5px; }
        
        /* Social Icons Grid */
        .social-grid { display: flex; justify-content: center; gap: 20px; margin: 25px 0; }
        .s-icon { width: 50px; height: 50px; background: white; border-radius: 18px; display: flex; align-items: center; justify-content: center; color: var(--primary); font-size: 22px; text-decoration: none; box-shadow: 0 8px 20px rgba(0,0,0,0.06); transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
        .s-icon:hover { background: var(--accent); color: white; transform: translateY(-5px); box-shadow: 0 12px 25px rgba(59,130,246,0.3); }

        /* Modern Buttons */
        .btn-stack { display: flex; flex-direction: column; gap: 12px; margin: 25px 0; }
        .p-btn { padding: 16px; border-radius: 20px; font-weight: 700; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 12px; transition: 0.3s; border: none; font-size: 15px; }
        .btn-dark { background: var(--primary); color: white; box-shadow: 0 10px 20px rgba(15, 23, 42, 0.2); }
        .btn-light { background: white; color: var(--primary); border: 2px solid #e2e8f0; }

        /* Product Gallery */
        .section-header { text-align: left; font-size: 18px; font-weight: 800; color: var(--primary); margin: 30px 0 15px; display: flex; align-items: center; gap: 10px; }
        .section-header::after { content: ""; height: 2px; background: #e2e8f0; flex-grow: 1; }
        .gallery-box { display: flex; overflow-x: auto; gap: 15px; padding-bottom: 10px; scrollbar-width: none; }
        .gallery-card { min-width: 180px; background: white; border-radius: 22px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.04); }
        .gallery-img { width: 100%; height: 130px; object-fit: cover; }

        /* QR Section */
        .qr-card { background: white; padding: 25px; border-radius: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); margin-top: 30px; }
        .qr-img { width: 160px; height: 160px; padding: 10px; background: #f8fafc; border-radius: 20px; }

        /* Dashboard UI */
        .input-group { background: white; padding: 20px; border-radius: 25px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.02); }
        input, textarea { width: 100%; padding: 14px; border: 2px solid #f1f5f9; border-radius: 15px; margin-bottom: 12px; outline: none; transition: 0.3s; font-size: 14px; }
        input:focus { border-color: var(--accent); }

        /* Sticky Action Bar */
        .action-bar { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 400px; background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(10px); height: 65px; border-radius: 25px; display: flex; justify-content: space-around; align-items: center; z-index: 100; box-shadow: 0 15px 35px rgba(0,0,0,0.3); }
        .bar-tool { color: white; font-size: 20px; text-decoration: none; opacity: 0.8; }
        .bar-tool:hover { opacity: 1; }
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
    col = get_db_col()
    user = col.find_one({"email": email}) if col else None
    if not user: return "<h1>Not Found</h1>", 404
    
    # QR Code
    card_url = request.url_root.rstrip('/') + url_for('view_card', email=email)
    qr = qrcode.make(card_url)
    buf = io.BytesIO()
    qr.save(buf)
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    gallery = ""
    if user.get('products'):
        for p in user['products'].split(','):
            if p.strip(): gallery += f'<div class="gallery-card"><img src="{p.strip()}" class="gallery-img"></div>'

    return render_template_string(UI_TEMPLATE, title=user['name'], content=f"""
        <div class="header-visual">
            <div class="profile-wrapper">
                <img src="{user.get('logo','https://cdn-icons-png.flaticon.com/512/3135/3135715.png')}" class="profile-img">
            </div>
        </div>
        <div class="card-body">
            <h1 class="user-name">{user['name']}</h1>
            <span class="biz-badge">{user.get('business_name','DIGITAL PARTNER')}</span>
            
            <div class="social-grid">
                <a href="tel:{user.get('phone','')}" class="s-icon"><i class="fas fa-phone"></i></a>
                <a href="https://wa.me/{user.get('whatsapp','')}" class="s-icon" style="color:#25d366;"><i class="fab fa-whatsapp"></i></a>
                <a href="{user.get('instagram','#')}" class="s-icon" style="color:#e4405f;"><i class="fab fa-instagram"></i></a>
                <a href="{user.get('facebook','#')}" class="s-icon" style="color:#1877f2;"><i class="fab fa-facebook-f"></i></a>
            </div>

            <p style="color:#64748b; font-size:14px; margin-bottom:25px;">{user.get('services','Connect with us for premium services.')}</p>

            <div class="btn-stack">
                <a href="/download_vcf/{email}" class="p-btn btn-dark"><i class="fas fa-user-plus"></i> ADD TO CONTACTS</a>
                <a href="mailto:{user['email']}" class="p-btn btn-light"><i class="fas fa-envelope"></i> SEND EMAIL</a>
            </div>

            <div class="section-header">Our Products</div>
            <div class="gallery-box">{gallery if gallery else '<p>Latest products coming soon.</p>'}</div>
            
            <div class="qr-card">
                <h3 style="margin-bottom:15px; font-size:16px;">Scan to Connect</h3>
                <img src="data:image/png;base64,{qr_b64}" class="qr-img">
            </div>
        </div>

        <div class="action-bar">
            <a href="tel:{user.get('phone','')}" class="bar-tool"><i class="fas fa-phone"></i></a>
            <a href="https://wa.me/{user.get('whatsapp','')}" class="bar-tool"><i class="fab fa-whatsapp"></i></a>
            <a href="mailto:{user['email']}" class="bar-tool"><i class="fas fa-envelope"></i></a>
            <a href="/" class="bar-tool"><i class="fas fa-home"></i></a>
        </div>
    """)

@app.route('/login', methods=['GET', 'POST'])
def login():
    col = get_db_col()
    ensure_admin(col)
    error = ""
    if request.method == 'POST':
        u = col.find_one({"email": request.form['email'], "password": request.form['password']})
        if u:
            session['uid'] = u['email']
            session['role'] = u.get('role','user')
            return redirect(url_for('dashboard'))
        error = "Login failed! Please check email/password."
    return render_template_string(UI_TEMPLATE, title="Login", content=f"""
        <div style="padding:80px 30px; text-align:center;">
            <div style="width:80px; height:80px; background:var(--accent); border-radius:25px; display:inline-flex; align-items:center; justify-content:center; color:white; font-size:35px; margin-bottom:30px; box-shadow: 0 15px 30px rgba(59,130,246,0.3);">
                <i class="fas fa-shield-alt"></i>
            </div>
            <h2 style="font-weight:800; color:var(--primary);">Welcome Back</h2>
            <p style="color:#64748b; margin-bottom:30px;">Login to manage your digital presence</p>
            <form method="POST">
                <input name="email" type="email" placeholder="Email Address" required>
                <input name="password" type="password" placeholder="Password" required>
                <button type="submit" class="p-btn btn-dark" style="width:100%; margin-top:10px;">SIGN IN</button>
                <p style="color:#ef4444; font-size:13px; margin-top:15px; font-weight:600;">{error}</p>
            </form>
        </div>
    """)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'uid' not in session: return redirect(url_for('login'))
    col = get_db_col()
    
    if request.method == 'POST':
        if session.get('role') == 'admin' and 'new_email' in request.form:
            col.insert_one({"email": request.form['new_email'], "password": request.form['new_pass'], "name": request.form['new_name'], "role": "user", "business_name": request.form['new_biz']})
        
        if 'name' in request.form:
            col.update_one({"email": session['uid']}, {"$set": {
                "name": request.form['name'], "business_name": request.form['business_name'],
                "phone": request.form['phone'], "whatsapp": request.form['whatsapp'],
                "instagram": request.form['instagram'], "facebook": request.form['facebook'],
                "logo": request.form['logo'], "services": request.form['services'], "products": request.form['products']
            }})

    curr = col.find_one({"email": session['uid']})
    admin_ui = ""
    if session.get('role') == 'admin':
        others = list(col.find({"role": "user"}))
        u_list = "".join([f"<div style='background:white; padding:12px; margin-bottom:10px; border-radius:15px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 5px rgba(0,0,0,0.03);'><span><b>{u['name']}</b></span><a href='/card/{u['email']}' target='_blank' style='color:var(--accent); font-weight:700; text-decoration:none; font-size:12px;'>VIEW</a></div>" for u in others])
        admin_ui = f"""
            <div class="section-header">Admin: New Partner</div>
            <div class="input-group">
                <form method='POST'>
                    <input name='new_name' placeholder='Partner Name'>
                    <input name='new_email' placeholder='Partner Email'>
                    <input name='new_pass' placeholder='Password'>
                    <input name='new_biz' placeholder='Business Name'>
                    <button class='p-btn btn-dark' style='width:100%'>CREATE CARD</button>
                </form>
            </div>
            <div class="section-header">Active Cards</div>
            {u_list}
        """

    return render_template_string(UI_TEMPLATE, title="Dashboard", content=f"""
        <div style="padding:25px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="font-weight:800;">Settings</h2>
                <a href="/logout" style="color:#ef4444; font-weight:700; text-decoration:none;">LOGOUT</a>
            </div>
            
            <div class="section-header">Profile Details</div>
            <div class="input-group">
                <form method="POST">
                    <input name="name" value="{curr.get('name','')}" placeholder="Full Name">
                    <input name="business_name" value="{curr.get('business_name','')}" placeholder="Business Name">
                    <input name="phone" value="{curr.get('phone','')}" placeholder="Phone Number">
                    <input name="whatsapp" value="{curr.get('whatsapp','')}" placeholder="WhatsApp Number">
                    <input name="instagram" value="{curr.get('instagram','')}" placeholder="Instagram URL">
                    <input name="facebook" value="{curr.get('facebook','')}" placeholder="Facebook URL">
                    <input name="logo" value="{curr.get('logo','')}" placeholder="Logo URL">
                    <textarea name="services" placeholder="Business Bio">{curr.get('services','')}</textarea>
                    <textarea name="products" placeholder="Products (Comma separated Image URLs)">{curr.get('products','')}</textarea>
                    <button class="p-btn btn-dark" style="width:100%">SAVE UPDATES</button>
                </form>
            </div>
            {admin_ui}
        </div>
    """)

@app.route('/download_vcf/<email>')
def download_vcf(email):
    col = get_db_col()
    u = col.find_one({"email": email})
    vcf = f"BEGIN:VCARD\\nVERSION:3.0\\nFN:{u['name']}\\nORG:{u.get('business_name','')}\\nTEL:{u.get('phone','')}\\nEMAIL:{u['email']}\\nEND:VCARD"
    return Response(vcf, mimetype="text/vcard", headers={"Content-disposition": f"attachment; filename={u['name']}.vcf"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
