from flask import Flask, render_template, request, session, redirect, url_for, flash, g, send_from_directory
import sqlite3, random 
from flask_socketio import SocketIO, join_room, leave_room, emit
import os


app = Flask(__name__)
app.secret_key = 'fjaoidfj'
socketio = SocketIO(app, async_mode='threading')
app.config['UPLOAD_FOLDER'] = './uploads'

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
        # 시작 페이지를 signup이 아닌 index.html로 변경
        return render_template('index.html')

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
            with sqlite3.connect('teample.db', timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM class_info WHERE class_code = ?', (class_code,))
                existing_class_code = cursor.fetchone()
 
                if existing_class_code: 
                        flash('이미 존재하는 클래스 코드입니다.')
                        return render_template("create_class_prof.html")
                cursor.execute("INSERT INTO class_info (class_name, class_code, class_size, prof_id) VALUES (?, ?, ?, ?)",
                                (class_name, class_code, class_size, prof_id))
                flash('성공적으로 클래스가 생성되었습니다.')
                return redirect(url_for('teample_prof'))
   #    except sqlite3.OperationalError as e:
    #           flash(f"데이터베이스 오류: {e}")
     #          return render_template("create_class_prof.html")
        finally:
                conn.commit()
                conn.close()
        return render_template("create_class_prof.html")

@app.route('/teample_prof', methods = ['POST', 'GET'])
def teample_prof():
        if request.method == 'POST':
              class_code = request.form['class_code']
              conn = sqlite3.connect('teample.db')
              conn.row_factory = sqlite3.Row
              cursor = conn.cursor()
              cursor.execute('SELECT * FROM class_info WHERE class_code = ?', (class_code,))
              current_class_info = cursor.fetchall()
              cursor.execute('SELECT * FROM team_info WHERE class_code = ?', (class_code,))
              team_info = cursor.fetchall()
              cursor.execute('SELECT * FROM team_relationship WHERE class_code = ?', (class_code,))
              team_relationship = cursor.fetchall()
              conn.close()
              session['class_code'] = class_code 
              return render_template("teample_prof.html", current_class_info = current_class_info, session = session, team_info = team_info, team_relationship = team_relationship)
        return render_template("teample_prof.html")

@app.route('/create_teample',  methods = ['POST', 'GET']) 
def create_teample():
       if request.method == 'POST':
        number_of_teams = int(request.form['number_of_teams'])
        team_size = int(request.form['team_size'])
        creator_method = request.form['creator_method']
        class_code = session.get("class_code")
        prof_id = session.get('username') 
        try:
                conn = sqlite3.connect('teample.db')
                cursor = conn.cursor()
                for team in range(int(number_of_teams)):
                        cursor.execute("INSERT INTO team_info (class_code, team_size) VALUES (?, ?)",
                                (class_code, int(team_size)))
                if creator_method == 'random':
                        cursor.execute('SELECT username FROM class_relationship WHERE class_code = ?', (class_code,))
                        student_in_class = cursor.fetchall()
                        random.shuffle(student_in_class)
                        if student_in_class:
                                cursor.execute('SELECT team_id FROM team_info WHERE class_code = ?', (class_code,))
                                team_ids = cursor.fetchall()

                                student=0
                                for team_id in team_ids:
                                        for _ in range(team_size):
                                                if student >= len(student_in_class):
                                                        break 
                                                cursor.execute("INSERT INTO team_relationship (team_id, class_code, username) VALUES ( ?, ?, ?)",
                                                        (team_id[0], class_code, student_in_class[student][0],))
                                                student += 1
                                        if student >= len(student_in_class):
                                                break
                                if len(student_in_class) > student:
                                        left_students = len(student_in_class)-student
                                        flash(f"팀에 학생을 다 수용할 수 없습니다, {left_students}의 학생이 팀이 없습니다") 
                                        
                        else: flash("클래스에 학생이 없습니다")       
                        
        except Exception as e:
                flash(f"에러 발생: {e}")        
        finally: 
               conn.commit()
               conn.close()
               return redirect(url_for('teample_prof'))

@app.route('/mainpage_stu')
def mainpage_stu():
        username = session.get("username")
        conn = sqlite3.connect('teample.db')
        cursor = conn.cursor()
        cursor.execute('SELECT class_code FROM class_relationship WHERE username = ?', (username,))
        included_class_codes = cursor.fetchall()
        conn.commit()
        conn.close()
        included_class_info = []
        conn = sqlite3.connect('teample.db')
        cursor = conn.cursor()
        for class_code in included_class_codes:
                cursor.execute('SELECT class_name, class_code, class_size FROM class_info WHERE class_code= ?', (class_code[0],))
                class_info = cursor.fetchone()
                if class_info:
                    included_class_info.append(class_info)        
        return render_template("mainpage_stu.html", session=session, included_class_info= included_class_info)


@app.route('/join_class', methods=['GET', 'POST'])
def join_class():
        if request.method == 'POST':
                username = session.get('username')
                class_code = request.form['class_code']
                conn = sqlite3.connect('teample.db')
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM class_info WHERE class_code = ?', (class_code,))
                existing_class = cursor.fetchone()
                if existing_class: 
                        cursor.execute("SELECT * FROM class_relationship WHERE class_code = ? AND username = ?", (class_code, username))
                        included_in_class = cursor.fetchone()
                        if included_in_class:
                                conn.commit()
                                conn.close()
                                flash("이미 들어가 있는 클래스 입니다")
                                return redirect(url_for('mainpage_stu'))
                        insert_class_relationship = "INSERT INTO class_relationship(class_code, username) VALUES (?,?)"
                        cursor.execute(insert_class_relationship,(class_code, username))
                        session['class_code'] = class_code
                        conn.commit()
                        conn.close()
                        return redirect(url_for('teample_stu'))
                else:
                        conn.commit()
                        conn.close()
                        flash('존재하지 않는 클래스 입니다.')
                        return redirect(url_for('mainpage_stu'))
        return render_template("mainpage_stu.html")

@app.route('/teample_stu', methods=['GET', 'POST'])
def teample_stu():
        if request.method == 'POST':
                class_code = session.get('class_code')
                username = session.get('username')
                conn = sqlite3.connect('teample.db')
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM team_relationship WHERE username = ? and class_code = ?', (username, class_code))
                current_team_relationship_info = cursor.fetchall()
                current_team_info = []
                if current_team_relationship_info:
                        for _ in range(len(current_team_relationship_info)):
                                cursor.execute('SELECT * FROM team_relationship WHERE team_id = ?', (current_team_relationship_info[0][1],))
                                current_team_info.append(cursor.fetchall())
                        conn.commit()
                        conn.close() 
                        return render_template("teample_stu.html", current_team_info = current_team_info, session = session, current_team_relationship_info = current_team_relationship_info)
                return redirect(url_for('waiting_for_teample'))

        else: 
                return redirect(url_for('waiting_for_teample'))

@app.route('/waiting_for_teample', methods=['GET', 'POST'])
def waiting_for_teample():
       return render_template('waiting_for_teample.html')
        


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


if __name__ == '__main__':
        app.run( port="8000", debug=True)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
                socketio.run(app, port=8000, debug=True)