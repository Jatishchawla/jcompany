from flask import Flask, render_template, request, redirect ,flash, url_for , jsonify
from flask import session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import uuid
import bcrypt
import os
from sqlalchemy import func
from matplotlib import rcParams
from sqlalchemy.inspection import inspect
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sampledb1.sqlite3"
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
    complaints_count = db.Column(db.Integer, default=0)
    created_at   = db.Column(db.Date, default = datetime.utcnow)
    updated_at   = db.Column(db.Date, default = datetime.utcnow )
    status       = db.Column(db.Boolean  , default = True  ) # active/inactive


    customer_bookings = db.relationship('Bookings', foreign_keys='Bookings.cust_id', back_populates='customer', lazy=True) 
    # professional = db.relationship('Professional', uselist=False, back_populates='user')
    
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
       

    def check_password(self , password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)




class Professional(db.Model):
    __tablename__  = "Professional"
    uuid           = db.Column(db.String(),  db.ForeignKey("User.uuid") , primary_key=True)
    salary         = db.Column(db.Integer)
    experience     = db.Column(db.Integer, nullable=False)
    skill          = db.Column(db.String(),  nullable=False) 
    rating_sum     = db.Column(db.Integer, default=0)
    rated_services = db.Column(db.Integer, default=0) 
    status         = db.Column(db.Boolean , nullable=False , default = False  ) # active/inactive
    cv_path        = db.Column(db.String(255) )
    active_booking_count= db.Column(db.Integer, default=0)
    created_at     = db.Column(db.Date,default = datetime.utcnow )
    updated_at     = db.Column(db.Date,default = datetime.utcnow )
    user = db.relationship("User" , backref="professional" , cascade="all, delete" , lazy=True)

    # professional_bookings = db.relationship('Bookings', foreign_keys='Bookings.professional_id', backref='professional', lazy=True) 

class Bookings(db.Model):
    __tablename__   = "Bookings"
    id              = db.Column(db.Integer, primary_key=True , autoincrement=True)
    cust_id         = db.Column(db.String(), db.ForeignKey("User.uuid") , nullable=True )
    professional_id = db.Column(db.String() , db.ForeignKey("Professional.uuid") ) 
    service_id      = db.Column(db.Integer, db.ForeignKey("Services.id") )
    status          = db.Column(db.String(), nullable=False ,default = "active")
    booking_date    = db.Column(db.Date, nullable=False ,  default = datetime.utcnow)
    request_date    = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    feedback        = db.Column(db.String())
    rating          = db.Column(db.Integer, default=0)

    service = db.relationship("Services", backref="bookings", lazy=True )
    customer = db.relationship("User", back_populates="customer_bookings", lazy=True)   #customer
    professional = db.relationship("Professional" , backref="bookings" ,  lazy=True)

    # created_at      = db.Column(db.Date, default = datetime.utcnow) 
    updated_at      = db.Column(db.Date, default = datetime.utcnow )

class Services(db.Model):
    __tablename__   = "Services"
    id              = db.Column(db.Integer, primary_key=True , autoincrement=True)
    name            = db.Column(db.String(), nullable=False)
    description     = db.Column(db.String(), nullable=False)
    category_id     = db.Column(db.Integer, db.ForeignKey("ServiceCategory.id"), nullable=False)
    price           = db.Column(db.Integer, nullable=False)
    duration        = db.Column(db.Integer, nullable=False)
    rated_services  = db.Column(db.Integer, default=0 )
    rating_sum      = db.Column(db.Integer, default=0 )
    status          = db.Column(db.Boolean, default =True ) # service_status = active/inactive
    location        = db.Column(db.String())
    pincode         = db.Column(db.Integer)


    created_at      = db.Column(db.Date,default = datetime.utcnow)
    updated_at      = db.Column(db.Date,default = datetime.utcnow )
    category = db.relationship("ServiceCategory", back_populates="services") 
    # category        = db.relationship("ServiceCategory" , backref="services" , lazy=True)

class  ServiceCategory(db.Model):
    __tablename__   = "ServiceCategory"
    id              = db.Column(db.Integer, primary_key=True,  autoincrement=True)
    name            = db.Column(db.String(), nullable=False)  
    created_at      = db.Column(db.Date ,default = datetime.utcnow )
    services        = db.relationship("Services" ,  back_populates="category"  ,lazy=True, cascade="all,delete" ) 
    # updated_at      = db.Column(db.Date ,default = datetime.utcnow )

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

    new_category1=ServiceCategory(name="cleaning")
    new_category2=ServiceCategory(name="electrical")
    new_category3=ServiceCategory(name="plumbing")
    new_category4=ServiceCategory(name="maintenance")
    
    db.session.add(new_category1)
    db.session.add(new_category2)
    db.session.add(new_category3)
    db.session.add(new_category4)
    db.session.commit()

    new_categories = [
        ServiceCategory(name="health & wellness"), #5
        ServiceCategory(name="beauty & personal care"),#6
        ServiceCategory(name="automotive services"),#7
        ServiceCategory(name="technology support"),#8
        ServiceCategory(name="home improvement"),#9
        ServiceCategory(name="education & tutoring"),#10
        ServiceCategory(name="professional services"),#11
        ServiceCategory(name="pest control"),#12
        ServiceCategory(name="pet care"),#13
        ServiceCategory(name="event services"),#14
        ServiceCategory(name="fitness & sports"),#15
        ServiceCategory(name="moving & relocation"),#16
        ServiceCategory(name="appliance repair"),#17
        ServiceCategory(name="security services"),#18
        ServiceCategory(name="childcare"),#19
        ServiceCategory(name="gardening & landscaping"),#20
        ServiceCategory(name="legal & documentation"),#21
        ServiceCategory(name="photography & videography"),#22
        ServiceCategory(name="transportation & delivery"),#23
        ServiceCategory(name="waste management"),#24
        ServiceCategory(name="handyman services")#25
    ]

    db.session.add_all(new_categories)
    db.session.commit()



    new_service_1 = Services(name="room cleaning" , category_id = 1 , price=1000 , description ="cleaning of rooms" , location = "ambala" ,pincode = 134023 ,
                         duration=1)
    new_service_2 = Services(name="home cleaning" , category_id = 1 , price=3000 , description ="cleaning of home" ,
                         duration=4 , location ="ambala" , pincode = 111111)
    new_service_3 = Services(name="ofiice cleaning" , category_id = 1 , price=2000 , description ="cleaning of office" ,
                         duration=1 , location ="ambala" , pincode = 111111 )
    new_service_4 = Services(name="toilet cleaning" , category_id = 1 , price=500 , description ="cleaning of toilet" ,
                         duration=1 , location ="ambala" , pincode = 111111 )
    new_service_5 = Services(name="Ac Repair & Service" , category_id = 2 , price=1000 , description ="Ac Repair & Service" ,
                         duration=1 , location ="ambala" , pincode = 111111 )
    new_service_6 = Services(name="Gyser Repair & Service" , category_id = 2 , price=1000 , description ="Gyser Repair & Service" ,
                         duration=1 , location ="ambala" , pincode = 111111 )
    new_service_7 = Services(name="Pipe fitings" , category_id = 3 , price=1000 , description ="Pipe fitings" ,
                         duration=1 , location ="chennai" , pincode = 600001 )
    new_service_8 = Services(name="plumbing related" , category_id = 3 , price=1000 , description ="plumbing related" ,
                         duration=1 , location ="chennai" , pincode = 600001 )
    new_service_9 = Services(name="wall repair" , category_id = 4 , price=1000 , description ="repairing of walls" ,
                         duration=1 , location ="connaught place" , pincode = 110000 )
    db.session.add_all([new_service_1,new_service_2,new_service_3,new_service_4,new_service_5,new_service_6,new_service_7,new_service_8,new_service_9])
    db.session.commit()

    new_services = [
        # Cleaning Services
        Services(name="deep cleaning", category_id=1, price=5000, description="thorough cleaning of the entire home", duration=3, location ="ambala" , pincode = 111111 ),
        Services(name="window cleaning", category_id=1, price=800, description="cleaning windows inside and out", duration=2, location ="ambala" , pincode = 111111 ),
        Services(name="carpet cleaning", category_id=1, price=1500, description="professional carpet cleaning", duration=2, location ="ambala" , pincode = 111111 ),
        
        # Electrical Services
        Services(name="wiring installation", category_id=2, price=3000, description="new wiring for your home", duration=4, location ="chandigarh" , pincode = 160017 ),
        Services(name="lighting installation", category_id=2, price=1200, description="installation of indoor and outdoor lighting", duration=2, location ="chandigarh" , pincode = 160017 ),
        Services(name="outlet repair", category_id=2, price=500, description="repair faulty electrical outlets", duration=1, location ="chandigarh" , pincode = 160017 ),
        
        # Plumbing Services
        Services(name="faucet installation", category_id=3, price=700, description="installing new faucets", duration=1, location ="chennai" , pincode = 600001 ),
        Services(name="drain cleaning", category_id=3, price=1000, description="cleaning clogged drains", duration=1, location ="ambala" , pincode = 111111 ),
        Services(name="water heater installation", category_id=3, price=2500, description="installing a new water heater", duration=3, location ="connaught place" , pincode = 110000 ),
        
        # Maintenance Services
        Services(name="home maintenance checkup", category_id=4, price=1500, description="annual maintenance check for your home", duration=2, location ="connaught place" , pincode = 110000 ),
        Services(name="furniture assembly", category_id=4, price=800, description="assembling furniture from flat-pack", duration=1, location ="ambala" , pincode = 111111 ),
        
        # Health & Wellness Services
        Services(name="personal training", category_id=5, price=1500, description="one-on-one personal training sessions", duration=1, location ="ambala" , pincode = 111111 ),
        Services(name="yoga classes", category_id=5, price=1200, description="group yoga sessions", duration=1.5, location ="ambala" , pincode = 111111 ),
        
        # Beauty & Personal Care Services
        Services(name="haircut & styling", category_id=6, price=500, description="professional haircut and styling", duration=1, location ="ambala" , pincode = 111111 ),
        Services(name="makeup services", category_id=6, price=1200, description="professional makeup for events", duration=2, location ="ambala" , pincode = 111111 ),
        
        # Automotive Services
        Services(name="car wash", category_id=7, price=400, description="full exterior and interior car wash", duration=1, location ="ambala" , pincode = 111111 ),
        Services(name="oil change", category_id=7, price=1000, description="oil change and filter replacement", duration=1, location ="ambala" , pincode = 111111 ),
        
        # Technology Support Services
        Services(name="computer setup", category_id=8, price=1500, description="setting up new computers and peripherals", duration=2, location ="ambala" , pincode = 111111 ),
        Services(name="virus removal", category_id=8, price=800, description="removing viruses and malware from computers", duration=1, location ="ambala" , pincode = 111111 ),

        # More services can be added similarly...
         Services(name="interior painting", category_id=9, price=3500, description="painting the interior of the home", duration=4, location ="ambala" , pincode = 111111 ),
        Services(name="flooring installation", category_id=9, price=4000, description="installing hardwood, laminate, or tile flooring", duration=5, location ="ambala" , pincode = 111111 ),

        # Education & Tutoring Services
        Services(name="online tutoring", category_id=10, price=800, description="one-on-one online tutoring sessions", duration=1, location ="ambala" , pincode = 111111 ),
        Services(name="homework help", category_id=10, price=600, description="assistance with homework and assignments", duration=1, location ="ambala" , pincode = 111111 ),

        # Professional Services
        Services(name="legal consultation", category_id=11, price=3000, description="consultation with a legal expert", duration=1, location ="ambala" , pincode = 111111 ),
        Services(name="financial planning", category_id=11, price=2000, description="personal financial planning services", duration=2, location ="ambala" , pincode = 111111 ),

        # Pest Control Services
        Services(name="general pest control", category_id=12, price=1500, description="treatment for common pests", duration=2, location ="ambala" , pincode = 111111 ),
        Services(name="termite inspection", category_id=12, price=2000, description="inspection for termite infestations", duration=1.5, location ="ambala" , pincode = 111111 ),

        # Pet Care Services
        Services(name="dog walking", category_id=13, price=500, description="daily dog walking services", duration=1, location ="ambala" , pincode = 111111 ),
        Services(name="pet grooming", category_id=13, price=1200, description="grooming services for pets", duration=1.5, location ="ambala" , pincode = 111111 ),

        # Event Services
        Services(name="event planning", category_id=14, price=5000, description="complete event planning services", duration=8, location ="ambala" , pincode = 111111 ),
        Services(name="catering services", category_id=14, price=3000, description="catering for events and parties", duration=3, location ="ambala" , pincode = 111111 ),

        # Fitness & Sports Services
        Services(name="personal training sessions", category_id=15, price=1500, description="personal training for fitness goals", duration=1, location ="ambala" , pincode = 111111 ),
        Services(name="group fitness classes", category_id=15, price=800, description="join group fitness sessions", duration=1, location ="ambala" , pincode = 111111 ),

        # Moving & Relocation Services
        Services(name="local moving", category_id=16, price=3000, description="moving services within the local area", duration=4, location ="ambala" , pincode = 111111 ),
        Services(name="packing services", category_id=16, price=1200, description="packing services for relocations", duration=2, location ="ambala" , pincode = 111111 ),

        # Appliance Repair Services
        Services(name="washing machine repair", category_id=17, price=1500, description="repair services for washing machines", duration=2, location ="ambala" , pincode = 111111 ),
        Services(name="refrigerator repair", category_id=17, price=2000, description="repair services for refrigerators", duration=3, location ="ambala" , pincode = 111111 ),

        # Security Services
        Services(name="home security installation", category_id=18, price=2500, description="installation of home security systems", duration=3, location ="ambala" , pincode = 111111 ),
        Services(name="security patrol services", category_id=18, price=3000, description="security patrol for properties", duration=4, location ="ambala" , pincode = 111111 ),

        # Childcare Services
        Services(name="nanny services", category_id=19, price=2000, description="full-time or part-time nanny services", duration=8, location ="ambala" , pincode = 111111 ),
        Services(name="babysitting services", category_id=19, price=800, description="occasional babysitting services", duration=2, location ="ambala" , pincode = 111111 ),

        # Gardening & Landscaping Services
        Services(name="lawn care", category_id=20, price=1000, description="care and maintenance of lawns", duration=2, location ="ambala" , pincode = 111111 ),
        Services(name="landscaping design", category_id=20, price=3000, description="designing and installing landscapes", duration=4, location ="ambala" , pincode = 111111 ),

        # Legal & Documentation Services
        Services(name="will writing", category_id=21, price=1500, description="writing legal wills", duration=2),
        Services(name="contract drafting", category_id=21, price=2500, description="drafting contracts and agreements", duration=3, location ="ambala" , pincode = 111111 ),

        # Photography & Videography Services
        Services(name="event photography", category_id=22, price=4000, description="photography for events", duration=4, location ="ambala" , pincode = 111111 ),
        Services(name="video editing services", category_id=22, price=2500, description="editing video content for clients", duration=3, location ="ambala" , pincode = 111111 ),

        # Transportation & Delivery Services
        Services(name="parcel delivery", category_id=23, price=800, description="delivery of parcels and packages", duration=1, location ="ambala" , pincode = 111111 ),
        Services(name="airport transfer services", category_id=23, price=2500, description="transfers to and from the airport", duration=2, location ="ambala" , pincode = 111111 ),

        # Waste Management Services
        Services(name="garbage collection", category_id=24, price=1000, description="regular garbage collection services", duration=2, location ="ambala" , pincode = 111111 ),
        Services(name="recycling services", category_id=24, price=800, description="recycling of various materials", duration=1, location ="ambala" , pincode = 111111 ),

        # Handyman Services
        Services(name="furniture repair", category_id=25, price=1200, description="repairing and restoring furniture", duration=2, location ="ambala" , pincode = 111111 ),
        Services(name="small home repairs", category_id=25, price=800, description="handling minor repairs around the house", duration=1, location ="ambala" , pincode = 111111 )

    ]

    db.session.add_all(new_services)
    db.session.commit()
    
    return redirect("/")

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads/cv_files'   # Directory to save uploaded CVs 
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#-------------------------------
@app.route("/" , methods= ["GET"])
def home():
    categories=ServiceCategory.query.all()
    return render_template("homepage.html",categories=categories)

# for customer
@app.route("/register" , methods =["GET",  "POST"])
def register():
    
    if (request.method == "POST"):
        email = request.form.get("email")
        password = request.form.get("password")  
        # Ensure password is not None or empty
        if not password:
            flash("Password Required")
            return redirect("/register")
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash( "Email Id Already in Use, please sign in" ,"error")
            return redirect(url_for('login'))
        
        id=uuid.uuid4()
        # db wala code
        firstname = request.form.get("firstname")
        lastname     =request.form.get("lastname")
        address      =request.form.get("address")
        pincode      =request.form.get("pincode")
        phone_number =request.form.get("phonenumber")
        
        new_registration = User(uuid = str(id) ,email=email , password = password , firstname=firstname, lastname=lastname,
                                address=address , pincode=pincode, phone_number=phone_number
                                ,role_id = 3   )

        db.session.add(new_registration)
        db.session.commit()

        flash( "REGISTERED SUCCESSFULLY !" ,"success" )
        return redirect(url_for("login")) # REDIRECT TO LOGIN PAGE !
       
    categories=ServiceCategory.query.all()
    return render_template("/customer/customer_registeration_form.html",categories=categories)
    
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
            return redirect("/professional/register")
        
        user = User.query.filter_by(email=email).first()
        if user:
            if (email == user.email):
                flash( "Email Id Already in Use, please sign in" , "error" )
                return redirect(url_for('login'))
        
        # db wala code
        id = uuid.uuid4()
        firstname    = request.form.get("firstname")
        lastname     =request.form.get("lastname")
        role_id      = 2
        address      =request.form.get("address")
        pincode      =request.form.get("pincode")
        phone_number =request.form.get("phonenumber")
        
        experience   = request.form.get("experience")
        skill        =request.form.get("skill")

        cv_file = request.files.get("cv")
        if not cv_file:
            flash("No file selected. Please upload your CV.", "danger")
            return redirect(url_for("professional_register"))

        if cv_file and allowed_file(cv_file.filename):
            filename = secure_filename(cv_file.filename)
            cv_path = app.config['UPLOAD_FOLDER']+"/"+ filename  
            cv_file.save(cv_path)
        else:
            flash("Invalid CV file. Please upload a PDF, DOC, or DOCX file.", "danger")
            return redirect("/professional/register")

        
        new_user_registration = User(uuid=str(id), email=email , password = password , firstname=firstname, lastname=lastname,
                                address=address , pincode=pincode, phone_number=phone_number,
                                role_id = 2  )
        

        new_professional_registration= Professional(uuid=str(id), skill=skill , experience=experience,cv_path=cv_path)
        
        db.session.add(new_professional_registration)
        db.session.add(new_user_registration)
        db.session.commit()
        user = User.query.filter_by(email=email).first()
        user.status=False
        db.session.commit()

        flash( "REGISTERED SUCCESSFULLY !" , "success" )
        return redirect(url_for("login")) # REDIRECT TO  LOGIN PAGE !
    categories=ServiceCategory.query.all()
    return render_template("/professional/professional_registeration_form.html" , categories=categories)  # make a seperate register page for Professional

# common for Admin , Cust and Prof
@app.route("/login" , methods =["GET" , "POST"])
def login():
    
    if "firstname" in session:
        flash("Please Sign Out First","info")
        return redirect("/")
     
    if (request.method == "POST"):
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        # if not then register
        if not user:
            flash("please create account first" , "info")
            return redirect(url_for("register"))

        if user:
            if not user.status:
                flash("Your account is Not Verfied or Terminated " , "danger")
                return redirect("/")

            if (email == user.email and user.check_password(password) ):
                # session['user'] = user.id      ---YET TO MAKE SESSION---
                session['firstname']=user.firstname
                session['lastname']=user.lastname
                session['uuid']=user.uuid
                session['email']=user.email
                session['role_id']=user.role_id
                session['address']=user.address
                session['phone_number']=user.phone_number
                session['signedin']=True

                if (user.role_id == 3 ):
                    return redirect("/customer/dashboard" )   ## REDIRECT TO COSTUMER HOME PAGE !
                    
                if (user.role_id == 2):
                    return redirect("/professional/dashboard") # make service professional dashboard
                if (user.role_id == 1):
                    return redirect("/admin/dashboard") # make admin dashboard page
            else:
                flash("invalid email or password" , "error")
                return redirect(url_for("login"))
        else:
            flash("User NOT FOUND , Please Register First", "error")
            return redirect("/")
        
    categories=ServiceCategory.query.all()
    return render_template("login.html",categories=categories)

@app.route("/signout")
def signout():
    # session['signedin']= False
    session.pop('signedin',None )
    session.pop('uuid',None )
    session.pop('firstname', None)  # Remove username from session
    session.pop("lastname",None)
    session.pop("role_id",None)
    session.pop("email",None)
    session.pop("address",None)
    session.pop("phone_number",None)
    flash("You are Signed Out" , "info" )
    return redirect('/')

@app.route("/summary",methods=["GET","POST"])
def summary():
    if "role_id" in session:
        if(session["role_id"]==2):
            prof_id = session["uuid"]
            service_count_plot = generate_service_count_chart(prof_id)
            service_count_plot.savefig(f"./static/images/professional_{prof_id}_service_count.jpeg")
            service_count_plot.clf()

            # Generate Average Ratings Pie Chart
            avg_rating_plot = generate_avg_rating_chart(prof_id)
            avg_rating_plot.savefig(f"./static/images/professional_{prof_id}_avg_rating.jpeg")
            avg_rating_plot.clf()
            generate_avg_rating_by_skill_plot = generate_avg_rating_by_skill_chart(prof_id)
            generate_avg_rating_by_skill_plot.savefig(f"./static/images/professional_{prof_id}_service_avg_rating.jpeg")
            generate_avg_rating_by_skill_plot.clf()

            service_history=Bookings.query.filter(Bookings.professional_id == prof_id, Bookings.status != "accepted" ).all()
            return render_template("/professional/professional_summary.html",service_history=service_history , prof_id=prof_id)
        if(session["role_id"] ==3 ):
            customer_id = session["uuid"]  
           
            customer_booking = generate_customer_booking_chart(customer_id)
            customer_booking.savefig(f"./static/images/customer_booking_{customer_id}.jpeg")
            customer_booking.clf()

            service_history=Bookings.query.filter(Bookings.cust_id == customer_id, Bookings.status=="closed" ).all()
            return render_template("/customer/customer_summary.html" , customer_id=customer_id)
        if(session["role_id"]==1):
            return redirect("/admin-summary")
    return redirect("/") 

# aboutus route
@app.route("/aboutus")
def aboutus():
    return render_template("/aboutus.html")

# complaints count increase
@app.route("/complaint/<string:report_id>",methods=["GET","POST"])
def complaints(report_id):
    if "role_id" in session:
        user=User.query.get(report_id)
        if user:
            user.complaints_count =user.complaints_count +1
            db.session.commit()
            flash("Reported Successfully" , "success" )
    else:
        flash("An Error Occured")
    return redirect('/')
            
@app.route("/professional/dashboard")
def professional_dashboard():
    if(session):
        if(session["role_id"]==2):
            professional=Professional.query.get(session["uuid"])
            active_services = Bookings.query.join(Services).join(ServiceCategory).filter(
                ServiceCategory.name == professional.skill ,Bookings.status=="active").all()
            service_history=Bookings.query.join(Services).join(ServiceCategory).filter(
                Bookings.professional_id ==professional.uuid, Bookings.status!="accepted"  ).all()
            assigned_services=Bookings.query.filter(
                Bookings.professional_id ==professional.uuid, Bookings.status=="accepted"  ).all()

            # services=Bookings.query.filter_by(Bookings.service.category_id=user.skill)
            # add category_id in professional table
            # make dropdown options for skills in register form of  professional
            # admin can add new categories , add column status , in category 
            # show only  active categories in dropdown options
            # 1 professional can accept upto 3 request at any point
         
            if professional:
                filter_by = request.args.get('filter', '').strip()
                search_query = request.args.get('query', '').strip()
                if search_query or filter_by:

                    query = Bookings.query.join(Services).join(ServiceCategory).join(User).filter( User.uuid == Bookings.cust_id,
                        Bookings.professional_id == professional.uuid, Bookings.status!="accepted")

                    if filter_by == "name":
                        query = query.filter(Services.name.ilike(f"%{search_query}%")).order_by(Services.name.asc())
                    elif filter_by == "address":
                        query = query.filter(User.address.ilike(f"%{search_query}%")) 
                    elif filter_by == "pincode":
                        if search_query.isdigit():
                            query = query.filter(User.pincode == int(search_query))
                    elif filter_by == "date":
                        query = query.filter(Bookings.request_date == search_query).order_by(Bookings.request_date.asc())
                    else:
                        flash("Invalid filter selected.", "danger")
                        return redirect("/professional/dashboard")
                    service_history=query.all()
                
                return render_template("/professional/professional_dashboard.html",professional=professional  ,today_services=active_services , service_history=service_history, assigned_services=assigned_services)
            else:
                flash("user not found" , "error")
                return redirect("/professional/dashboard")
        else:
            flash("Only Professionals are allowed" , "error")
            return redirect("/")
    else:
        flash("You are not signed in" , "error")
        return redirect("/")

@app.route('/reject_booking/<int:booking_id>/<string:professional_id>', methods=["GET" , "POST"])
def reject_booking(booking_id , professional_id):

    booking = Bookings.query.get_or_404(booking_id)

    if booking.status == "active" and booking.professional_id != professional_id:
        flash(f"This booking does not belongs to you", "info")
        return redirect(url_for('professional_dashboard'))
    if ("role_id" not in session or session["role_id"] != 2 ):
        flash('You do not have permission to perform this action', 'danger')
        return redirect("/")
    
    professional=Professional.query.filter(Professional.uuid == professional_id).first()

    booking.status = "active"
    booking.professional_id=None
    booking.updated_at=datetime.utcnow()
    professional.active_booking_count= professional.active_booking_count - 1
    db.session.commit()

    flash("Booking rejected successfully!", "success")
    return redirect("/professional/dashboard")

@app.route('/accept_booking/<int:booking_id>/<string:professional_id>', methods=['POST'])
def accept_booking(booking_id , professional_id):

    booking = Bookings.query.get_or_404(booking_id)

    if booking.status == "accepted":
        flash(f"This booking has already been accepted by {booking.professional.name} ", "info")
        return redirect(url_for('professional_dashboard'))
    if ("role_id" not in session or session["role_id"] != 2 ):
        flash('You do not have permission to perform this action', 'danger')
        return redirect("/")
    
    professional=Professional.query.filter(Professional.uuid == professional_id).first()
    if professional.active_booking_count<3:

        booking.status = "accepted"
        booking.professional_id=professional_id
        booking.updated_at=datetime.utcnow()
        professional.active_booking_count= professional.active_booking_count + 1
        db.session.commit()

        flash("Booking accepted successfully!", "success")
        return redirect("/professional/dashboard")
    else:
        flash("You have already accepted 3 bookings today" , "error")
        return redirect("/professional/dashboard")

@app.route("/customer/dashboard", methods=["GET"])
def customer_dashboard():
    if "firstname" in session and session["role_id"]==3:
        # Retrieve the current user from the database using their UUID stored in the session
        user = User.query.filter_by(email=session["email"]).first()

        if user:
            categories=ServiceCategory.query.filter().order_by(ServiceCategory.name.asc()).all()
            services = Services.query.filter(Services.status == True ).limit(8).all()
            all_bookings = [booking for booking in user.customer_bookings ]
            upcoming_bookings = [booking for booking in user.customer_bookings if (not booking.completion_date and booking.status != "canceled")]
                    
            # CREATE VIEW active_professionals AS
            # SELECT p.uuid AS professional_id
            # FROM professionals p
            # LEFT JOIN bookings b ON p.uuid = b.professional_id
            # WHERE b.status NOT IN ('cancelled', 'closed')
            # GROUP BY p.uuid
            # HAVING COUNT(b.id) < 3;

            # professionals = db.session.query(Professional).join(
            #         Bookings, isouter=True  # Right join on Booking and Professional
            #     ).filter(
            #         Bookings.status.notin_(['canceled', 'closed']),  # Exclude canceled and closed bookings
            #         Bookings.professional_id == Professional.uuid  # Join condition between Professional and Booking
            #     ).group_by(
            #         Professional.uuid  # Group by Professional ID
            #     ).having(
            #         db.func.count(Bookings.id).filter(Bookings.status == 'accepted' ) < 3  # Professionals with less than 3 active bookings
            #     ).all() 

            professionals=Professional.query.filter( (Professional.active_booking_count<3) & (Professional.status == True )).all()

            return render_template("/customer/customer_dashboard.html", services=services ,all_bookings=all_bookings, upcoming_bookings=upcoming_bookings ,categories=categories ,professionals=professionals)
        else:
            flash("User not found", "error")
            return redirect('/')
    elif "role_id" in session and session["role_id"] != 3:
        flash("You are not a customer", "error")
        return redirect('/')
    flash("You are not signed in", "error")
    return redirect('/')
    
@app.route("/viewservice" ,methods=["GET","POST"])
def view_service():
    services = Services.query.filter(Services.status == True ).order_by(Services.category_id).all()
    # categories = ServiceCategory.query.all()
    search_global = request.args.get('query_global', '').strip()

    if search_global:
        services=Services.query.join(ServiceCategory).filter( 
            (Services.name.ilike(f"%{search_global}%")) |
            (ServiceCategory.name.ilike(f"%{search_global}%")) &
            Services.status == True
        ).order_by(ServiceCategory.id.asc()).all() 
 
    filter_by = request.args.get('filter', '').strip()
    search_query = request.args.get('query', '').strip()
    if search_query or filter_by:
        # Start with the base query
        query = Services.query.filter(Services.status == True )

        # Apply filter based on the user's choice
        if filter_by == "name":
            query = query.filter(Services.name.ilike(f"%{search_query}%")).order_by(Services.name.asc())
        elif filter_by == "category":
            query = query.join(ServiceCategory).filter(ServiceCategory.name.ilike(f"%{search_query}%")).order_by(ServiceCategory.id.asc())
        elif filter_by == "price":
            query = query.order_by(Services.price.asc())
            if search_query.isdigit():
                query = query.filter(Services.price == int(search_query))
            else:
                query = query.filter(Services.name.ilike(f"%{search_query}%")).order_by(Services.price.asc())
        elif filter_by == "location":
            query = query.filter(Services.location.ilike(f"%{search_query}%")).order_by(Services.location.asc())
        elif filter_by == "pincode":
            query = query.order_by(Services.pincode.asc())
            if search_query.isdigit():
                query = query.filter(Services.pincode == int(search_query))
            else:
                query = query.filter(Services.name.ilike(f"%{search_query}%")).order_by(Services.pincode.asc())
        elif filter_by == "rating":
            query = query.order_by((Services.rating_sum / Services.rated_services).desc())
            if search_query.isdigit():
                query = query.filter((Services.rating_sum / Services.rated_services)>=int(search_query)).order_by((Services.rating_sum / Services.rated_services).desc())
            else:
                query = query.filter(Services.name.ilike(f"%{search_query}%")).order_by((Services.rating_sum / Services.rated_services).desc())
        elif filter_by == "duration":
            query = query.order_by(Services.duration.asc())
            if search_query.isdigit():
                query = query.filter(Services.duration == int(search_query))
        else:
            flash("Invalid filter selected.", "danger")
            return redirect("/viewservice")

        # Execute the query
        services = query.all()
    return render_template('view_service.html', services=services)

@app.route('/book_service/<int:service_id>'  , methods=["POST"])
def book_service(service_id):
    if ("role_id" in session and [session['role_id']==3]):
        request_date_str = request.form.get("request_date")
        
        if request_date_str:
            request_date = datetime.strptime(request_date_str, '%Y-%m-%d').date()
            booking = Bookings(service_id=service_id , cust_id = session["uuid"] ,request_date=request_date )
        db.session.add(booking)
        db.session.commit()
        
        flash("Booking Successful" , "success")
        return redirect("/customer/dashboard")
    else:
        flash("You are not authorized to book this service" , "danger")
        return redirect("/")
    
@app.route('/assign_professional/<int:booking_id>/<string:professional_uuid>', methods=['GET'])
def assign_professional(booking_id, professional_uuid):
    # Retrieve the professional by uuid from the database
    booking = Bookings.query.filter_by(id=booking_id).first()
    if ("role_id" not in session and session["role_id"]!=booking.cust_id ):
        flash("You are not authorized to assign a professional" , "danger")
        return redirect("/")
      # Retrieve the booking and professional by their respective IDs
    professional = Professional.query.filter_by(uuid=professional_uuid).first()

    if booking and professional and professional.active_booking_count <3:
        booking.professional_id = professional.uuid
        booking.status="accepted"
        booking.updated_at=datetime.utcnow()
        professional.active_booking_count = professional.active_booking_count + 1
        db.session.commit()

        return redirect("/customer/dashboard")  
    else:
        return "Booking or Professional not found", 404

@app.route('/update_request_date/<int:booking_id>', methods=["POST"])
def update_request_date(booking_id):
    try:
        # Get the new request date from the form
        request_date_str = request.form.get("request_date")
        if request_date_str:
            # Convert to date object for SQLite
            request_date = datetime.strptime(request_date_str, '%Y-%m-%d').date()

            # Fetch booking and update the request date
            booking = Bookings.query.get(booking_id)
            if booking:
                booking.request_date = request_date
                booking.updated_at = datetime.utcnow()
                db.session.commit()
                flash("Request date updated successfully!", "success")
            else:
                flash("Booking not found.", "error")
        else:
            flash("Please select a valid date.", "error")
    except Exception as e:
        flash("An error occurred: " + str(e), "error")

    return redirect("/customer/dashboard")

@app.route("/close_booking/<int:booking_id>" , methods=["post"])
def close_booking(booking_id):
    booking = Bookings.query.get(booking_id)
    if booking:
        if session["uuid"]==booking.cust_id :
            professional = Professional.query.get(booking.professional_id)
            service=Services.query.get(booking.service_id)
            # print()
            rating = int(request.form.get(f"rating{booking.id}") or 0)
            feedback = request.form.get("remarks") or None
            print(rating,feedback)
            booking.status = "closed"
            booking.rating=rating
            booking.feedback=feedback
            booking.completion_date=datetime.utcnow()
            booking.updated_at=datetime.utcnow()
            # print("rating of booking",rating)
        
            professional.rating_sum = professional.rating_sum + rating
            professional.rated_services = professional.rated_services + 1
            professional.active_booking_count = professional.active_booking_count - 1

            service.rating_sum = service.rating_sum + rating
            service.rated_services = service.rated_services + 1
            # print(service.rating_sum)

            db.session.commit()
            flash("Booking Closed Successfully" ,"success")
            return  redirect("/customer/dashboard")
        else:
            flash("User Not Mathced" ,"error")
            return  redirect("/customer/dashboard")
    else:
        flash("Booking Not Found" ,"error")
        return  redirect("/customer/dashboard")

@app.route('/cancel_booking/<int:booking_id>' ,methods=["GET","POST"])  
def cancel_booking(booking_id):
    feedback = request.form.get("feedback")
    booking = Bookings.query.get(booking_id)
    if(booking.status not in ["canceled" , "closed"]):

        if( session['uuid']==booking.cust_id or session["role_id"]==1):
            if(feedback):
                booking.feedback = feedback
            booking.status="canceled"
            booking.updated_at=datetime.utcnow()
            if booking.professional_id:
                professional = Professional.query.get(booking.professional_id)
                professional.active_booking_count = professional.active_booking_count - 1
            db.session.commit()
            flash("Booking has been canceled" , "success")
            
        else:
            flash("You are Not Authorised to perform action" , "error")
    else:
        flash("This booking is already canceled / Closed" , "warning")
    if(session["role_id"]==1):
                return redirect("/admin/manage-bookings")
    return redirect("/customer/dashboard")

@app.route("/user_profile", methods=["GET","POST"])
def user_profile():
    user = User.query.get(session['uuid'])
    if user.role_id == 2:
        professional=Professional.query.get(user.uuid)
        return render_template("/profile.html" , user=user , professional=professional)    


    return render_template("/profile.html" , user=user )    

@app.route("/admin/dashboard"  , methods=["GET"])
def admin_dashboard():
    
    if 'role_id' in session and session['role_id'] == 1:
        total_customers = User.query.filter_by(role_id=3).count()
        total_professionals = User.query.filter_by(role_id=2).count()
        total_bookings = Bookings.query.count()
        total_services=Services.query.filter(Services.status==True).count()
        total_revenue = db.session.query(db.func.sum(Services.price)).join(Bookings, Services.id == Bookings.service_id).filter(Bookings.status == "closed").scalar() or 0
         # Generate the chart and save it
        plot = get_bookings_summary()
        plot.savefig("./static/images/bookings_summary.jpeg")
        plot.clf()  # Clear the figure after saving
        return render_template("/admin/dashboard_overview.html" , total_customers=total_customers, total_professionals=total_professionals ,total_bookings=total_bookings , total_services=total_services,total_revenue=total_revenue ) 
    
    flash("only admins are allowed" , "error")
    return redirect("/")

# view reports for admin
@app.route("/admin/reports" , methods=["GET"])
def admin_reports():
    if 'role_id' in session and session['role_id'] == 1:
        customers = User.query.filter(User.role_id == 3).all()
        professionals=Professional.query.all() 
        return render_template("/admin/reports.html", customers=customers , professionals=professionals )
    flash("only admins are allowed" , "error")
    return redirect("/")

@app.route("/admin/manage-users"  , methods=["GET" ,"POST"])
def manage_users():
    if ("role_id" not in session or session["role_id"] != 1 ):
        flash('You do not have permission to perform this action', 'danger')
        return redirect("/")
    
    customers = User.query.filter(User.role_id == 3).all()
    professionals=Professional.query.all() 

    sort_by = request.args.get('sort_by', 'name')  # Default sort by name
    order = request.args.get('order', 'asc')  # Default order is ascending

    if sort_by == 'name':
        if order == 'asc':
            customers = User.query.filter(User.role_id == 3).order_by(User.firstname.asc()).all()
            professionals = Professional.query.join(User).order_by(User.firstname.asc()).all()
        else:
            customers = User.query.filter(User.role_id == 3).order_by(User.firstname.desc()).all()
            professionals = Professional.query.join(User).order_by(User.firstname.desc()).all() 
    elif sort_by == 'rating':
        if order == 'asc':
            professionals = Professional.query.order_by((Professional.rating_sum / Professional.rated_services).asc()).all()
        else:
            professionals = Professional.query.order_by((Professional.rating_sum / Professional.rated_services).desc()).all()
    elif sort_by == 'exp':
        if order == 'asc':
            professionals = Professional.query.order_by((Professional.experience).asc()).all()
        else:
            professionals = Professional.query.order_by((Professional.experience).desc()).all()
    elif sort_by == "doj":
        if order == "asc":
            customers = User.query.filter(User.role_id == 3).order_by(User.created_at.asc()).all()
            professionals = Professional.query.join(User).order_by(User.created_at.asc()).all()
        else:
            customers = User.query.filter(User.role_id == 3).order_by(User.created_at.desc()).all()
            professionals = Professional.query.join(User).order_by(User.created_at.desc()).all()
    else:
        customers = User.query.filter(User.role_id == 3).all()
        professionals=Professional.query.all()    

    search_query = request.args.get('search')
    if search_query:
        customers = User.query.filter(User.role_id == 3, 
                                      (User.firstname.ilike(f"%{search_query}%") | 
                                       User.lastname.ilike(f"%{search_query}%") |
                                       User.email.ilike(f"%{search_query}%"))).all()
        professionals = Professional.query.filter(Professional.user.has( 
            User.firstname.ilike(f"%{search_query}%") |
            User.lastname.ilike(f"%{search_query}%") |
            User.email.ilike(f"%{search_query}%"))).all()
    categories = ServiceCategory.query.all()
    return render_template("/admin/manage_users.html",  customers=customers, professionals=professionals , categories=categories) 

@app.route('/edit-user/<string:user_id>', methods=['POST'])
def edit_user(user_id):
    user = User.query.get(user_id)

    if user and session.get("signedin"):
        if session['uuid'] == user.uuid or session["role_id"] == 1:
            user.firstname = request.form['firstname']
            user.lastname = request.form['lastname']
            user.email = request.form['email']
            user.phone_number = request.form['phone_number']
            user.address = request.form['address']
            user.pincode = request.form['pincode']

            db.session.commit()

            if user.role_id == 2:
                professional = Professional.query.get(user_id)
                if professional:
                    professional.experience = int(request.form['experience'])
                    professional.skill = request.form["skill"]
                    professional.salary = request.form["salary"]
                    db.session.commit()

            flash('Profile Updated Successfully!', 'success')
            return redirect(url_for('manage_users') if session["role_id"] == 1 else "/user_profile")
        else:
            flash('You are not authorized to edit this user', 'danger')
    else:
        flash('You are not signed in', 'danger')

    return redirect(url_for('manage_users') if session.get("role_id") == 1 else "/user_profile")

@app.route('/admin/toggle-status/<string:id>', methods=["GET" , 'POST'])
def toggle_status(id):
    if 'role_id' in session and session['role_id'] == 1:
        service = Services.query.filter_by(id=id).first()
        if service:
            
            service.status = not service.status
            service.updated_at=datetime.utcnow()
            db.session.commit()
            flash('Status toggled successfully', 'success')
            return redirect("/admin/manage-services")
        user = User.query.filter_by(uuid=id).first()
        if user: 
            user.status = not user.status
            user.updated_at=datetime.utcnow()
            db.session.commit()

            if user.role_id == 2: # if this user is professional
                professional = Professional.query.filter_by(uuid=id).first()
                if professional: 
                    professional.status = not professional.status
                    professional.updated_at=datetime.utcnow()
                    db.session.commit()
            flash('User status updated successfully!', 'success')
        else:
            flash('not found.', 'danger')
    else:
        flash('You do not have permission to perform this action', 'danger')
        return redirect(url_for('manage_users'))
        
    return redirect(url_for('manage_users'))

@app.route('/admin/delete-user/<string:user_id>', methods=["GET",'POST']) 
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        if session.get("signedin"):
            if session["role_id"] == 1:  # Only admins can delete users
                if user.role_id == 2:  # delete Professional = delete user
                    professional = Professional.query.get(user_id)
                    if professional:
                        db.session.delete(professional)
                        db.session.commit() 
                else:
                    db.session.delete(user)
                    db.session.commit()
                
                flash('User deleted successfully!', 'success')
            else:
                flash('You are not authorized to delete this user.', 'danger')
        else:
            flash('you are not signed in.', 'danger')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('manage_users'))

@app.route('/admin/manage-bookings', methods=['GET', 'POST'])
def manage_booking():
    if ("role_id" not in session or session["role_id"] != 1 ):
        flash('You do not have permission to perform this action', 'danger')
        return redirect("/")
    if request.method == 'POST':         
        booking_id = request.form.get('id')
        booking = Bookings.query.filter_by(id=booking_id).first()
        if booking:
            if request.form.get('status') in ["canceled" , "closed"]:
                professional=Professional.query.get(booking.professional_id)
                if professional:
                    professional.active_booking_count = professional.active_booking_count - 1
                    db.session.commit()
                

            booking.status = request.form.get('status', booking.status)
            request_date_str = request.form.get('request_date', booking.request_date)
            booking.request_date=datetime.strptime(request_date_str, '%Y-%m-%d').date() 
            db.session.commit()
            flash("Booking updated successfully", "success")
        else:
            flash("Booking not found", "danger")
        return redirect(url_for('manage_booking'))

    # Handle displaying and filtering bookings
    search_query = request.args.get('search', '').strip()
    if search_query:
        bookings = Bookings.query.join(User).join(Services).filter(
            (User.firstname.ilike(f"%{search_query}%")) |
            (User.lastname.ilike(f"%{search_query}%")) |
            (User.address.ilike(f"%{search_query}%")) |
            (Services.name.ilike(f"%{search_query}%")) |
            (Bookings.status.ilike(f"%{search_query}%"))
        ).all()
    else:
        bookings = Bookings.query.all()
    return render_template('admin/manage_bookings.html', bookings=bookings, search_query=search_query)

@app.route('/admin/manage-category', methods=['GET', 'POST'])
def manage_category():
    if ("role_id" not in session or session["role_id"] != 1 ):
        flash('You do not have permission to perform this action', 'danger')
        return redirect("/")

    if request.method == 'POST':
        # Handle updating a service
        name = request.form.get('name')
        category = ServiceCategory(name=name)
        db.session.add(category)
        db.session.commit()
        flash("Category created successfully", "success")
        return redirect(url_for('manage_category'))
    
    categories = ServiceCategory.query.all()
    

    return render_template('admin/manage_categories.html' , categories=categories)

@app.route('/admin/delete-category/<string:id>', methods=["GET",'POST']) 
def delete_category(id):
    category = ServiceCategory.query.get(id)
    if category:
        if session.get("signedin"):
            if session["role_id"] == 1:   
                # # Check if any services in the category have bookings
                # has_bookings = db.session.query(
                #     exists().where(
                #         Bookings.service_id == Services.id,
                #     ).where(
                #         Services.category_id == id,
                #     )).scalar()
                for service in category.services:
                    if service.bookings:
                        flash("Cannot delete category; it has associated services with active bookings.", "error")
                        return redirect(url_for("manage_category"))
                
                db.session.delete(category)
                db.session.commit()
                
                flash('category and its services deleted successfully!', 'success')
            else:
                flash('You are not authorized to delete this category.', 'danger')
        else:
            flash('you are not signed in.', 'danger')
    else:
        flash('category not found.', 'danger')
    return redirect(url_for('manage_category'))

@app.route('/admin/manage-services', methods=['GET', 'POST'])
def manage_services():
    if ("role_id" not in session or session["role_id"] != 1 ):
        flash('You do not have permission to perform this action', 'danger')
        return redirect("/")

    if request.method == 'POST':
        # Handle updating a service
        service_id = request.form.get('id')
        if service_id:
            # Update existing service
            service = Services.query.filter_by(id=service_id).first()
            if service:
                service.name = request.form.get('name', service.name)
                service.category_id = request.form.get('category_id', service.category_id)
                service.price = request.form.get('price', service.price)
                service.location = request.form.get('location', service.location)
                service.pincode = request.form.get('pincode', service.pincode)
                db.session.commit()
                flash("Service updated successfully", "success")
            else:
                flash("Service not found", "danger")
       
        return redirect(url_for('manage_services'))

    # Fetch and display all services
    services = Services.query.order_by(Services.category_id).all()
    categories = ServiceCategory.query.all()

    filter_by = request.args.get('filter', '').strip()
    search_query = request.args.get('query', '').strip()
    if search_query or filter_by:
        # Start with the base query
        query = Services.query

        # Apply filter based on the user's choice
        if filter_by == "name":
            query = query.filter(Services.name.ilike(f"%{search_query}%"))
        elif filter_by == "location":
            query = query.filter(Services.location.ilike(f"%{search_query}%")).order_by(Services.location.asc())
        elif filter_by == "pincode":
            query = query.order_by(Services.pincode.asc())
            if search_query.isdigit():
                query = query.filter(Services.pincode == int(search_query))
        elif filter_by == "category":
            query = query.join(ServiceCategory).filter(ServiceCategory.name.ilike(f"%{search_query}%"))
        elif filter_by == "price":
            if search_query.isdigit():
                query = query.filter(Services.price == int(search_query))
            else:
                query = query.filter(Services.name.ilike(f"%{search_query}%")).order_by(Services.price.asc())
        elif filter_by == "id":
            if search_query.isdigit():
                query = query.filter(Services.id == int(search_query))
        elif filter_by == "duration":
            if search_query.isdigit():
                query = query.filter(Services.duration == int(search_query))
        elif filter_by == "status":
            query = query.filter(Services.status.ilike(f"%{search_query}%"))
        else:
            flash("Invalid filter selected.", "danger")
            return redirect(url_for('manage_services'))

        # Execute the query
        services = query.all()
        


    return render_template('admin/manage_services.html', services=services, categories=categories)

@app.route('/admin/delete-service/<string:id>', methods=["GET",'POST']) 
def delete_service(id):
    service = Services.query.get(id)
    if service:
        if session.get("signedin"):
            if session["role_id"] == 1:

                # Check for dependent bookings
                bookings = Bookings.query.filter_by(service_id=id).all()
                if bookings:
                    flash("Cannot delete service; it has associated bookings.", "danger")
                    return redirect(url_for('manage_services'))
                db.session.delete(service)
                db.session.commit()
                
                flash('Service deleted successfully!', 'success')
            else:
                flash('You are not authorized to delete this service.', 'danger')
        else:
            flash('you are not signed in.', 'danger')
    else:
        flash('Service not found.', 'danger')
    return redirect(url_for('manage_services'))

@app.route("/admin/add-service"  , methods=["GET" , "POST"])
def add_service():
    if ("role_id" not in session or session["role_id"] != 1 ):
        flash('You do not have permission to perform this action', 'danger')
        return redirect("/")
    if(request.method =="POST"):
        service_name=request.form.get("name")
        category_id=request.form.get("category_id")
        price=request.form.get("price")
        description=request.form.get("description")
        duration=request.form.get("duration")
        pincode=request.form.get("pincode")
        location=request.form.get("location")
        new_service=Services(name=service_name , category_id = category_id , price=price , description =description ,
                         duration=duration, pincode=pincode, location=location)
        db.session.add(new_service)
        db.session.commit()
        flash("Service Added Successfully" , "success")
        return(redirect("/admin/manage-services"))
    return render_template("/admin/manage_services.html")

@app.route("/admin-summary")
def admin_summary():
    if ("role_id" not in session or session["role_id"] != 1 ):
        flash('You do not have permission to perform this action', 'danger')
        return redirect("/")
    # Generate the chart and save it
    plot = get_bookings_summary()
    plot.savefig("./static/images/bookings_summary.jpeg")
    plot.clf()  # Clear the figure after saving
    return render_template("/admin/admin_summary.html")

def get_bookings_summary():
    
    ## Fetch bookings data
    bookings = (
        db.session.query(Services.name, db.func.count(Bookings.id))
        .join(Bookings, Bookings.service_id == Services.id)
        .filter(Bookings.status == "closed")
        .group_by(Services.id)
        .order_by(Services.id)
        .all()
    )

    # Separate service names and booking counts into two lists
    services = [booking[0] for booking in bookings]  # Service names
    booking_counts = [booking[1] for booking in bookings]  # Booking counts
    # Create a bar chart
    plt.bar(services, booking_counts, color="skyblue", width=0.4)
    plt.title("Bookings per Service")
    plt.xlabel("Service")
    plt.ylabel("Number of Bookings")
    plt.xticks(rotation=45, ha='right')  # Rotate labels 45 degrees and align to the right
    plt.tight_layout()  # Adjust layout to prevent clipping
    return plt

def generate_avg_rating_by_skill_chart(prof_id):
    # Fetch the professional's skill
    professional = Professional.query.filter_by(uuid=prof_id).first()
    if not professional:
        return None

    skill = professional.skill

    # Fetch services under the matching category
    services = (
        Services.query.join(ServiceCategory, Services.category_id == ServiceCategory.id)
        .filter(ServiceCategory.name == skill)
        .all()
    )
    
    # Calculate average ratings for each service
    avg_ratings = {}
    for service in services:
        # Fetch bookings for this service
        bookings = Bookings.query.filter_by(service_id=service.id, status="closed").all()
        if bookings:
            ratings = [booking.rating for booking in bookings if booking.rating > 0]
            if ratings:
                avg_ratings[service.name] = sum(ratings) / len(ratings)

    # Plot the bar chart
    labels = list(avg_ratings.keys())
    values = list(avg_ratings.values())

    plt.figure(figsize=(5, 4))
    bar_width = 0.5  # Set narrower bar width
    bars = plt.bar(labels, values, width=bar_width, color='skyblue')

    # Add average rating annotations on top of bars
    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # X-position
            bar.get_height() + 0.05,           # Y-position
            f"{value:.1f}",                    # Text (formatted to 1 decimal)
            ha="center", fontsize=10
        )

    plt.xlabel("Service Name")
    plt.ylabel("Average Rating")
    plt.title(f"Average Ratings for Services in {skill} Category")
    # plt.xticks(rotation=0, ha="right")
    plt.tight_layout()

    return plt


def generate_service_count_chart(prof_id):
    bookings = (
        Bookings.query.filter_by(professional_id=prof_id, status="closed")
        .join(Services, Bookings.service_id == Services.id)
        .add_columns(Services.name)
        .all()
    )

    service_counts = {}
    for booking in bookings:
        service_name = booking.name
        service_counts[service_name] = service_counts.get(service_name, 0) + 1

    x_names = list(service_counts.keys())
    y_counts = list(service_counts.values())

    plt.bar(x_names, y_counts, color="blue", width=0.4)
    plt.title("Service Count")
    plt.xlabel("Service")
    plt.ylabel("Count")
    plt.xticks(rotation=15, ha="right")
    return plt

def generate_avg_rating_chart(prof_id):
    bookings = (
        Bookings.query.filter_by(professional_id=prof_id, status="closed")
        .join(Services, Bookings.service_id == Services.id)
        .add_columns(Services.name, Bookings.rating)
        .all()
    )

    ratings = {}
    for booking in bookings:
        service_name = booking.name
        if service_name not in ratings:
            ratings[service_name] = []
        ratings[service_name].append(booking.rating)

    avg_ratings = {name: sum(ratings[name]) / len(ratings[name]) for name in ratings if ratings[name]}

    labels = list(avg_ratings.keys())
    sizes = list(avg_ratings.values())

    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
    plt.title("Average Ratings")
    return plt

def generate_customer_booking_chart(customer_id):
    bookings = (
        Bookings.query.filter_by(cust_id=customer_id)
        .add_columns(Bookings.status)
        .all() 
    )
    summary = {"active": 0, "closed": 0, "canceled": 0}

    for booking in bookings:
        if booking.status in summary:
            summary[booking.status] += 1

    x_status = list(summary.keys())
    y_counts = list(summary.values())

    plt.bar(x_status, y_counts, color=["skyblue", "lightgreen", "salmon"], width=0.4)
    plt.title("Customer Bookings Summary")
    plt.xlabel("Status")
    plt.ylabel("Count")

    # chart_path = f"static/images/customer_{customer_id}_booking_summary.jpeg"
    # plt.savefig(chart_path)
    # plt.close()
    return plt


@app.route('/admin/api/schema', methods=['GET'])
def get_database_schema():
    if ("role_id" not in session or session["role_id"] != 1 ):
        flash('You do not have permission to perform this action', 'danger')
        return redirect("/")
    schema = {}
    inspector = inspect(db.engine)  # Use inspect to get metadata
    for table_name in inspector.get_table_names():
        table_info = []
        columns = inspector.get_columns(table_name)
        for column in columns:
            table_info.append({
                'name': column['name'],
                'type': str(column['type']),
                'nullable': column['nullable'],
                'primary_key': column['primary_key'],
                'default': str(column['default']) if column['default'] else None
            })
        schema[table_name] = table_info
    return jsonify(schema)


if __name__ == "__main__":
    app.run(debug=True)
