from flask import Flask, render_template, request, session, redirect, url_for
app = Flask(__name__)

@app.route('/')
def index():
        return redirect(url_for('login'))

@app.route('/login', methods = ['GET','POST'])
def login():
        if request.method == 'POST':
                session['username'] = request.form['username']
                session['password'] = request.form['password']
                session['password_match'] = request.form['password_match']
                return redirect(url_for('mainpage_prof'))
        return render_template("loginpage.html")

@app.route('/mainpage_prof')
def mainpage_prof():        
        return render_template("mainpage_prof.html")


if __name__ == "__main__":
        app.run( port="8000")



