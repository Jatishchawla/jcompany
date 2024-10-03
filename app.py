from flask import Flask, render_template, request, redirect ,flash, url_for
from flask import session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
import pandas as pd


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sampledb2.sqlite3"
db = SQLAlchemy(app)

app.app_context().push()


class User(db.Model):
    __tablename__= "User"
    id           = db.Column(db.Integer, primary_key=True)
    email        = db.Column(db.String() , nullable =False , unique = True )
    password     = db.Column(db.String(), nullable=False)
    firstname    = db.Column(db.String(), nullable=False)
    lastname     = db.Column(db.String(), nullable=False)
    address      = db.Column(db.String(), nullable=False)
    pincode      = db.Column(db.Integer, nullable=False)
    role_id      = db.Column(db.Integer, nullable=False)  # 1 - admin , 2 - employee , 3- customer
    phone_number = db.Column(db.Integer, nullable=False)
    created_at   = db.Column(db.Date, nullable = True)
    updated_at   = db.Column(db.Date , nullable = True)
    profile_image  = db.Column(db.String() )

class Employee(db.Model):
    __tablename__  = "Employee"
    id             = db.Column(db.Integer, primary_key=True)
    salary         = db.Column(db.Integer)
    experience     = db.Column(db.Integer, nullable=False)
    skills         = db.Column(db.String())
    total_bookings = db.Column(db.Integer, nullable=False)
    total_rating   = db.Column(db.Integer, nullable=False)
    created_at     = db.Column(db.Date, nullable=False)
    updated_at     = db.Column(db.Date, nullable=False)

class Booking(db.Model):
    __tablename__   = "Booking"
    id              = db.Column(db.Integer, primary_key=True)
    status          = db.Column(db.String(), nullable=False)
    cust_id         = db.Column(db.Integer, nullable=False)
    emp_id          = db.Column(db.Integer)
    package_id      = db.Column(db.Integer, nullable=False)
    booking_date    = db.Column(db.Date, nullable=False)
    completion_date = db.Column(db.Date)
    feedback        = db.Column(db.String())
    rating          = db.Column(db.Integer, nullable=False)
    created_at      = db.Column(db.Date, nullable=False)
    updated_at      = db.Column(db.Date, nullable=False)

class Package(db.Model):
    __tablename__   = "Package"
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(), nullable=False)
    description     = db.Column(db.String(), nullable=False)
    required_skills = db.Column(db.String())
    price           = db.Column(db.Integer)
    created_at      = db.Column(db.Date, nullable=False)
    updated_at      = db.Column(db.Date, nullable=False)

# Create all tables
# Key Concepts:
# Application Context: Flask needs to know which application is the "current" app when executing certain operations, such as database interactions or configuration retrieval. The application context ensures that the code is aware of which app's settings to use.

# Why It's Needed: If you’re using functionality that relies on the application (like db.create_all(), url_for(), current_app, etc.), Flask requires that you tell it which app you’re working with. Otherwise, it will raise the "Working outside of application context" error.

# Inside with app.app_context():
# Pushes the Application Context: It sets up the app’s context, making the app’s configuration and resources available for the duration of the block.
# Access to current_app and g: You can access current_app, which points to the app in the context, and g, a special object for storing data during a request.
# Handles Database Operations: Since the database depends on the app configuration (SQLAlchemy settings, for example), using app.app_context() ensures that the database functions properly inside the context.
with app.app_context():
    db.create_all()


@app.route("/" , methods= ["GET"])
def home():
    return render_template("index.html")


# for customer
@app.route("/register" , methods =["GET",  "POST"])
def register():
    if (request.method == "POST"):
        
        # print(request.form)
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Ensure password is not None or empty
        if not password:
            return "Password is required", 400 # add flash msg
        
        person = User.query.filter_by(email=email).first()
        if person:
            if (email == person.email):
                return "alredy registered email" # add flash msg
        
        # db wala code
        # role_id      =request.form.get("role_id")
        firstname = request.form.get("firstname")
        lastname     =request.form.get("lastname")
        role_id      = 3
        address      =request.form.get("address")
        pincode      =request.form.get("pincode")
        phone_number =request.form.get("phonenumber")
        profile_image =request.form.get("profile_image")
        


        new_registration = User(email=email , password = password , firstname=firstname, lastname=lastname,
                                address=address , pincode=pincode, phone_number=phone_number,
                                role_id = 3 , profile_image=profile_image ,created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow() )
        db.session.add(new_registration)
        db.session.commit()

        # person = User.query.filter_by(email=email).first()      ____
        #                                                             |___               
        # session['user'] = person.id                             ____|

        
        if (role_id == "3" ):
            return redirect("/login") # REDIRECT TO CUSTOMER LOGIN PAGE !
        if (role_id == "2"):
            return "hello service proffessional , yet to make page" # make service proffessional dashboard
        if (role_id == "1"):
            return "hello admin , yet to make admin dashboard "  # make admin dashboard page
    

    return render_template("customer_registeration_form.html")


# REGISTER SERVICE PROFFESSIONAL ON A NEW PAGE:  proffessional/register
@app.route("/proffessional/register" , methods=["GET" , "POST"])
def register3():
    if (request.method == "POST"):
        #REGISTER THE PROFESSIONAL
        return "you are registered , once admin verifies you , you can login :)"
    return render_template("proffessional_registeration_form.html")  # make a seperate register page for employee



# common for both cust and prof
@app.route("/login" , methods =["GET" , "POST"])
def login():
    
    if "user" in session:
        return redirect("/user/home") 

    if (request.method == "POST"):
        email = request.form.get("email")
        password = request.form.get("password")

        person = User.query.filter_by(email=email).first()
        # if not then register
        if not person:
            return  "user not found , please register first"

        

        if person:

            if (email == person.email and password == person.password):

                # session['user'] = person.id      ---YET TO MAKE SESSION---
                

                if (person.role_id == 3 ):
                    return redirect("/user/home")   ## REDIRECT TO COSTUMER HOME PAGE !
                    
                if (person.role_id == 2):
                    return "hello service proffessional , yet to make page" # make service proffessional dashboard
                if (person.role_id == 1):
                    return "hello admin , yet to make admin dashboard "  # make admin dashboard page
            else:
                return "credentials didnt match"
        else:
            return "PERSON NOT FOUND"
            # return redirect("/register")
    return render_template("login.html")


@app.route("/user/home", methods=["GET"])
def user_home():
    # Dummy data for services
    services = {
        'AC Repair': {'icon': 'fas fa-snowflake'},
        'Saloon': {'icon': 'fas fa-cut'},
        'Cleaning': {'icon': 'fas fa-broom'},
        'Electrician': {'icon': 'fas fa-bolt'},
        'Plumbing': {'icon': 'fas fa-faucet'}
    }
    
    # Dummy data for service history using pandas DataFrame
    service_history = pd.DataFrame({
        'Service Name': ['AC Repair', 'Cleaning', 'Electrician', 'Plumbing', 'Saloon'],
        'Professional Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Davis'],
        'Phone no.': ['123-456-7890', '234-567-8901', '345-678-9012', '456-789-0123', '567-890-1234'],
        'Status': ['Closed', 'Requested', 'In Progress', 'Closed', 'Scheduled']
    })
    
    return render_template("user_dashboard.html", services=services, service_history=service_history)

@app.route("/user/home/bookings" , methods=["GET"])
def bookings():
    return "heres is your history of booking and active services"


    
if __name__ == "__main__":
    app.run(debug=True)
