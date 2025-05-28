from flask import Flask, render_template, request, session, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'fjaoidfj'


@app.route('/')
def index():
        return redirect(url_for('signup'))

@app.route('/signup', methods = ['GET','POST'])
def signup():
        if request.method == 'POST':
                session['username'] = request.form['username']
                session['password'] = request.form['password']
                session['password_match'] = request.form['password_match']
                session['major'] = request.form['major']
                session['studentNUM'] = request.form['studentNUM']
                session['grade'] = request.form['grade']

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
        else:
                return render_template("signup.html")

@app.route('/login', methods = ['GET','POST'])

def login():
        if request.method == 'POST':
                session['username'] = request.form['username']
                session['password'] = request.form['password']
                conn = sqlite3.connect('logindatabase.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM signup_info_student WHERE username = ? AND password = ?", session['username'], session['password'])
                q = "SELECT password FROM users WHERE username = ?;"
                cursor.execute(q, (session['username'],))
                rows = cursor.fetchone()
                print(rows)
                print(rows[0])
                

                return redirect(url_for('mainpage_prof'))
        else:
                return render_template("loginpage.html")





@app.route('/mainpage_prof')
def mainpage_prof():        
        return render_template("mainpage_prof.html")
@app.route('/mainpage_stu')
def mainpage_stu():        
        return render_template("mainpage_stu.html")




@app.route('/teample_prof')
def teample_prof():
    return render_template("teample_prof.html")

@app.route('/teample_stu')
def teample_stu():
    return render_template("teample_stu.html")


if __name__ == "__main__":
        app.run( port="8000")