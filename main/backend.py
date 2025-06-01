from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_socketio import SocketIO, join_room, leave_room, emit
import os 
import sqlite3

app = Flask(__name__)
app.secret_key = 'fjaoidfj'
socketio = SocketIO(app) 
app.config['UPLOAD_FOLDER'] = './uploads'

@app.route('/')
def index():
        return redirect(url_for('signup'))

@app.route('/signup', methods = ['GET','POST'])
def signup():
        if request.method == 'POST':
                session['porf_or_stu'] = request.form['prof_or_stu']
                session['username'] = request.form['username']
                session['password'] = request.form['password']
                session['password_match'] = request.form['password_match']
                session['major'] = request.form['major']
                session['studentNUM'] = request.form['studentNUM']
                session['grade'] = request.form['grade']
                
                if session['prof_or_stu'] == 'student':
                        conn = sqlite3.connect('logindatabase.db')
                        cursor = conn.cursor()
                        cursor.execute('SELECT * FROM signup_info_student WHERE username = ?', (session['username'],))
                        existing_user = cursor.fetchone()
                        if existing_user: 
                                conn.commit()
                                conn.close()
                                flash('이미 존재하는 사용자 이름입니다.')
                                return render_template("signup.html")
                        else:
                                insert_logininfo = "INSERT INTO signup_info_student(Username,Password,PasswordCHECK,Major,Grade,StudentNumber) VALUES (?,?,?,?,?,?)"
                                cursor.execute(insert_logininfo,(session['username'],session['password'],session['password_match'],
                                                session['major'],session['grade'],session['studentNUM']))
                                conn.commit()
                                conn.close()
                                flash('성공적으로 회원가입 되었습니다.')
                                return redirect(url_for('login'))
                elif session['prof_or_stu'] == 'prof':
                        conn = sqlite3.connect('logindatabase.db')
                        cursor = conn.cursor()
                        cursor.execute('SELECT * FROM signup_info_prof WHERE username = ?', (session['username'],))
                        existing_user = cursor.fetchone()
                
                        if existing_user: 
                                conn.commit()
                                conn.close()
                                flash('이미 존재하는 사용자 이름입니다.')
                                return render_template("signup.html")
                        else:
                                insert_logininfo = "INSERT INTO signup_info_prof(Username,Password,Major,ProfNumber) VALUES (?,?,?,?)"
                                cursor.execute(insert_logininfo,(session['username'],session['password'],
                                                session['major'], session['profNUM']))
                                conn.commit()
                                conn.close()
                                flash('성공적으로 회원가입 되었습니다.')
                                return redirect(url_for('login'))
        else:
                return render_template("signup.html")

@app.route('/login', methods = ['GET','POST'])

def login():
        if request.method == 'POST':
                session['username'] = request.form['username']
                session['password'] = request.form['password']
                conn = sqlite3.connect('logindatabase.db')
                cursor = conn.cursor()
                if session['prof_or_stu'] == 'student':
                        conn = sqlite3.connect('logindatabase.db')
                        cursor = conn.cursor()
                        cursor.execute('SELECT password FROM signup_info_student WHERE username = ?', (session['username'],))
                        info = cursor.fetchone()
                        if info: 
                                stored_password = info[0]
                        
                                if (session['username'],) == stored_password:
                                        return render_template("login.html")
                        else: 
                                return render_template("login.html")
                elif session['prof_or_stu'] == 'prof':
                        conn = sqlite3.connect('logindatabase.db')
                        cursor = conn.cursor()
                        cursor.execute('SELECT password FROM signup_info_prof WHERE username = ?', (session['username'],))
                        existing_user = cursor.fetchone()
                
                        if existing_user: 
                                conn.commit()
                                conn.close()
                                flash('이미 존재하는 사용자 이름입니다.')
                                return redirect(url_for('login'))
                        
                        else:
                                conn.commit()
                                conn.close()
                                flash('존재하지 않는 계정입니다.')
                                return render_template("login.html")
        else:
                return render_template("loginpage.html")
                

@app.route('/mainpage_prof')
def mainpage_prof():        
        return render_template("mainpage_prof.html")
@app.route('/mainpage_stu')
def mainpage_stu():        
        return render_template("mainpage_stu.html")



@app.route('/teample_stu')
def teample_stu():
        my_team = {
        'id': 3,  
        'name': 'A조',
        'members': [{'name': '홍길동'}, {'name': '김학생'}, {'name': '이학생'}]
    }
        return render_template(
        "teample_stu.html",
        my_team=my_team,
        student_name='익명',
        student_id='202301234',
        student_phone='010-1234-5678'
    )

# 파일 업로드
@app.route('/upload/<int:team_id>', methods=['POST'])
def upload_file(team_id):
    if 'file' not in request.files:
        return 'No file', 400
    file = request.files['file']
    filename = file.filename
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    # 파일 업로드 시 채팅방에 메시지 알림
    socketio.emit('chat', {
        'msg': f'파일 업로드: <a href="/uploads/{filename}" target="_blank">{filename}</a>',
        'user': session.get('username', '익명')
    }, room=f'team_{team_id}')
    return '', 204

# === 업로드된 파일 제공 ===
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# === SocketIO: 팀별 실시간 채팅 ===
@socketio.on('join')
def on_join(data):
    room = f"team_{data['team_id']}"
    join_room(room)
    emit('chat', {'msg': f"{data['user']}님이 입장했습니다.", 'user': 'system'}, room=room)

@socketio.on('chat')
def on_chat(data):
    room = f"team_{data['team_id']}"
    emit('chat', {'msg': data['msg'], 'user': data['user']}, room=room)


@app.route('/teample_prof')
def teample_prof():
    return render_template("teample_prof.html")

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    socketio.run(app, port=8000, debug=True)


