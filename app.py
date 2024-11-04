from flask import Flask, render_template, request, redirect ,flash, url_for
from flask import session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
import pandas as pd
import uuid
import bcrypt

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sampledb4.sqlite3"
app.config['SECRET_KEY']="key"
db = SQLAlchemy(app)

app.app_context().push()

class User(db.Model):
    __tablename__= "User"
    uuid         = db.Column(db.String(), primary_key=True)
    email        = db.Column(db.String(), nullable =False , unique = True )
    password     = db.Column(db.String(), nullable=False)
    firstname    = db.Column(db.String(), nullable=False)
    lastname     = db.Column(db.String(), nullable=False)
    address      = db.Column(db.String(), nullable=False)
    pincode      = db.Column(db.Integer, nullable=False)
    role_id      = db.Column(db.Integer, nullable=False)  # 1 - admin , 2 - Professional , 3- customer
    phone_number = db.Column(db.Integer, nullable=False)
    created_at   = db.Column(db.Date, default = datetime.utcnow, nullable = True)
    updated_at   = db.Column(db.Date, default = datetime.utcnow, nullable = True)
    profile_image= db.Column(db.String() )
    customer_bookings = db.relationship('Bookings', foreign_keys='Bookings.cust_id', backref='customer', lazy=True) 
    def __init__(self, uuid , email, password, firstname, lastname, address, pincode, role_id, phone_number):
        self.uuid = uuid
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.firstname = firstname
        self.lastname =lastname
        self.pincode=pincode
        self.address=address 
        self.phone_number=phone_number
        self.role_id = role_id
        # self.profile_image=profile_image 
        # self.created_at = datetime.utcnow
        # self.updated_at = datetime.utcnow



    def check_password(self , password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)




class Professional(db.Model):
    __tablename__  = "Professional"
    email          = db.Column(db.String() , nullable =False , unique = True )
    uuid           = db.Column(db.String(),  db.ForeignKey("User.uuid") , primary_key=True)
    salary         = db.Column(db.Integer)
    experience     = db.Column(db.Integer, nullable=False)
    skill          = db.Column(db.String(),  nullable=False)
    total_bookings = db.Column(db.Integer, nullable=False)
    total_rating   = db.Column(db.Integer, nullable=False)
    status         = db.Column(db.Boolean , nullable=False , default = True  ) # active/inactive
    # add a column to store salary in previous job (maybe not needed)
    
    created_at     = db.Column(db.Date,default = datetime.utcnow , nullable=False)
    updated_at     = db.Column(db.Date,default = datetime.utcnow , nullable=False)
    professional_bookings = db.relationship('Bookings', foreign_keys='Bookings.professional_id', backref='professional', lazy=True) 


class Bookings(db.Model):
    __tablename__   = "Bookings"
    id              = db.Column(db.Integer, primary_key=True , autoincrement=True)
    status          = db.Column(db.String(), nullable=False ,default = "active")
    cust_id         = db.Column(db.String(), db.ForeignKey("User.uuid") ,  nullable=False)
    professional_id = db.Column(db.String() , db.ForeignKey("Professional.uuid") ) 
    service_id      = db.Column(db.Integer, db.ForeignKey("Services.id") ,  nullable=False)
    booking_date    = db.Column(db.Date, nullable=False ,  default = datetime.utcnow)
    completion_date = db.Column(db.Date)
    feedback        = db.Column(db.String())
    rating          = db.Column(db.Float, default=0)
    created_at      = db.Column(db.Date, default = datetime.utcnow)
    updated_at      = db.Column(db.Date, default = datetime.utcnow)

class Services(db.Model):
    __tablename__   = "Services"
    id              = db.Column(db.Integer, primary_key=True , autoincrement=True)
    name            = db.Column(db.String(), nullable=False)
    description     = db.Column(db.String(), nullable=False)
    category_id     = db.Column(db.Integer, db.ForeignKey("ServiceCategory.id"), nullable=False)
    price           = db.Column(db.Integer, nullable=False)
    duration        = db.Column(db.Integer, nullable=False)
    rating          = db.Column(db.Float, default=0 ) 
    status          = db.Column(db.Boolean, default =True ) # service_status = active/inactive
    created_at      = db.Column(db.Date,default = datetime.utcnow , nullable=False)
    updated_at      = db.Column(db.Date,default = datetime.utcnow , nullable=False)

class  ServiceCategory(db.Model):
    __tablename__   = "ServiceCategory"
    id              = db.Column(db.Integer, primary_key=True,  autoincrement=True)
    name            = db.Column(db.String(), nullable=False)  # category name
    # service_id      = db.Column(db.Integer ,  db.ForeignKey("Services.id"), nullable=False)
    services        = db.relationship("Services" ,  backref="category"  ,lazy=True,cascade="all,delete" ) 
    created_at      = db.Column(db.Date ,default = datetime.utcnow )

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

#-------------------------------
@app.route("/fill")
def fill_tables():
    print(1)
    print()

    new_category1=ServiceCategory(name="cleaning")
    new_category2=ServiceCategory(name="electrical")
    new_category3=ServiceCategory(name="plumbing")
    new_category4=ServiceCategory(name="maintainance")
    db.session.add(new_category1)
    db.session.add(new_category2)
    db.session.add(new_category3)
    db.session.add(new_category4)
    db.session.commit()

    new_service_1 = Services(name="room cleaning" , category_id = 0 , price=1000 , description ="cleaning of rooms" ,
                         duration=1)
    new_service_2 = Services(name="home cleaning" , category_id = 0 , price=1000 , description ="cleaning of home" ,
                         duration=1)
    new_service_2 = Services(name="house cleaning" , category_id = 0 , price=1000 , description ="cleaning of house" ,
                         duration=1)
    new_service_3 = Services(name="toilet cleaning" , category_id = 0 , price=1000 , description ="cleaning of toilet" ,
                         duration=1)
    new_service_4 = Services(name="Ac Repair & Service" , category_id = 1 , price=1000 , description ="Ac Repair & Service" ,
                         duration=1)
    new_service_5 = Services(name="Gyser Repair & Service" , category_id = 1 , price=1000 , description ="Gyser Repair & Service" ,
                         duration=1)
    new_service_6 = Services(name="Pipe fitings" , category_id = 2 , price=1000 , description ="Pipe fitings" ,
                         duration=1)
    new_service_7 = Services(name="plumbing related" , category_id = 2 , price=1000 , description ="plumbing related" ,
                         duration=1)
    new_service_8 = Services(name="wall repair" , category_id = 3 , price=1000 , description ="repairing of walls" ,
                         duration=1)
    db.session.add_all([new_service_1,new_service_2,new_service_3,new_service_4,new_service_5,new_service_6,new_service_7,new_service_8])
    db.session.commit()
    id=uuid.uuid4()
    customer1 = User(uuid = str(id) ,email="p1@gmail.com" , password = "1234" , firstname="p1", lastname="p1",
                                address="address" , pincode="111111", phone_number=1234567890
                    ,role_id = 3  )
    
    id1=1
    admin= User(uuid = str(id1) ,email="admin@gmail.com" , password = "1111" , firstname="admin", lastname="admin",
                                address="address" , pincode="111111", phone_number=1234567890
                    ,role_id = 1 )
    db.session.add_all([customer1 , admin] )
    db.session.commit()
    return "done"


#-------------------------------

@app.route("/" , methods= ["GET"])
def home():
    return render_template("homepage.html")

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
            flash( "Email Id Already in Use, please sign in" ,"error")
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
                                address=address , pincode=pincode, phone_number=phone_number
                                # ,created_at=datetime.utcnow(), updated_at=datetime.utcnow()
                                ,role_id = 3 , profile_image=profile_image  )

        db.session.add(new_registration)
        db.session.commit()

        
        # user = User.query.filter_by(email=email).first()      ____
        #                                                             |___               
        # session['user'] = user.id                             ____|

        flash( "REGISTERED SUCCESSFULLY !" ,"success" )
        return redirect(url_for("login")) # REDIRECT TO LOGIN PAGE !
       

    return render_template("/customer/customer_registration_form.html")
    


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
                flash( "Email Id Already in Use, please sign in" , "error" )
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
        

        new_professional_registration= Professional(uuid=str(id), email=email,salary=salary , skill=skill , experience=experience , total_bookings=0 , 
                                                total_rating=0 ,created_at=datetime.utcnow(), updated_at=datetime.utcnow() 
                                                )
        
        db.session.add(new_professional_registration)
        db.session.add(new_user_registration)
        db.session.commit()

        
        # user = User.query.filter_by(email=email).first()      ____
        #                                                             |___               
        # session['user'] = user.id                             ____|

        flash( "REGISTERED SUCCESSFULLY !" , "success" )
        return redirect(url_for("login")) # REDIRECT TO  LOGIN PAGE !
    
    return render_template("/professional/professional_registeration_form.html")  # make a seperate register page for Professional



# common for both cust and prof
@app.route("/login" , methods =["GET" , "POST"])
def login():
    
    if "firstname" in session:
        flash("Please Sign Out First"),400
        return redirect(url_for("customer_dashboard"))
     
    if (request.method == "POST"):
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        # if not then register
        if not user:
            flash("please create account first" , "info"),400
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
                    return redirect("/customer/dashboard" )   ## REDIRECT TO COSTUMER HOME PAGE !
                    
                if (user.role_id == 2):
                    return "hello service professional , yet to make page" # make service professional dashboard
                if (user.role_id == 1):
                    return redirect("/admin/dashboard") # make admin dashboard page
            else:
                flash("invalid email or password" , "error")
                return redirect(url_for("login"))
        else:
            flash("User NOT FOUND , Please Register First", "error")
            return redirect("/")
        
    # return redirect("/")
    return render_template("login.html")

@app.route("/signout")
def signout():
    # session['signedin']= False
    session.pop('signedin',None )
    session.pop('firstname', None)  # Remove username from session
    session.pop("lastname",None)
    session.pop("role_id",None)
    session.pop("email",None)
    flash("You are Signed Out" , "info" )
    return redirect('/')


#customer dashboard / homepage
# @app.route("/customer/dashboard", methods=["GET"])
# def customer_dasboard():
#     if session["firstname"]:
#         # # Dummy data for services
#         # services = {
#         #     'AC Repair': {'icon': 'fas fa-snowflake'},
#         #     'Saloon': {'icon': 'fas fa-cut'},
#         #     'Cleaning': {'icon': 'fas fa-broom'},
#         #     'Electrician': {'icon': 'fas fa-bolt'},
#         #     'Plumbing': {'icon': 'fas fa-faucet'},
#         # }
        
#         # # Dummy data for service history using pandas DataFrame
#         # service_history = pd.DataFrame({
#         #     'Service Name': ['AC Repair', 'Cleaning', 'Electrician', 'Plumbing', 'Saloon'],
#         #     'Professional Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Davis'],
#         #     'Phone no.': ['123-456-7890', '234-567-8901', '345-678-9012', '456-789-0123', '567-890-1234'],
#         #     'Status': ['Closed', 'Requested', 'In Progress', 'Closed', 'Scheduled']
#         # })
#         user = User.query.filter_by(email=session["email"]).first()
#         past_bookings = [booking  for booking in user.customer_bookings if booking.completion_date ]
#         upcoming_bookings = [booking  for booking in user.customer_bookings if not booking.completion_date ]
#         # return render_template("user_dashboard.html", services=services, service_history=service_history)
#         return render_template("/customer/customer_dashboard.html" ,past_bookings = past_bookings,upcoming_bookings=upcoming_bookings)
#     else:
#         flash("You are not signed in" , "error")
#         return redirect('/')
@app.route("/customer/dashboard", methods=["GET"])
def customer_dashboard():
    if "firstname" in session:
        # Retrieve the current user from the database using their UUID stored in the session
        user = User.query.filter_by(email=session["email"]).first()

        if user:
            services = Services.query.limit(8).all()
            past_bookings = [booking for booking in user.customer_bookings if booking.completion_date]
            upcoming_bookings = [booking for booking in user.customer_bookings if not booking.completion_date]

            return render_template("/customer/customer_dashboard.html", services=services ,past_bookings=past_bookings, upcoming_bookings=upcoming_bookings)
        else:
            flash("User not found", "error")
            return redirect('/')
    else:
        flash("You are not signed in", "error")
        return redirect('/')
    

@app.route('/service/<int:service_id>')
def view_service(service_id):
    # Fetch the specific service details from the database
    service = Services.query.get_or_404(service_id)
    return render_template('view_service.html', service=service)

@app.route('/book_service/<int:service_id>')
def book_service(service_id):
    # Fetch the specific service details and handle booking logic here
    service = Services.query.get_or_404(service_id)
    # You can implement the booking logic or redirect to a booking form
    return render_template('book_service.html', service=service)

# @app.route("/customer/booking" , methods=[ "GET","POST"])
# def  customer_booking():
#     if(request.method=="POST" ):
#         if session["firstname"]:
#             # Get the service name from the form data
#             service_id = request.form.get('service_id')
#             customer_id=session["uuid"]

#             booking = Bookings(service_id = service_id , cust_id=customer_id )

#             db.session.add(booking)
#             db.session.commit()
#             flash("Booking Successful" , "success")
#             return redirect('/customer/dashboard')
#     return render_template('/customer/book_service')

@app.route("/edit/customer_profile", methods=["GET","POST"])
def edit_customer_profile():
    # if request.method == "POST":

    return render_template("/customer/edit_customer_profile.html")    

@app.route("/user/dashboard/bookings" , methods=["GET"])
def bookings():
    return "heres is your history of booking and active services"

@app.route("/admin/dashboard"  , methods=["GET"])
def admin_dashboard():
    return render_template("/admin/admin_dashboard.html")

@app.route("/admin/add_service"  , methods=["GET" , "POST"])
def add_service():
    if(request.method =="POST"):
        service_name=request.form.get("name")
        category_id=request.form.get("category_id")
        price=request.form.get("price")
        description=request.form.get("description")
        duration=request.form.get("duration")
        service=Services(name=service_name , category_id = category_id , price=price , description =description ,
                         duration=duration)
        db.session.add(service)
        db.session.commit()
        flash("Service Added Successfully" , "success")
        return(redirect("/admin/dashboard"))
    return render_template("/admin/add_service.html")



if __name__ == "__main__":
    app.run(debug=True)
