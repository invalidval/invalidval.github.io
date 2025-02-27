from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 请替换为安全的密钥


# 创建数据库表
def create_tables():
    conn = sqlite3.connect('travel_system.db')
    c = conn.cursor()
    # 创建用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE,
                 password TEXT)''')
    # 创建旅游景点表
    c.execute('''CREATE TABLE IF NOT EXISTS attractions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 category TEXT,
                 rating REAL,
                 popularity INTEGER,
                 description TEXT)''')
    # 创建场所设施表
    c.execute('''CREATE TABLE IF NOT EXISTS facilities
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 category TEXT,
                 location TEXT,
                 attraction_id INTEGER,
                 FOREIGN KEY (attraction_id) REFERENCES attractions(id))''')
    conn.commit()
    conn.close()


# 注册功能
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template('register.html', error='用户名和密码不能为空')
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect('travel_system.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error='用户名已存在')
    return render_template('register.html')


# 登录功能
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template('login.html', error='用户名和密码不能为空')
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect('travel_system.db')
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username =? AND password =?", (username, hashed_password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    return render_template('login.html')


# 登出功能
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# 首页，展示旅游推荐
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('travel_system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM attractions ORDER BY popularity DESC LIMIT 5")
    recommended_attractions = c.fetchall()
    conn.close()
    return render_template('index.html', attractions=recommended_attractions)


# 场所查询功能
@app.route('/search_facilities', methods=['GET'])
def search_facilities():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    attraction_id = request.args.get('attraction_id')
    facility_type = request.args.get('facility_type')
    conn = sqlite3.connect('travel_system.db')
    c = conn.cursor()
    if attraction_id and facility_type:
        c.execute("""
            SELECT f.name 
            FROM facilities f
            WHERE f.attraction_id =? AND f.category =?
        """, (attraction_id, facility_type))
        facilities = c.fetchall()
    else:
        facilities = []
    conn.close()
    return render_template('search_facilities.html', facilities=facilities)


if __name__ == '__main__':
    create_tables()
    app.run(debug=True, port=5000)