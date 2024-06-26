from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# モデルの定義をここに移動
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(100), nullable=False)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_day = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(100), nullable=False)

# データベースの作成
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    accounts = Account.query.all()
    transactions = Transaction.query.filter(Transaction.date.between(datetime.date.today().replace(day=1), datetime.date.today())).all()
    
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expense = sum(t.amount for t in transactions if t.amount < 0)
    net = total_income + total_expense

    category_breakdown = {}
    for t in transactions:
        if t.amount < 0:
            category_breakdown[t.category] = category_breakdown.get(t.category, 0) + abs(t.amount)

    return render_template('index.html', accounts=accounts, total_income=total_income, total_expense=abs(total_expense), net=net, category_breakdown=category_breakdown)

@app.route('/add_account', methods=['GET', 'POST'])
def add_account():
    if request.method == 'POST':
        name = request.form['name']
        balance = float(request.form['balance'])
        account = Account(name=name, balance=balance)
        db.session.add(account)
        db.session.commit()
        flash(f'アカウント "{name}" が追加されました。', 'success')
        return redirect(url_for('index'))
    return render_template('add_account.html')

@app.route('/remove_account', methods=['GET', 'POST'])
def remove_account():
    if request.method == 'POST':
        name = request.form['name']
        account = Account.query.filter_by(name=name).first()
        if account:
            db.session.delete(account)
            db.session.commit()
            flash(f'アカウント "{name}" が削除されました。', 'success')
        else:
            flash(f'アカウント "{name}" は存在しません。', 'error')
        return redirect(url_for('index'))
    accounts = Account.query.all()
    return render_template('remove_account.html', accounts=accounts)

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        date = datetime.datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        payment_method = request.form['payment_method']
        
        transaction = Transaction(amount=amount, category=category, date=date, payment_method=payment_method)
        db.session.add(transaction)
        
        account = Account.query.filter_by(name=payment_method).first()
        account.balance -= amount
        
        db.session.commit()
        flash('取引が追加されました。', 'success')
        return redirect(url_for('index'))
    accounts = Account.query.all()
    return render_template('add_transaction.html', accounts=accounts)

@app.route('/add_subscription', methods=['GET', 'POST'])
def add_subscription():
    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        payment_day = int(request.form['payment_day'])
        payment_method = request.form['payment_method']
        
        subscription = Subscription(name=name, amount=amount, payment_day=payment_day, payment_method=payment_method)
        db.session.add(subscription)
        db.session.commit()
        flash('サブスクリプションが追加されました。', 'success')
        return redirect(url_for('index'))
    accounts = Account.query.all()
    return render_template('add_subscription.html', accounts=accounts)

if __name__ == '__main__':
    app.run(debug=True)