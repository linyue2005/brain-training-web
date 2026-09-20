from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pymysql
import uvicorn
import bcrypt

app = FastAPI()

# ============ 数据库配置 ============
# ⚠️ 下面这行，把 '你的密码' 换成你自己的 MySQL 密码！
DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "123456",      # ⬅ 改成这个
    "database": "brain_trainer",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

def get_db():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

# ============ 密码加密 ============
def hash_password(password: str) -> str:
    """把明文密码加密"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    """验证密码是否正确"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

# ============ 数据格式 ============
class Record(BaseModel):
    game: str
    level: str
    duration: float
    errors: int = 0
    score: int = 0
    user_id: int = 1     # 暂时写死用户ID为1，后面做登录后会改

# ============ 接口 ============
@app.get("/api")
def read_root():
    return {"message": "脑训练服务器启动成功！"}

@app.post("/api/record")
def add_record(record: Record):
    """保存一次训练成绩"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO records 
                (user_id, game, level, duration, errors, score)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                record.user_id,
                record.game,
                record.level,
                record.duration,
                record.errors,
                record.score
            ))
            conn.commit()
        return {"status": "ok"}
    finally:
        conn.close()

@app.get("/api/records")
def get_records(limit: int = 10, user_id: int = None):
    """获取最近 N 条训练记录（可选按用户过滤）"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            if user_id:
                sql = """
                    SELECT id, game, level, duration, errors, score, created_at
                    FROM records
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """
                cursor.execute(sql, (user_id, limit))
            else:
                sql = """
                    SELECT id, game, level, duration, errors, score, created_at
                    FROM records
                    ORDER BY created_at DESC
                    LIMIT %s
                """
                cursor.execute(sql, (limit,))
            records = cursor.fetchall()
            for r in records:
                r["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            return records
    finally:
        conn.close()
# ============ 数据格式：注册 ============
class RegisterData(BaseModel):
    username: str
    password: str

# ============ 注册接口 ============
@app.post("/api/register")
def register(data: RegisterData):
    """用户注册"""
    # 简单校验
    if len(data.username) < 2:
        return {"status": "error", "message": "用户名至少 2 个字符"}
    if len(data.password) < 6:
        return {"status": "error", "message": "密码至少 6 个字符"}

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 检查用户名是否已存在
            cursor.execute("SELECT id FROM users WHERE username = %s", (data.username,))
            if cursor.fetchone():
                return {"status": "error", "message": "用户名已存在"}

            # 加密密码并插入
            hashed = hash_password(data.password)
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (data.username, hashed)
            )
            conn.commit()
            new_id = cursor.lastrowid
        return {"status": "ok", "user_id": new_id, "username": data.username}
    finally:
        conn.close()
# ============ 数据格式：登录 ============
class LoginData(BaseModel):
    username: str
    password: str

# ============ 登录接口 ============
@app.post("/api/login")
def login(data: LoginData):
    """用户登录"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, password FROM users WHERE username = %s",
                (data.username,)
            )
            user = cursor.fetchone()

            if not user:
                return {"status": "error", "message": "用户名不存在"}

            if not verify_password(data.password, user["password"]):
                return {"status": "error", "message": "密码错误"}

            return {
                "status": "ok",
                "user_id": user["id"],
                "username": user["username"]
            }
    finally:
        conn.close()
# ============ 用户统计 ============
@app.get("/api/user/stats")
def get_user_stats(user_id: int):
    """获取用户的统计数据"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 基础统计
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_count,
                    IFNULL(SUM(duration), 0) as total_duration,
                    IFNULL(MAX(score), 0) as best_score,
                    IFNULL(AVG(score), 0) as avg_score
                FROM records
                WHERE user_id = %s
            """, (user_id,))
            stats = cursor.fetchone()

            # 用户信息
            cursor.execute("SELECT username, created_at FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            return {
                "user_id": user_id,
                "username": user["username"] if user else "未知",
                "created_at": user["created_at"].strftime("%Y-%m-%d") if user else "",
                "total_count": stats["total_count"],
                "total_duration": round(float(stats["total_duration"]), 1),
                "best_score": int(stats["best_score"]),
                "avg_score": int(stats["avg_score"])
            }
    finally:
        conn.close()
# ============ 打卡统计 ============
from datetime import datetime, timedelta

@app.get("/api/checkin/status")
def get_checkin_status(user_id: int):
    """获取打卡状态：连续天数、本月天数、最近7天"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 1. 查询所有有训练的日期（去重）
            cursor.execute("""
                SELECT DISTINCT DATE(created_at) as day
                FROM records
                WHERE user_id = %s
                ORDER BY day DESC
            """, (user_id,))
            days = [row["day"] for row in cursor.fetchall()]

            if not days:
                return {
                    "continuous_days": 0,
                    "month_days": 0,
                    "recent_7_days": [0, 0, 0, 0, 0, 0, 0],
                    "total_days": 0
                }

            # 2. 连续打卡天数（从今天往前数）
            today = datetime.now().date()
            continuous = 0
            check_day = today
            day_set = set(days)

            # 如果今天没打卡，从昨天开始算
            if today not in day_set:
                check_day = today - timedelta(days=1)

            while check_day in day_set:
                continuous += 1
                check_day -= timedelta(days=1)

            # 3. 本月打卡天数
            month_start = today.replace(day=1)
            month_days = sum(1 for d in days if d >= month_start)

            # 4. 最近 7 天打卡情况（1=打卡，0=没打卡），从今天往前推
            recent_7 = []
            for i in range(6, -1, -1):
                d = today - timedelta(days=i)
                recent_7.append(1 if d in day_set else 0)

            return {
                "continuous_days": continuous,
                "month_days": month_days,
                "recent_7_days": recent_7,
                "total_days": len(days)
            }
    finally:
        conn.close()
# ============ 挂载前端 ============
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)