import os 
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask("miu_save")
app.secret_key = "miu-save-2026-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///miu_save.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

USERNAME = "admin"
PASSWORD = "miu2026"

class Saver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    total_deposit = db.Column(db.Float)
    weekly = db.Column(db.Float)
    method = db.Column(db.String(20), default='Cash')
    date = db.Column(db.DateTime, default=datetime.now)

with app.app_context():
    db.create_all()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect('/')
        else:
            return render_template('login.html', error="Wrong password!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        saver = Saver(
            full_name=request.form['full_name'],
            phone=request.form['phone'],
            total_deposit=float(request.form['total_deposit']),
            weekly=float(request.form['weekly']),
            method=request.form['method']
        )
        db.session.add(saver)
        db.session.commit()
        return redirect(f'/receipt/{saver.id}')
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    savers = Saver.query.order_by(Saver.date.desc()).all()
    total = sum(s.total_deposit for s in savers)
    return render_template('dashboard.html', savers=savers, total=total)

@app.route('/receipt/<int:id>')
@login_required
def receipt(id):
    s = Saver.query.get(id)
    return render_template('receipt.html', s=s)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    s = Saver.query.get(id)
    db.session.delete(s)
    db.session.commit()
    return redirect('/dashboard')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
