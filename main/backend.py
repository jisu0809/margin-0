from flask import Flask, render_template, request, session, redirect, url_for
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
                insert_logininfo = "INSERT INTO signup_info_student(Username,Password,PasswordCHECK,Major,Grade,StudentNumber) VALUES (?,?,?,?,?,?)"
                cursor.execute(insert_logininfo,(session['username'],session['password'],session['password_match'],
                                                session['major'],session['grade'],session['studentNUM']))
                conn.commit()
                conn.close()

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
                insert_logininfo = "INSERT INTO signup_info_student(Username,Password,PasswordCHECK,Major,Grade,StudentNumber) VALUES (?,?,?,?,?,?)"
                cursor.execute(insert_logininfo,(session['username'],session['password'],session['password_match'],
                                                session['major'],session['grade'],session['studentNUM']))
                conn.commit()
                conn.close()

                return redirect(url_for('mainpage_prof.html'))
        else:
                return render_template("signup.html")


@app.route('/mainpage_prof')
def mainpage_prof():        
        return render_template("mainpage_prof.html")


if __name__ == "__main__":
        app.run( port="8000")



