import io, base64, qrcode, os
from flask import Flask, render_template_string, request, Response, redirect, url_for, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "maruti_industries_secret_key"

# ================= DATABASE (CONNECTED ONLY WHEN NEEDED) =================
MONGO_URI = "mongodb+srv://myvisitingcard01:Gs111994@cluster0.ydu8lor.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def get_db():
    try:
        # Timeout ko sirf 3 second rakha hai taaki page na tange
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000)
        return client['vcard_db']['users']
    except Exception as e:
        print(f"Database Error: {e}")
        return None

# ================= UI TEMPLATE (STILL PREMIUM) =================
UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #f1f5f9; font-family: sans-serif; margin: 0; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 450px; background: white; min-height: 100vh; padding: 20px; box-sizing: border-box; }
        .btn { background: #0f172a; color: white; padding: 15px; border-radius: 10px; text-decoration: none; display: block; text-align: center; font-weight: bold; border: none; width: 100%; cursor: pointer; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        .card { border: 1px solid #eee; padding: 15px; border-radius: 15px; margin-top: 20px; text-align: center; }
        .social-btn { display: inline-block; margin: 5px; padding: 10px; background: #eee; border-radius: 50%; width: 40px; height: 40px; text-decoration: none; color: #333; }
    </style>
    <title>{{ title }}</title>
</head>
<body>
    <div class="container">{% block content %}{% endblock %}</div>
</body>
</html>
"""

# ================= ROUTES =================

@app.route('/')
def home():
    # Pehle login dikhao, database baad mein dekhenge
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        users_col = get_db()
        if users_col is not None:
            # Default Admin Login if DB is empty
            if request.form['email'] == "admin@maruti.com" and request.form['password'] == "admin786":
                session['uid'] = "admin@maruti.com"
                return redirect(url_for('dashboard'))
            
            u = users_col.find_one({"email": request.form['email'], "password": request.form['password']})
            if u:
                session['uid'] = u['email']
                return redirect(url_for('dashboard'))
            error = "Invalid Credentials"
        else:
            error = "Database Connection Timeout! Try again."

    return render_template_string(UI_TEMPLATE, title="Login", content=f"""
        <div style="text-align:center; padding-top:50px;">
            <h2>Partner Login</h2>
            <form method="POST">
                <input name="email" type="email" placeholder="Email" required>
                <input name="password" type="password" placeholder="Password" required>
                <button type="submit" class="btn">LOGIN</button>
                <p style="color:red">{error}</p>
            </form>
        </div>
    """)

@app.route('/dashboard')
def dashboard():
    if 'uid' not in session: return redirect(url_for('login'))
    return render_template_string(UI_TEMPLATE, title="Dashboard", content=f"""
        <h3>Welcome Partner</h3>
        <p>Logged in: {session['uid']}</p>
        <div class="card">
            <p>Aapka card system ab active hai.</p>
            <a href="/logout" style="color:red">Logout</a>
        </div>
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Render ke liye simple port binding
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
