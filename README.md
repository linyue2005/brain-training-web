# 脑训练 Web 应用

一个专注"认知能力训练"的 Web 应用，通过多个小游戏训练用户的注意力、记忆力、反应速度、抗干扰能力等。

## 功能

### 5 个训练游戏
- **舒尔特表** — 训练注意力与视觉搜索
- **Stroop 色词** — 训练抑制控制
- **反应抑制（Go/No-Go）** — 训练冲动控制
- **N-Back 记忆** — 训练工作记忆
- **序列记忆** — 训练空间工作记忆

每个游戏都有 **初级 / 中级 / 高级** 三档难度。

### 用户系统
- 注册 / 登录（密码 bcrypt 加密）
- 个人中心（训练统计）
- 数据隔离（每个用户只看自己的成绩）

### 其他功能
- 打卡记录（连续天数、日历）
- 日间 / 夜间模式（含星空粒子效果）
- 早睡提醒
- 响应式布局

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python + FastAPI |
| 数据库 | MySQL |
| 前端 | HTML + CSS + 原生 JavaScript |
| 密码加密 | bcrypt |

## 项目结构

```
python_yy/
├── backend/
│   └── main.py          # FastAPI 后端
└── frontend/
    ├── css/             # 样式
    ├── js/              # 脚本
    ├── index.html       # 首页
    ├── login.html       # 登录
    ├── register.html    # 注册
    ├── profile.html     # 个人中心
    ├── checkin.html     # 打卡
    ├── schulte.html     # 舒尔特表
    ├── stroop.html      # Stroop
    ├── gonogo.html      # 反应抑制
    ├── nback.html       # N-Back
    └── sequence.html    # 序列记忆
```

## 本地运行

```bash
# 1. 安装依赖
pip install fastapi uvicorn pymysql bcrypt

# 2. 配置数据库（MySQL）
# 创建数据库 brain_trainer，并建 users、records 两张表

# 3. 修改 backend/main.py 里的数据库配置

# 4. 启动服务器
cd backend
python main.py

# 5. 浏览器访问
http://127.0.0.1:8000
```
