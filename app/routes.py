from app import app, db
from flask import render_template, redirect, url_for, flash, request, session
from app.forms import LoginForm, RegisterForm, CompanyDetailForm,StrategyForm
from app.models import User, Company
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
@app.route('/home')
def home_page():
    session['logged_in'] = False
    return render_template('home.html')

#Contact Us Page
@app.route('/contact')
def contact():
    return render_template('contact.html')

#FAQ Page
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
        session['logged_in'] = True
        return redirect(url_for('main_page'))

    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    session['logged_in'] = False
    return render_template('register.html', form=form)


# logging out of the app
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    flash("Logged out successfully.", category='info')
    return redirect(url_for('login_page'))

# main page (after login)
@app.route('/main', methods=['GET', 'POST'])
def main_page():
    session['logged_in'] = True
    return render_template('main.html')

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

    # return render_template('admin_main.html')

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
#@app.route('/predict',methods=['POST'])
#def predict():

#    int_features = [int(x) for x in request.form.values()]
#    final_features = [np.array(int_features)] 

#   return render_template('xx.html')