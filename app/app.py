from flask import Flask
import psycopg2
import os
import sys

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "paymentdb")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")


def connect_db():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn


# Application refuses to start if database is unavailable.
# This is intentionally bad design so we can demonstrate CrashLoopBackOff.
try:
    connect_db()
    print("Connected to PostgreSQL.")
except Exception as e:
    print("Database connection failed:")
    print(e)
    sys.exit(1)


@app.route("/")
def home():
    return "Payment Service Running"


@app.route("/health")
def health():
    return "OK"


app.run(host="0.0.0.0", port=5000)
