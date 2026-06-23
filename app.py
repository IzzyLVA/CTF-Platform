from flask import Flask, render_template, request, session, redirect, jsonify, make_response
from flask_socketio import SocketIO
import sqlite3, os, base64
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "database.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        is_admin INTEGER DEFAULT 0,
        score INTEGER DEFAULT 0
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS solved (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        challenge TEXT,
        UNIQUE(username, challenge)
    )
    """)

    conn.commit()

    if not conn.execute("SELECT 1 FROM users WHERE username='jmadmin'").fetchone():
        conn.execute(
            "INSERT INTO users (username,password,is_admin) VALUES (?,?,1)",
            ("jmadmin", generate_password_hash("JuniorMember#CTF26"))
        )
        conn.commit()

    conn.close()

init_db()

# ===== FLAGS & POINTS =====
FLAGS = {
    "portal": "JMCTF{1s_1t_r3al_L1fe_0r_ju5t_5q1i_1nject10n}",
    "cookies": "JMCTF{0nly_Ch0co1at3_ch1p_c00kies_ar3_g00d}",
    "vault": "JMCTF{l33t_h4x0r_d1dnt_brutef0rc3}",
    "encoding": "JMCTF{https://youtu.be/dQw4w9WgXcQ?si=RJpFTuxola65_ymw}",
    "mountain": "JMCTF{Mt.Haruna}",
    "ip": "JMCTF{My_0n1y_cr1m3_15_cur10517y}",
    "store": "JMCTF{Redwood_Avenue}",
    "skater": "JMCTF{SW_Park_Av_&_SW_Oak_St}",
    "crypto": "JMCTF{Crypto_15_4_us3fu1_5ki11_bu7_ch0c0l4t3_ch1p_1s_5t1ll_b3tt3r}"
}

POINTS = {
    "portal": 30,
    "cookies": 35,
    "vault": 50,
    "encoding": 60,
    "mountain": 80,
    "ip": 40,
    "store": 250,
    "skater": 120,
    "crypto": 35
}

def get_data():
    return request.get_json() if request.is_json else request.form

def broadcast_leaderboard():
    conn = get_db()
    users = conn.execute(
        "SELECT username, score FROM users ORDER BY score DESC"
    ).fetchall()
    conn.close()

    socketio.emit("leaderboard_update", [
        {"username": u["username"], "score": u["score"]}
        for u in users
    ])

def broadcast_users():
    conn = get_db()
    users = conn.execute(
        "SELECT username, score FROM users"
    ).fetchall()
    conn.close()

    socketio.emit("admin_users_update", [
        {"username": u["username"], "score": u["score"]}
        for u in users
    ])

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        data = get_data()
        u = data.get("username","").strip()
        p = data.get("password","").strip()

        if not u or not p:
            return jsonify({"success":False})

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], p):
            session["user"] = u
            broadcast_leaderboard()
            broadcast_users()
            return jsonify({"success":True})

        return jsonify({"success":False})

    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        data = get_data()
        u = data.get("username","").strip()
        p = data.get("password","").strip()

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username,password) VALUES (?,?)",
                (u, generate_password_hash(p))
            )
            conn.commit()
            broadcast_users()
            broadcast_leaderboard()
            return jsonify({"success":True})
        except:
            return jsonify({"success":False})
        finally:
            conn.close()

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# Challenges
@app.route("/challenges")
def challenges():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    solved = conn.execute(
        "SELECT challenge FROM solved WHERE username=?",
        (session["user"],)
    ).fetchall()

    score_row = conn.execute(
        "SELECT score FROM users WHERE username=?", (session["user"],)
    ).fetchone()

    admin_row = conn.execute(
        "SELECT is_admin FROM users WHERE username=?", (session["user"],)
    ).fetchone()

    conn.close()

    score = score_row["score"] if score_row else 0
    is_admin = bool(admin_row["is_admin"]) if admin_row else False

    solved_dict = {row["challenge"]: True for row in solved}

    return render_template(
        "index.html",
        solved=solved_dict,
        score=score,
        user=session["user"],
        is_admin=is_admin
    )

# ===== CHALLENGES =====
@app.route("/challenge/<name>", methods=["GET","POST"])
def challenge(name):
    if "user" not in session:
        return redirect("/login")

    if name == "portal":
        message = ""
        if request.method == "POST":
            u = request.form.get("username")
            p = request.form.get("password")

            query = f"SELECT * FROM users WHERE username='{u}' AND password='{p}'"
            conn = get_db()
            result = conn.execute(query).fetchone()
            conn.close()

            if result:
                message = f"ACCESS GRANTED :: {FLAGS['portal']}"
            else:
                message = "ACCESS DENIED"

        return render_template("portal.html", message=message)

    if name == "cookies":
        role = request.cookies.get("role")

        try:
            decoded = base64.b64decode(role).decode() if role else "user"
        except:
            decoded = "invalid"

        message = FLAGS["cookies"] if decoded == "JM{session.role = admin}" else "ACCESS DENIED"

        resp = make_response(render_template("cookies.html", message=message))
        resp.set_cookie("role", base64.b64encode(b"JM{session.role = user}").decode())
        return resp

    if name == "vault":
        return render_template("vault.html")

    if name == "encoding":
        return render_template("encoding.html")
    
    if name == "mountain":
        return render_template("mountain.html")
    
    if name == "ip":
        return render_template("ip.html")
    
    if name =="store":
        return render_template("store.html")
    
    if name =="skater":
        return render_template("skater.html")
    
    if name == "crypto":
        return render_template("crypto.html")
    
        return "Not found", 404

@app.route("/submit_flag", methods=["POST"])
def submit_flag():
    if "user" not in session:
        return jsonify({"status":"error"})

    data = get_data()
    flag = (data.get("flag") or "").strip()
    challenge = (data.get("challenge") or "").strip()

    if flag == FLAGS.get(challenge):
        conn = get_db()

        exists = conn.execute(
            "SELECT * FROM solved WHERE username=? AND challenge=?",
            (session["user"], challenge)
        ).fetchone()

        if not exists:
            conn.execute(
                "UPDATE users SET score = score + ? WHERE username=?",
                (POINTS[challenge], session["user"])
            )
            conn.execute(
                "INSERT INTO solved (username, challenge) VALUES (?,?)",
                (session["user"], challenge)
            )
            conn.commit()

        conn.close()

        broadcast_leaderboard()
        broadcast_users()

        return jsonify({"status":"success","message":"Correct flag!"})

    return jsonify({"status":"error","message":"Incorrect flag"})

@app.route("/api/admin/delete_user", methods=["POST"])
def delete_user():
    data = request.get_json()
    target = data.get("username")

    conn = get_db()
    conn.execute("DELETE FROM users WHERE username=?", (target,))
    conn.execute("DELETE FROM solved WHERE username=?", (target,))
    conn.commit()
    conn.close()

    broadcast_users()
    broadcast_leaderboard()

    return jsonify({"status":"success"})

@app.route("/api/admin/reset_user_score", methods=["POST"])
def reset_user_score():
    data = request.get_json()
    username = data.get("username")

    conn = get_db()
    conn.execute("UPDATE users SET score=0 WHERE username=?", (username,))
    conn.execute("DELETE FROM solved WHERE username=?", (username,))
    conn.commit()
    conn.close()

    broadcast_users()
    broadcast_leaderboard()

    return jsonify({"status":"success"})

@app.route("/api/admin/reset_scores", methods=["POST"])
def reset_scores():
    conn = get_db()

    conn.execute("UPDATE users SET score = 0")
    conn.execute("DELETE FROM solved")

    conn.commit()
    conn.close()

    broadcast_leaderboard()
    broadcast_users()

    socketio.emit("ctf_reset")

    return jsonify({"status": "ok"})

@socketio.on("connect")
def handle_connect():
    broadcast_leaderboard()
    broadcast_users()

if __name__ == "__main__":
    socketio.run(
        app, 
        host="0.0.0.0", 
        port=5000, 
        allow_unsafe_werkzeug=True,
        debug=True
    )