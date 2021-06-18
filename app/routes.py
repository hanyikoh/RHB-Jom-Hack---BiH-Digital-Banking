from app import app, db
from flask import render_template, redirect, url_for, flash, request, session, jsonify
from app.forms import LoginForm, RegisterForm, CompanyDetailForm,StrategyForm,BankLoanPackage
from app.models import User, Company, BankLoanApplication, Sales
from flask_login import login_user, logout_user, login_required, current_user
import json
import numpy as np
import pandas as pd
from app import model_arima as model
from ast import literal_eval
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

@app.route('/')
@app.route('/home')
def home_page():
    session['logged_in'] = False
    return render_template('home.html')

# Contact Us Page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# FAQ Page
@app.route('/faq')
def faq():
    return render_template('faq.html')

# login with an existing account
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):

            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')

            # this session
            session['logged_in'] = True
            session['user_id'] = attempted_user.user_id
            session['company_id'] = attempted_user.company_id

            # check is user is admin
            if attempted_user.is_admin:
                return redirect(url_for('admin_main_page'))
            
            return redirect(url_for('main_page'))
        else:
            flash('Username and password does not match! Please try again.', category='danger')

    return render_template('login.html', form=form)

# register a new account
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email=form.email.data,
                              generate_password=form.password.data)

        try:
            db.session.add(user_to_create)
            db.session.commit()
        except Exception as ex:
            flash(f"Something went wrong, user not created.", category='danger')
            session['logged_in'] = False
            return redirect(url_for('register_page'))

        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        
        
        # this session
        session['logged_in'] = True
        session['user_id'] = user_to_create.user_id
        session['company_id'] = user_to_create.company_id

        return redirect(url_for('main_page'))
    
    # if there are not errors from the validations
    if form.errors != {}: 
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    session['logged_in'] = False
    return render_template('register.html', form=form)


# logging out of the app
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    
    session['logged_in'] = False
    session['user_id'] = None
    session['company_id'] = None

    flash("Logged out successfully.", category='info')
    return redirect(url_for('login_page'))

# main page (after login)
@app.route('/main', methods=['GET', 'POST'])
def main_page():

    session['logged_in'] = True

    form = CompanyDetailForm()
    form_package = BankLoanPackage()
    today = datetime.now()

    if request.method != "POST":
        # read from database
        user_id = session.get('user_id')
        company_id = session.get('company_id')
        
        if user_id is not None and company_id is not None:
            application = BankLoanApplication.query.filter_by(user_id=user_id, company_id=company_id).first()

            # fetch all profit from rds
            all_profit = Sales.query.filter_by(application_id=application.application_id).all()
            
            profits = []
            dates = []

            for profit in all_profit:
                profits.append(profit.sales)
                dates.append('{:02d}/{}'.format(profit.month, profit.year))

            flash(profits)
            flash(dates)
            
            json_output = predict(profits, dates)    
            flash(type(json_output))     

            return render_template('main.html', form=form, form_package=form_package, json_output=json_output, today_date=today, labels=dates)
            
    return render_template('main.html', form=form, form_package=form_package, json_output=None, today_date=today, labels=None)

# check available services
@app.route('/main/service', methods=['GET', 'POST'])
def service_page():
    session['logged_in'] = True
    return render_template('service.html')

# account page, view and change account
@app.route('/main/account', methods=['GET', 'POST'])
def account_page():
    form = CompanyDetailForm()
    session['logged_in'] = True
    return render_template('my_account.html', form=form)

# Model Strategy Page, Let Company enter their strategy
@app.route('/main/form/2', methods=['GET', 'POST'])
def strategy_page():
    formOne = StrategyForm()
    session['logged_in'] = True
    return render_template('strategy.html', StrategyForm=formOne)


# form page 1
@app.route('/main/form/1', methods=['GET', 'POST'])
def form_page():
    form = CompanyDetailForm()
    session['logged_in'] = True
    return render_template('form_general.html', form=form)

# Sales form
@app.route('/main/form/sales')
def salesForm_page():
    session['logged_in'] = True
    return render_template('sales_form.html')

##### admin
# admin main page
@app.route('/admin/main', methods=['GET', 'POST'])
def admin_main_page():
    session['logged_in'] = True
    return render_template( 'admin_main.html', segment='index' )

def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  

## Model
## Getting input from the forms
@app.route('/predict', methods=['POST'])
def predict(income, dates):

    if request.method == "POST":
        income = []
        dates = []
        for i in range(0, len(request.form.getlist('income'))):
            income.append(float(request.form.getlist('income')[i])-float(request.form.getlist('expense')[i]))
            dates.append(request.form.getlist('dates')[i])

    # sales prediction using arima model
    arr = np.array(income)
    df = pd.DataFrame(arr)
    output_sales = model.sales_prediction(df)
    
    # generating label
    last_date = dates[len(dates)-1]
    last_datetime = datetime.strptime(last_date, '%m/%Y')

    for i in range(12):
        next_month = last_datetime + relativedelta(months=i+1) 
        dates.append(datetime.strftime(next_month, '%m/%Y'))
    
    values_list = output_sales.tolist()
    income.extend(values_list)

    json_output = {
        "labels": dates,
        "values": income
    }

    return jsonify(json_output)