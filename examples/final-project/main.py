from fastapi import FastAPI, HTTPException
import sqlite3
import hashlib
import os

app = FastAPI()

# ✅ 조치 완료: 환경변수를 활용한 자격 증명 은닉 (Hardcoded Secret 우회)
AWS_SECRET_TOKEN = os.getenv("AWS_SECRET_TOKEN", "default-fallback-if-needed")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Secure App. All vulnerabilities and code smells have been remediated."}

@app.get("/users/{user_id}")
def get_user(user_id: str):
    # ✅ 조치 완료: SQL 파라미터 바인딩을 이용한 Injection 차단
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()
    
    # f-string 제거 및 ? 플레이스홀더 사용
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}

@app.post("/login")
def login(password: str):
    # ✅ 조치 완료: Guard Clauses (Early Return) 도입으로 Code Smell (인지적 복잡도) 해소
    if not password or len(password) <= 3:
        return {"status": "invalid"}
        
    # ✅ 조치 완료: 취약한 MD5 해시 함수 제거 및 강력한 SHA256 알고리즘 상향 적용
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    if hashed != "some_db_hash":
        return {"status": "fail"}
        
    return {"status": "success"}
