from fastapi import FastAPI, HTTPException
import sqlite3
import hashlib

app = FastAPI()

# 🎯 보안 결함 (Semgrep 탐지 타겟): Hardcoded Credentials
AWS_SECRET_TOKEN = "AKIA-SUPER-SECRET-DEV-KEY-1234"

@app.get("/")
def read_root():
    return {"message": "Welcome to the Vulnerable App. This app is designed to fail SAST and SCA scans."}

@app.get("/users/{user_id}")
def get_user(user_id: str):
    # 🎯 보안 결함 (Semgrep 탐지 타겟): SQL Injection
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()
    # f-string을 이용한 외부 변수 직접 삽입
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}

@app.post("/login")
def login(password: str):
    # 🎯 보안 결함 (Semgrep 탐지 타겟): Weak Hashing Algorithm
    hashed = hashlib.md5(password.encode()).hexdigest()
    
    # 🎯 코드 스멜 (SonarQube 탐지 타겟): Cognitive Complexity
    if password != "":
        if len(password) > 3:
            if hashed == "some_db_hash":
               return {"status": "success"}
            else:
               return {"status": "fail"}
    return {"status": "invalid"}
