from flask import Flask, render_template, request, session, redirect, url_for, flash, g, send_from_directory
import sqlite3
#from flask_socketio import SocketIO, join_room, leave_room, emit
import os


app = Flask(__name__)
app.secret_key = 'fjaoidfj'
#socketio = SocketIO(app, async_mode='threading')
#app.config['UPLOAD_FOLDER'] = './uploads'

@app.before_request
def save_logged_in_user():
    username = session.get('username')
    prof_or_stu = session.get('prof_or_stu')
    g.user = None
    if username and prof_or_stu:
        conn = sqlite3.connect('teample.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if prof_or_stu == 'student':
            cursor.execute('SELECT * FROM signup_info_student WHERE username = ?', (username,))
            g.user = cursor.fetchone()
            conn.close()
        elif prof_or_stu == 'prof':
            cursor.execute('SELECT * FROM signup_info_prof WHERE username = ?', (username,))
            g.user = cursor.fetchone()
            conn.close()

@app.route('/')
def index():
        return redirect(url_for('signup'))

@app.route('/signup', methods = ['GET','POST'])
def signup():
        if request.method == 'POST':
                prof_or_stu = request.form['prof_or_stu']
                
                if prof_or_stu == 'student':
                        username = request.form['username']
                        password = request.form['password']
                        major = request.form['major']
                        student_number = request.form['studentNUM']
                        grade = request.form['grade']
                        conn = sqlite3.connect('teample.db')
                        cursor = conn.cursor()
                        cursor.execute('SELECT * FROM signup_info_student WHERE username = ?', (username,))
                        existing_user = cursor.fetchone()
                        if existing_user: 
                                conn.commit()
                                conn.close()
                                flash('이미 존재하는 사용자 이름입니다.')
                                return render_template("signup.html")
                        else:
                                insert_logininfo = "INSERT INTO signup_info_student(username,password,major,grade,student_number) VALUES (?,?,?,?,?)"
                                cursor.execute(insert_logininfo,(username,password,major,grade,student_number))
                                conn.commit()
                                conn.close()
                                flash('성공적으로 회원가입 되었습니다.')
                                return redirect(url_for('login'))
                elif prof_or_stu == 'prof':
                        username = request.form['username']
                        password = request.form['password']
                        major = request.form['major']
                        prof_number = request.form['profNUM']
                        conn = sqlite3.connect('teample.db')
                        cursor = conn.cursor()
                        cursor.execute('SELECT * FROM signup_info_prof WHERE username = ?', (username,))
                        existing_user = cursor.fetchone()
                
                        if existing_user: 
                                conn.commit()
                                conn.close()
                                flash('이미 존재하는 사용자 이름입니다.')
                                return render_template("signup.html")
                        else:
                                insert_logininfo = "INSERT INTO signup_info_prof(username,password,major,prof_number) VALUES (?,?,?,?)"
                                cursor.execute(insert_logininfo,(username,password,major, prof_number))
                                conn.commit()
                                conn.close()
                                flash('성공적으로 회원가입 되었습니다.')
                                return redirect(url_for('login'))
        else:
                return render_template("signup.html")

@app.route('/login', methods = ['GET','POST'])
def login():
        if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                prof_or_stu = request.form['prof_or_stu']
                conn = sqlite3.connect('teample.db')
                cursor = conn.cursor()

                if prof_or_stu == 'student':
                        cursor.execute('SELECT * FROM signup_info_student WHERE username = ?', (username,))
                        existing_user_info = cursor.fetchone()
                        if existing_user_info: 
                                stored_password = existing_user_info[1]
                                if password == stored_password:
                                        session['username'] = username
                                        session['prof_or_stu'] = prof_or_stu
                                        session['major'] = existing_user_info[2]          
                                        session['grade'] = existing_user_info[3]          
                                        session['student_number'] = existing_user_info[4]
                                        conn.close()
                                        return redirect(url_for('mainpage_stu'))
                                else: flash('비밀번호가 틀렸습니다.')
                        else: flash('존재하지 않는 계정입니다.')
                        conn.close()
                        return render_template("loginpage.html")
                elif prof_or_stu == 'prof':
                        cursor.execute('SELECT * FROM signup_info_prof WHERE username = ?', (username,))
                        existing_user_info = cursor.fetchone()
                        if existing_user_info: 
                                stored_password = existing_user_info[1]
                                if password == stored_password:
                                        session['username'] = username
                                        session['prof_or_stu'] = prof_or_stu
                                        session['major'] = existing_user_info[2]          
                                        session['prof_number'] = existing_user_info[3]
                                        conn.close()
                                        return redirect(url_for('mainpage_prof'))
                                else: flash('비밀번호가 틀렸습니다.')
                        else: flash('존재하지 않는 계정입니다.')
                        conn.close()
                        return render_template("loginpage.html")
        else:
                return render_template("loginpage.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("로그아웃 되었습니다.")
    return redirect(url_for('login'))


@app.route('/mainpage_prof')
def mainpage_prof():        
        prof_id = session.get("username")
        conn = sqlite3.connect('teample.db')
        cursor = conn.cursor()
        cursor.execute('SELECT class_name, class_code, class_size FROM class_info WHERE prof_id = ?', (prof_id,))
        prof_all_class_info = cursor.fetchall()
        return render_template("mainpage_prof.html", session=session, prof_all_class_info= prof_all_class_info)

@app.route('/move_to_create_class', methods=['GET', 'POST'])
def move_to_create_class():           
        if request.method == 'POST':    
                return render_template("create_class_prof.html")
        return redirect(url_for('mainpage_prof'))

@app.route('/create_class_prof', methods = ['GET','POST'])
def create_class_prof():
    if request.method == 'POST':
        class_name = request.form['class_name']
        class_code = request.form['class_code']
        class_size = int(request.form['class_size'])
        prof_id = session.get('username') 

        try:
            conn = sqlite3.connect('teample.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM class_info WHERE class_code = ?', (class_code,))
            existing_class_code = cursor.fetchone()
            if existing_class_code: 
                flash('이미 존재하는 클래스 코드입니다.')
                return render_template("create_class_prof.html")
            cursor.execute("INSERT INTO class_info (class_name, class_code, class_size, prof_id) VALUES (?, ?, ?, ?)",
                (class_name, class_code, class_size, prof_id))
            conn.commit()
            flash('성공적으로 클래스가 생성되었습니다.')
            return redirect(url_for('teample_prof'))
        except sqlite3.OperationalError as e:
            flash(f"데이터베이스 오류: {e}")
            return render_template("create_class_prof.html")
        finally:
            conn.close()
    return render_template("create_class_prof.html")

@app.route('/teample_prof', methods = ['POST'])
def teample_prof():
        if request.method == 'POST':
              class_code = request.form['class_code']
              conn = sqlite3.connect('teample.db')
              cursor = conn.cursor()
              cursor.execute('SELECT * FROM class_info WHERE class_code = ?', (class_code,))
              current_class_info = cursor.fetchone()
              conn.close()
              return render_template("teample_prof.html", current_class_info = current_class_info, session = session)
        return render_template("teample_prof.html")

@app.route('/create_team')
def create_team():'''
        if request.method == 'POST':
        class_name = request.form['class_name']
        class_code = request.form['class_code']
        class_size = int(request.form['class_size'])
        prof_id = session.get('username') 

        try:
            conn = sqlite3.connect('teample.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM class_info WHERE class_code = ?', (class_code,))
            existing_class_code = cursor.fetchone()
            if existing_class_code: 
                flash('이미 존재하는 클래스 코드입니다.')
                return render_template("create_class_prof.html")
            cursor.execute("INSERT INTO class_info (class_name, class_code, class_size, prof_id) VALUES (?, ?, ?, ?)",
                (class_name, class_code, class_size, prof_id))
            conn.commit()
            flash('성공적으로 클래스가 생성되었습니다.')
            return redirect(url_for('teample_prof'))
        except sqlite3.OperationalError as e:
            flash(f"데이터베이스 오류: {e}")
            return render_template("create_class_prof.html")
        finally:
            conn.close()
            return render_template("create_class_prof.html")
       '''
@app.route('/mainpage_stu')
def mainpage_stu():
        return render_template("mainpage_stu.html", session=session)

@app.route('/join_class', methods=['GET', 'POST'])
def join_class():
        if request.method == 'POST':
                class_code = request.form['class_code']
                conn = sqlite3.connect('teample.db')
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM class_info WHERE class_code = ?', (class_code,))
                existing_class = cursor.fetchone()
                if existing_class: 
                        insert_class_relationship = "INSERT INTO class_relationship(class_code, username) VALUES (?,?)"
                        cursor.execute(insert_class_relationship,(class_code, g.user))
                        return redirect(url_for('teample_stu'))
                else:
                        conn.commit()
                        conn.close()
                        flash('존재하지 않는 클래스 입니다.')
                        return redirect(url_for('mainpage_stu'))
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
"""
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
"""

if __name__ == '__main__':
        app.run( port="8000", debug=True)
#    if not os.path.exists(app.config['UPLOAD_FOLDER']):
#        os.makedirs(app.config['UPLOAD_FOLDER'])
#    socketio.run(app, port=8000, debug=True)


