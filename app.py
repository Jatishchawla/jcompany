from flask import Flask, render_template, request, redirect ,flash, url_for
from flask import session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
import pandas as pd
import uuid
import bcrypt


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sampledb1.sqlite3"
app.config['SECRET_KEY']="key"
db = SQLAlchemy(app)

app.app_context().push()


class User(db.Model):
    __tablename__= "User"
    uuid           = db.Column(db.String() , primary_key=True)
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
    profile_image= db.Column(db.String() )

    def __init__(self, uuid , email, password, firstname, lastname, address, pincode, role_id, phone_number, created_at, updated_at,  profile_image):
        self.uuid = uuid
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.firstname = firstname
        self.lastname =lastname
        self.pincode=pincode
        self.address=address 
        self.phone_number=phone_number
        self.role_id = role_id
        self.profile_image=profile_image 
        self.created_at = created_at
        self.updated_at = updated_at



    def check_password(self , password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)




class Employee(db.Model):
    __tablename__  = "Employee"
    email          = db.Column(db.String() , nullable =False , unique = True )
    uuid           = db.Column(db.String(), primary_key=True)
    salary         = db.Column(db.Integer)
    experience     = db.Column(db.Integer, nullable=False)
    skill          = db.Column(db.String())
    total_bookings = db.Column(db.Integer, nullable=False)
    total_rating   = db.Column(db.Integer, nullable=False)
    avialable      = db.Column(db.Boolean , nullable=False , default = True  )
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
            flash("Password Required")
            return redirect(url_for('register'))
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash( "Email Id Already in Use, please sign in")
            return redirect(url_for('login'))
        
        id=uuid.uuid4()
        # db wala code
        firstname = request.form.get("firstname")
        lastname     =request.form.get("lastname")
        role_id      = 3
        address      =request.form.get("address")
        pincode      =request.form.get("pincode")
        phone_number =request.form.get("phonenumber")
        profile_image =request.form.get("profile_image")
        
        new_registration = User(uuid = str(id) ,email=email , password = password , firstname=firstname, lastname=lastname,
                                address=address , pincode=pincode, phone_number=phone_number,
                                role_id = 3 , profile_image=profile_image ,created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow() )
        db.session.add(new_registration)
        db.session.commit()

        
        # user = User.query.filter_by(email=email).first()      ____
        #                                                             |___               
        # session['user'] = user.id                             ____|

        flash( "REGISTERED SUCCESSFULLY !" )
        return redirect(url_for("login")) # REDIRECT TO LOGIN PAGE !
       

    return render_template("customer_registeration_form.html")


# REGISTER SERVICE PROFESSIONAL ON A NEW PAGE:  professional/register
@app.route("/professional/register" , methods=["GET" , "POST"])
def professional_register():
    if (request.method == "POST"):
        
        # print(request.form)
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Ensure password is not None or empty
        if not password:
            flash("Password is required")
            return redirect("/login")
        
        user = User.query.filter_by(email=email).first()
        if user:
            if (email == user.email):
                flash( "Email Id Already in Use, please sign in" )
                return redirect(url_for('login'))
        
        # db wala code

        id = uuid.uuid4()

        # print('Your UUID is: ' + str(myuuid))

        firstname = request.form.get("firstname")
        lastname     =request.form.get("lastname")
        role_id      = 2
        address      =request.form.get("address")
        pincode      =request.form.get("pincode")
        phone_number =request.form.get("phonenumber")
        profile_image =request.form.get("profile_image")

        salary = 0
        experience = request.form.get("experience")
        skill=request.form.get("skill")
        # total_bookings=request.form.get("total_bookings")
        # =request.form.get("")
        # =request.form.get("")
        # =request.form.get("")
        # total_rating=request.form.get("total_rating")

        new_user_registration = User(uuid=str(id), email=email , password = password , firstname=firstname, lastname=lastname,
                                address=address , pincode=pincode, phone_number=phone_number,
                                role_id = 2 , profile_image=profile_image ,created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow() )
        

        new_professional_registration= Employee(uuid=str(id), email=email,salary=salary , skill=skill , experience=experience , total_bookings=0 , 
                                                total_rating=0 ,created_at=datetime.utcnow(), updated_at=datetime.utcnow() 
                                                )
        
        db.session.add(new_professional_registration)
        db.session.add(new_user_registration)
        db.session.commit()

        
        # user = User.query.filter_by(email=email).first()      ____
        #                                                             |___               
        # session['user'] = user.id                             ____|

        flash( "REGISTERED SUCCESSFULLY !" )
        return redirect(url_for("login")) # REDIRECT TO  LOGIN PAGE !
    
    return render_template("professional_registeration_form.html")  # make a seperate register page for employee



# common for both cust and prof
@app.route("/login" , methods =["GET" , "POST"])
def login():
    
    if "firstname" in session:
        flash("Please Sign Out First"),400
        return redirect(url_for("user_home"))
     
    if (request.method == "POST"):
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        # if not then register
        if not user:
            flash("please create account first"),400
            return redirect(url_for("register"))

        if user:

            if (email == user.email and user.check_password(password) ):
                # session['user'] = user.id      ---YET TO MAKE SESSION---
                session['firstname']=user.firstname
                session['lastname']=user.lastname
                session['email']=user.email
                session['role_id']=user.role_id
                session['signedin']=True

                if (user.role_id == 3 ):
                    return redirect("/user/home" )   ## REDIRECT TO COSTUMER HOME PAGE !
                    
                if (user.role_id == 2):
                    return "hello service professional , yet to make page" # make service professional dashboard
                if (user.role_id == 1):
                    return "hello admin , yet to make admin dashboard "  # make admin dashboard page
            else:
                flash("invalid email or password")
                return redirect(url_for("login"))
        else:
            flash("User NOT FOUND , Please Register First")
            return redirect("/login")
    return render_template("login.html")

@app.route("/signout")
def signout():
    # session['signedin']= False
    session.pop('signedin',None )
    session.pop('firstname', None)  # Remove username from session
    session.pop("lastname",None)
    session.pop("role_id",None)
    session.pop("email",None)
    flash("You are Signed Out")
    return redirect('/')


#customer dashboard / homepage
@app.route("/user/home", methods=["GET"])
def user_home():
    if session["firstname"]:
        # Dummy data for services
        services = {
            'AC Repair': {'icon': 'fas fa-snowflake'},
            'Saloon': {'icon': 'fas fa-cut'},
            'Cleaning': {'icon': 'fas fa-broom'},
            'Electrician': {'icon': 'fas fa-bolt'},
            'Plumbing': {'icon': 'fas fa-faucet'},
        }
        
        # Dummy data for service history using pandas DataFrame
        service_history = pd.DataFrame({
            'Service Name': ['AC Repair', 'Cleaning', 'Electrician', 'Plumbing', 'Saloon'],
            'Professional Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Davis'],
            'Phone no.': ['123-456-7890', '234-567-8901', '345-678-9012', '456-789-0123', '567-890-1234'],
            'Status': ['Closed', 'Requested', 'In Progress', 'Closed', 'Scheduled']
        })
        
        return render_template("user_dashboard.html", services=services, service_history=service_history)

@app.route("/edit/customer_profile", methods=["GET","POST"])
def edit_customer_profile():
    # if request.method == "POST":

    return render_template("edit_customer_profile.html")    

@app.route("/user/home/bookings" , methods=["GET"])
def bookings():
    return "heres is your history of booking and active services"

@app.route("/admin_dashboard"  , methods=["GET"])
def admin_dashboard():
    return render_template("admin_dashboard.html")

    
if __name__ == "__main__":
    app.run(debug=True)
