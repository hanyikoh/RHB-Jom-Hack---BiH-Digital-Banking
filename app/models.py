from app import db, bcrypt, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Company(db.Model):
    company_id = db.Column(db.Integer(), primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    company_address_1 = db.Column(db.String(200), nullable=False)
    company_address_2 = db.Column(db.String(200))
    city = db.Column(db.String(50), nullable=False)
    zip = db.Column(db.Integer(), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    business_type = db.Column(db.String(70), nullable=False)
    contact_number = db.Column(db.String(50), nullable=False)
    contact_email = db.Column(db.String(50), nullable=False)
    website_link = db.Column(db.String(200))
    ctos = db.Column(db.Integer())
    ssm_id = db.Column(db.Integer())
    company_description = db.Column(db.String(500))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Company %r>' % self.company_id

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    company_id = db.Column(db.ForeignKey(Company.company_id))
    is_admin = db.Column(db.Boolean(), default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.user_id

    def get_id(self):
        return self.user_id
    
    @property
    def generate_password(self):
        return self.generate_password

    @generate_password.setter
    def generate_password(self, plain_text_password):
        self.password = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password, attempted_password)

class BankLoanApplication(db.Model):
    application_id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.ForeignKey(User.user_id))
    company_id = db.Column(db.ForeignKey(Company.company_id))
    status = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Sales(db.Model):
    sales_id = db.Column(db.Integer(), primary_key=True)
    application_id = db.Column(db.ForeignKey(BankLoanApplication.application_id))
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    sales = db.Column(db.Integer, nullable=False)

    