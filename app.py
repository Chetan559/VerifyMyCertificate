from flask import Flask, render_template, jsonify
import psycopg2
import os
import urllib.parse as urlparse
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/mydb")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.get("/test")
def test():
    return jsonify(message="certifiacate verification app is working!")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/certificate/<enrollment_no>")
def user_certificates(enrollment_no):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT c.cert_id, e.event_name, c.issue_date
        FROM certificates c
        JOIN events e ON c.event_id = e.event_id
        WHERE c.enrollment_no = %s;
    ''', (enrollment_no,))
    
    certificates = cur.fetchall()
    conn.close()

    return render_template("user_certificate.html", enrollment_no=enrollment_no, certificates=certificates)


@app.route("/certificate/verify/<cert_id>")
def verify_certificate(cert_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT 
    c.cert_id, 
    u.name, 
    u.enrollment_no, 
    u.email, 
    u.department, 
    u.batch_year,
    e.event_name, 
    o.org_name, 
    e.event_date
FROM certificates c
JOIN users u ON c.enrollment_no = u.enrollment_no
JOIN events e ON c.event_id = e.event_id
JOIN organizations o ON e.org_id = o.org_id
WHERE c.cert_id = %s;

    ''', (cert_id,))

    cert_data = cur.fetchone()
    conn.close()

    if cert_data:
        cert_info = {
            "cert_id": cert_data[0],
            "name": cert_data[1],
            "enrollment_no": cert_data[2],
            "email": cert_data[3],
            "department": cert_data[4],
            "batch_year": cert_data[5],
            "event_name": cert_data[6],
            "org_name": cert_data[7],
            "date": cert_data[8]
        }
        return render_template("verified.html", cert=cert_info)
    else:
        return render_template("not_found.html", cert_id=cert_id)

if __name__ == "__main__":
    app.run(debug=True)
