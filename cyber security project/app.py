from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from monitor import get_system_data
from detector import detect_abnormal
from whitelist import generate_whitelist
from alerts import send_alert
from werkzeug.security import generate_password_hash, check_password_hash
import json
import psutil
from flask import Flask, jsonify
import psutil
from collections import Counter
from flask_socketio import SocketIO
 
 
# Email config (GMAIL)
 
app = Flask(__name__)
CORS(app)
 
 
#DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root%4039@localhost:5432/SYSTEM_MONITOR'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
 
db = SQLAlchemy(app)
 
#MODELS 
 
class SystemMetrics(db.Model):
    __tablename__ = "system_metrics"
 
    id = db.Column(db.Integer, primary_key=True)
    cpu = db.Column(db.Float, nullable=False)
    memory = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
 
 
class AlertLog(db.Model):
    __tablename__ = "alert_logs"
 
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
 
 
class User(db.Model):
    __tablename__ = "users"
 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
 
 
 
@app.route("/")
def login_page():
    return render_template("login.html")
 
@app.route('/login-success')
def login_success():
    return render_template('success.html')
 
@app.route('/access-denied')
def access_denied():
    return render_template('access_denied.html')
 
@app.route('/user-not-found')
def user_not_found():
    return render_template('user_not_found.html')
 
 
@app.route("/signup")
def signup_page():
    return render_template("signup.html")
 
@app.route('/signup-success')
def signup_success():
    return render_template('signup_success.html')
 
@app.route("/forgot")
def forgot_page():
    return render_template("forgot.html")
 
 
@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")
 
 
@app.route('/reset-password/<token>')
def reset_password_page(token):
    return render_template("reset.html", token=token)
 
@app.route('/geo-map')
def geo_map():
    return render_template("geo.html")
 
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")
 
@app.route('/protocol')
def protocol_page():
    return render_template('protocol.html')
 
@app.route('/ip')
def ip_page():
    return render_template('ip.html')
 
 
#AUTH APIs
 
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
 
    email = data.get('email')
    password = data.get('password')
 
    if not email or not password:
        return jsonify({"message": "Missing fields"}), 400
 
    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400
 
    # Hash password
    hashed_password = generate_password_hash(password)
 
    # Save user
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
 
    return jsonify({"message": "User registered successfully"})
 
# LOGIN
@app.route('/login', methods=['POST'])
def login_api():
    try:
        data = request.get_json()
 
        email = data.get('email')
        password = data.get('password')
 
        user = User.query.filter_by(email=email).first()
 
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
 
       
        if not user.active:
            return jsonify({"status": "error", "message": "Account is deactivated"}), 403
 
        if check_password_hash(user.password, password):
            return jsonify({"status": "success", "message": "Login successful"})
        else:
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
   
@app.route('/check-user', methods=['POST'])
def check_user():
    data = request.get_json()
    email = data.get('email')
 
    user = User.query.filter_by(email=email).first()
 
    if user:
        return jsonify({"message": "User exists"}), 200
    else:
        return jsonify({"message": "User not found"}), 404
 
# API: LIVE DATA
 
@app.route("/api/data")
def api_data():
    try:
        system_data = get_system_data()
 
        known_processes = generate_whitelist()
 
        cpu = system_data.get("cpu", 0)
        memory = system_data.get("memory", 0)
 
        alerts = detect_abnormal(system_data, known_processes)
 
        # Save metrics
        metric = SystemMetrics(cpu=cpu, memory=memory)
        db.session.add(metric)
 
     
        if SystemMetrics.query.count() > 1000:
            old = SystemMetrics.query.order_by(SystemMetrics.timestamp.asc()).first()
            if old:
                db.session.delete(old)
 
        # Save alerts
        for alert in alerts:
            db.session.add(AlertLog(message=alert))
            send_alert(alert)
 
        db.session.commit()
        recent_alerts = AlertLog.query.order_by(AlertLog.timestamp.desc()).limit(15).all()
        return jsonify({
           "system_data": system_data,
           "alerts": [
                 f"{a.message} ({a.timestamp.strftime('%H:%M:%S')})"
                 for a in recent_alerts
                 ]
           })
 
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
 
 
#API: HISTORY
 
@app.route("/api/history")
def get_history():
    records = SystemMetrics.query.order_by(SystemMetrics.timestamp.desc()).limit(20).all()
 
    return jsonify([
        {
            "cpu": r.cpu,
            "memory": r.memory,
            "time": r.timestamp.strftime("%H:%M:%S")
        }
        for r in reversed(records)
    ])
 
 
# ---------------- API: PORT SCAN ---------------- #
 
@app.route("/api/scan")
def scan_ports_api():
    from scanner import scan_ports
    ports = scan_ports()
    return jsonify({"open_ports": ports})
 
# NETWORK CONNECTIONS API
@app.route('/api/connections')
def get_connections():
    connections = []
 
    for conn in psutil.net_connections(kind='inet'):
        try:
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "-"
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "-"
 
            pid = conn.pid
            process_name = "Unknown"
 
            if pid:
                try:
                    process_name = psutil.Process(pid).name()
                except:
                    process_name = "Access Denied"
 
            connections.append({
                "local_address": laddr,
                "remote_address": raddr,
                "status": conn.status,
                "pid": pid,
                "process": process_name
            })
 
        except:
            continue
 
    return jsonify(connections)
 
 
 
@app.route('/network-usage')
def network_usage():
    net = psutil.net_io_counters()
    return jsonify({
        "sent": net.bytes_sent,
        "recv": net.bytes_recv
    })
 
@app.route("/network-stats")
def network_stats():
    net_io = psutil.net_io_counters()
    connections = len(psutil.net_connections())
 
    data = {
        "packets_sent": net_io.packets_sent,
        "packets_recv": net_io.packets_recv,
        "bytes_sent": net_io.bytes_sent,
        "bytes_recv": net_io.bytes_recv
    }
 
    return jsonify(data)
 
#GEO IPS
 
import random
from flask import request, jsonify
import requests, random
 
@app.route('/geo-ip')
def geo_ip():
 
    sample_data = [
        {"ip": "8.8.8.8", "country": "United States", "lat": 37.77, "lon": -122.41},
        {"ip": "1.1.1.1", "country": "Australia", "lat": -33.86, "lon": 151.20},
        {"ip": "5.6.7.8", "country": "Russia", "lat": 55.75, "lon": 37.61},
        {"ip": "9.9.9.9", "country": "India", "lat": 13.08, "lon": 80.27},
    ]
 
    # add threat score (simulated real-time AI output)
    for item in sample_data:
        item["anomaly_score"] = random.randint(0, 40)
 
    return jsonify(sample_data)
 

@app.route('/protocol-stats')
def protocol_stats():
    connections = psutil.net_connections()
 
    tcp = sum(1 for c in connections if c.type == 1)
    udp = sum(1 for c in connections if c.type == 2)
 
    return jsonify({
        "TCP": tcp,
        "UDP": udp,
        "HTTP": tcp // 2,
        "HTTPS": tcp // 2
 })
 

 
socketio = SocketIO(app, cors_allowed_origins="*")
 
BLACKLISTED_IPS = set()
 
# ---------------- LOAD BLACKLIST ---------------- #
def load_blacklist():
    global BLACKLISTED_IPS
    try:
        with open("blacklist.json", "r") as f:
            BLACKLISTED_IPS = set(json.load(f))
    except:
        BLACKLISTED_IPS = set()
 
# ---------------- SAVE BLACKLIST ---------------- #
def save_blacklist():
    with open("blacklist.json", "w") as f:
        json.dump(list(BLACKLISTED_IPS), f)
 
# ---------------- REAL-TIME MONITOR ---------------- #
def monitor_attackers():
 
    while True:
        connections = psutil.net_connections()
        ip_counter = Counter()
 
        for conn in connections:
            if conn.raddr:
                ip_counter[conn.raddr.ip] += 1
 
        result = []
 
        for ip, count in ip_counter.most_common(5):
 
           
            if count > 5:
                BLACKLISTED_IPS.add(ip)
 
            result.append({
                "ip": ip,
                "count": count,
                "blacklisted": ip in BLACKLISTED_IPS
            })
 
        save_blacklist()   # persist data
 
        socketio.emit('attack_update', result)
 
        socketio.sleep(1)  
 
# ---------------- START BACKGROUND TASK ---------------- #
@socketio.on('connect')
def start_monitor():
    socketio.start_background_task(monitor_attackers)
load_blacklist()
 
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
   
    app.run(debug=True)