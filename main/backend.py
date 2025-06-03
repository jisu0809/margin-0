from flask import Flask, render_template, request, session, redirect, url_for, flash, g
import sqlite3
from flask_socketio import SocketIO, join_room, leave_room, emit
import os


app = Flask(__name__)
app.secret_key = 'fjaoidfj'

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id') 
    prof_or_stu = session.get('prof_or_stu')

    if user_id is None:
        g.user = None
    else:
        conn = sqlite3.connect('logindatabase.db')
        cursor = conn.cursor()

        if prof_or_stu == 'student':
            cursor.execute("SELECT * FROM signup_info_student WHERE username = ?", (user_id,))
        elif prof_or_stu == 'prof':
            cursor.execute("SELECT * FROM signup_info_prof WHERE username = ?", (user_id,))
        else:
            g.user = None
            conn.close()
            return

        user = cursor.fetchone()
        g.user = user
        conn.close()

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
                username = request.form['username']
                password = request.form['password']
                conn = sqlite3.connect('logindatabase.db')
                cursor = conn.cursor()
                if session['prof_or_stu'] == 'student':
                        conn = sqlite3.connect('logindatabase.db')
                        cursor = conn.cursor()
                        cursor.execute('SELECT password FROM signup_info_student WHERE username = ?', username,)
                        info = cursor.fetchone()
                        if info: 
                                stored_password = info[0]
                        
                                if username == stored_password:
                                        session['user_id'] = username
                                        return render_template("login.html")
                        else: 
                                return render_template("login.html")
                elif session['prof_or_stu'] == 'prof':
                        conn = sqlite3.connect('logindatabase.db')
                        cursor = conn.cursor()
                        cursor.execute('SELECT password FROM signup_info_prof WHERE username = ?', username,)
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
                prof_id = request.form['prof_id']

                conn = sqlite3.connect('class.db')
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM class_info WHERE class_code = ?', (class_code,))
                existing_class_code = cursor.fetchone()
                if existing_class_code: 
                        conn.commit()
                        conn.close()
                        flash('이미 존재하는 클래스 코드입니다.')
                        return render_template("create_class_prof.html")
                else:
                        insert_classinfo = "INSERT INTO class_info(class_name,class_code, class_size, prof_id) VALUES (?,?,?,?)"
                        cursor.execute(insert_classinfo,(class_name, class_code, class_size, prof_id))
                        conn.commit()
                        conn.close()
                        flash('성공적으로 클래스가 생성되었습니다.')
                        return redirect(url_for('teample_prof'))
        return render_template("create_class_prof.html")


@app.route('/mainpage_stu')
def mainpage_stu():
        return render_template("mainpage_stu.html")

@app.route('/join_class', methods=['GET', 'POST'])
def join_class():
        if request.method == 'POST':
                class_code = request.form['class_code']
                conn = sqlite3.connect('class.db')
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM class_info WHERE class_code = ?', (class_code,))
                existing_class = cursor.fetchone()
                if existing_class: 
                        return redirect(url_for('teample_stu'))
                else:
                        conn.commit()
                        conn.close()
                        flash('존재하지 않는 클래스 입니다.')
                        return redirect(url_for('mainpage_stu'))
        return render_template("mainpage_stu.html")

@app.route('/teample_prof')
def teample_prof():
    return render_template("teample_prof.html")

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    socketio.run(app, port=8000, debug=True)


