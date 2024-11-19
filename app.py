from flask import Flask, render_template, request, redirect ,flash, url_for
from flask import session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import uuid
import bcrypt

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sampledb5.sqlite3"
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
    created_at   = db.Column(db.Date, default = datetime.utcnow)
    updated_at   = db.Column(db.Date, default = datetime.utcnow )
    status       = db.Column(db.Boolean , nullable=False , default = True  ) # active/inactive

    profile_image= db.Column(db.String() )

    customer_bookings = db.relationship('Bookings', foreign_keys='Bookings.cust_id', back_populates='customer', lazy=True) 
    # professional = db.relationship('Professional', uselist=False, back_populates='user')
    
    def __init__(self, uuid , email, password, firstname, lastname, address, pincode, role_id, phone_number,profile_image):
        self.uuid = uuid
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.firstname = firstname
        self.lastname =lastname
        self.pincode=pincode
        self.address=address 
        self.phone_number=phone_number
        self.role_id = role_id
        if(profile_image):
            self.profile_image=profile_image 

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
    status         = db.Column(db.Boolean , nullable=False , default = True  ) # active/inactive
    cv_file_path   = db.Column(db.String(255) )
    created_at     = db.Column(db.Date,default = datetime.utcnow )
    updated_at     = db.Column(db.Date,default = datetime.utcnow )
    user = db.relationship("User" , backref="professional" , cascade="all, delete" , lazy=True)

    # professional_bookings = db.relationship('Bookings', foreign_keys='Bookings.professional_id', backref='professional', lazy=True) 

class Bookings(db.Model):
    __tablename__   = "Bookings"
    id              = db.Column(db.Integer, primary_key=True , autoincrement=True)
    cust_id         = db.Column(db.String(), db.ForeignKey("User.uuid") )
    professional_id = db.Column(db.String() , db.ForeignKey("Professional.uuid") ) 
    service_id      = db.Column(db.Integer, db.ForeignKey("Services.id") )
    status          = db.Column(db.String(), nullable=False ,default = "active")
    booking_date    = db.Column(db.Date, nullable=False ,  default = datetime.utcnow)
    request_date     = db.Column(db.Date)
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
    created_at      = db.Column(db.Date,default = datetime.utcnow)
    updated_at      = db.Column(db.Date,default = datetime.utcnow )
    # category        = db.relationship("ServiceCategory" , backref="services" , lazy=True)

class  ServiceCategory(db.Model):
    __tablename__   = "ServiceCategory"
    id              = db.Column(db.Integer, primary_key=True,  autoincrement=True)
    name            = db.Column(db.String(), nullable=False)  # category name
    # service_id      = db.Column(db.Integer ,  db.ForeignKey("Services.id"), nullable=False)
    services        = db.relationship("Services" ,  backref="category"  ,lazy=True, cascade="all,delete" ) 
    created_at      = db.Column(db.Date ,default = datetime.utcnow )
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



    new_service_1 = Services(name="room cleaning" , category_id = 1 , price=1000 , description ="cleaning of rooms" ,
                         duration=1)
    new_service_2 = Services(name="home cleaning" , category_id = 1 , price=3000 , description ="cleaning of home" ,
                         duration=4)
    new_service_3 = Services(name="ofiice cleaning" , category_id = 1 , price=2000 , description ="cleaning of office" ,
                         duration=1)
    new_service_4 = Services(name="toilet cleaning" , category_id = 1 , price=500 , description ="cleaning of toilet" ,
                         duration=1)
    new_service_5 = Services(name="Ac Repair & Service" , category_id = 2 , price=1000 , description ="Ac Repair & Service" ,
                         duration=1)
    new_service_6 = Services(name="Gyser Repair & Service" , category_id = 2 , price=1000 , description ="Gyser Repair & Service" ,
                         duration=1)
    new_service_7 = Services(name="Pipe fitings" , category_id = 3 , price=1000 , description ="Pipe fitings" ,
                         duration=1)
    new_service_8 = Services(name="plumbing related" , category_id = 3 , price=1000 , description ="plumbing related" ,
                         duration=1)
    new_service_9 = Services(name="wall repair" , category_id = 4 , price=1000 , description ="repairing of walls" ,
                         duration=1)
    db.session.add_all([new_service_1,new_service_2,new_service_3,new_service_4,new_service_5,new_service_6,new_service_7,new_service_8,new_service_9])
    db.session.commit()

    new_services = [
        # Cleaning Services
        Services(name="deep cleaning", category_id=1, price=5000, description="thorough cleaning of the entire home", duration=3),
        Services(name="window cleaning", category_id=1, price=800, description="cleaning windows inside and out", duration=2),
        Services(name="carpet cleaning", category_id=1, price=1500, description="professional carpet cleaning", duration=2),
        
        # Electrical Services
        Services(name="wiring installation", category_id=2, price=3000, description="new wiring for your home", duration=4),
        Services(name="lighting installation", category_id=2, price=1200, description="installation of indoor and outdoor lighting", duration=2),
        Services(name="outlet repair", category_id=2, price=500, description="repair faulty electrical outlets", duration=1),
        
        # Plumbing Services
        Services(name="faucet installation", category_id=3, price=700, description="installing new faucets", duration=1),
        Services(name="drain cleaning", category_id=3, price=1000, description="cleaning clogged drains", duration=1),
        Services(name="water heater installation", category_id=3, price=2500, description="installing a new water heater", duration=3),
        
        # Maintenance Services
        Services(name="home maintenance checkup", category_id=4, price=1500, description="annual maintenance check for your home", duration=2),
        Services(name="furniture assembly", category_id=4, price=800, description="assembling furniture from flat-pack", duration=1),
        
        # Health & Wellness Services
        Services(name="personal training", category_id=5, price=1500, description="one-on-one personal training sessions", duration=1),
        Services(name="yoga classes", category_id=5, price=1200, description="group yoga sessions", duration=1.5),
        
        # Beauty & Personal Care Services
        Services(name="haircut & styling", category_id=6, price=500, description="professional haircut and styling", duration=1),
        Services(name="makeup services", category_id=6, price=1200, description="professional makeup for events", duration=2),
        
        # Automotive Services
        Services(name="car wash", category_id=7, price=400, description="full exterior and interior car wash", duration=1),
        Services(name="oil change", category_id=7, price=1000, description="oil change and filter replacement", duration=1),
        
        # Technology Support Services
        Services(name="computer setup", category_id=8, price=1500, description="setting up new computers and peripherals", duration=2),
        Services(name="virus removal", category_id=8, price=800, description="removing viruses and malware from computers", duration=1),

        # More services can be added similarly...
         Services(name="interior painting", category_id=9, price=3500, description="painting the interior of the home", duration=4),
        Services(name="flooring installation", category_id=9, price=4000, description="installing hardwood, laminate, or tile flooring", duration=5),

        # Education & Tutoring Services
        Services(name="online tutoring", category_id=10, price=800, description="one-on-one online tutoring sessions", duration=1),
        Services(name="homework help", category_id=10, price=600, description="assistance with homework and assignments", duration=1),

        # Professional Services
        Services(name="legal consultation", category_id=11, price=3000, description="consultation with a legal expert", duration=1),
        Services(name="financial planning", category_id=11, price=2000, description="personal financial planning services", duration=2),

        # Pest Control Services
        Services(name="general pest control", category_id=12, price=1500, description="treatment for common pests", duration=2),
        Services(name="termite inspection", category_id=12, price=2000, description="inspection for termite infestations", duration=1.5),

        # Pet Care Services
        Services(name="dog walking", category_id=13, price=500, description="daily dog walking services", duration=1),
        Services(name="pet grooming", category_id=13, price=1200, description="grooming services for pets", duration=1.5),

        # Event Services
        Services(name="event planning", category_id=14, price=5000, description="complete event planning services", duration=8),
        Services(name="catering services", category_id=14, price=3000, description="catering for events and parties", duration=3),

        # Fitness & Sports Services
        Services(name="personal training sessions", category_id=15, price=1500, description="personal training for fitness goals", duration=1),
        Services(name="group fitness classes", category_id=15, price=800, description="join group fitness sessions", duration=1),

        # Moving & Relocation Services
        Services(name="local moving", category_id=16, price=3000, description="moving services within the local area", duration=4),
        Services(name="packing services", category_id=16, price=1200, description="packing services for relocations", duration=2),

        # Appliance Repair Services
        Services(name="washing machine repair", category_id=17, price=1500, description="repair services for washing machines", duration=2),
        Services(name="refrigerator repair", category_id=17, price=2000, description="repair services for refrigerators", duration=3),

        # Security Services
        Services(name="home security installation", category_id=18, price=2500, description="installation of home security systems", duration=3),
        Services(name="security patrol services", category_id=18, price=3000, description="security patrol for properties", duration=4),

        # Childcare Services
        Services(name="nanny services", category_id=19, price=2000, description="full-time or part-time nanny services", duration=8),
        Services(name="babysitting services", category_id=19, price=800, description="occasional babysitting services", duration=2),

        # Gardening & Landscaping Services
        Services(name="lawn care", category_id=20, price=1000, description="care and maintenance of lawns", duration=2),
        Services(name="landscaping design", category_id=20, price=3000, description="designing and installing landscapes", duration=4),

        # Legal & Documentation Services
        Services(name="will writing", category_id=21, price=1500, description="writing legal wills", duration=2),
        Services(name="contract drafting", category_id=21, price=2500, description="drafting contracts and agreements", duration=3),

        # Photography & Videography Services
        Services(name="event photography", category_id=22, price=4000, description="photography for events", duration=4),
        Services(name="video editing services", category_id=22, price=2500, description="editing video content for clients", duration=3),

        # Transportation & Delivery Services
        Services(name="parcel delivery", category_id=23, price=800, description="delivery of parcels and packages", duration=1),
        Services(name="airport transfer services", category_id=23, price=2500, description="transfers to and from the airport", duration=2),

        # Waste Management Services
        Services(name="garbage collection", category_id=24, price=1000, description="regular garbage collection services", duration=2),
        Services(name="recycling services", category_id=24, price=800, description="recycling of various materials", duration=1),

        # Handyman Services
        Services(name="furniture repair", category_id=25, price=1200, description="repairing and restoring furniture", duration=2),
        Services(name="small home repairs", category_id=25, price=800, description="handling minor repairs around the house", duration=1)

    ]

    db.session.add_all(new_services)
    db.session.commit()



    id=uuid.uuid4()
    customer1 = User(uuid = str(id) ,email="c1@gmail.com" , password = "1234" , firstname="c1", lastname="c1",
                                address="address" , pincode="111111", phone_number=9138394488
                    ,role_id = 3  ,profile_image= None)
    
    id1=uuid.uuid4()
    professional1 = User(uuid = str(id1) ,email="p1@gmail.com" , password = "1234" , firstname="p1", lastname="p1",
                            address="address" , pincode="111111", phone_number=8708063057
                            ,role_id = 2 ,profile_image= None )
                    
    professional_details= Professional(uuid=str(id1), skill="cleaning" , experience=1  )
    
    id2=uuid.uuid4()
    admin= User(uuid = str(id2) ,email="admin@gmail.com" , password = "1111" , firstname="admin", lastname="admin",
                                address="address" , pincode="111111", phone_number=1234567890
                    ,role_id = 1 ,profile_image= None )
    db.session.add_all([customer1 , admin , professional1,professional_details ] )
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
        profile_image =request.form.get("profile_image")
        
        new_registration = User(uuid = str(id) ,email=email , password = password , firstname=firstname, lastname=lastname,
                                address=address , pincode=pincode, phone_number=phone_number
                                ,role_id = 3 , profile_image=profile_image  )

        db.session.add(new_registration)
        db.session.commit()

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
            return redirect("/professional/register")
        
        user = User.query.filter_by(email=email).first()
        if user:
            if (email == user.email):
                flash( "Email Id Already in Use, please sign in" , "error" )
                return redirect(url_for('login'))
        
        # db wala code
        id = uuid.uuid4()

        firstname = request.form.get("firstname")
        lastname     =request.form.get("lastname")
        role_id      = 2
        address      =request.form.get("address")
        pincode      =request.form.get("pincode")
        phone_number =request.form.get("phonenumber")
        profile_image =request.form.get("profile_image")
        experience = request.form.get("experience")
        skill=request.form.get("skill")

        new_user_registration = User(uuid=str(id), email=email , password = password , firstname=firstname, lastname=lastname,
                                address=address , pincode=pincode, phone_number=phone_number,
                                role_id = 2 , profile_image=profile_image  )
        

        new_professional_registration= Professional(uuid=str(id), skill=skill , experience=experience,)
        
        db.session.add(new_professional_registration)
        db.session.add(new_user_registration)
        db.session.commit()

        flash( "REGISTERED SUCCESSFULLY !" , "success" )
        return redirect(url_for("login")) # REDIRECT TO  LOGIN PAGE !
    
    return render_template("/professional/professional_registeration_form.html")  # make a seperate register page for Professional



# common for both cust and prof
@app.route("/login" , methods =["GET" , "POST"])
def login():
    
    if "firstname" in session:
        flash("Please Sign Out First","info")
        return redirect(url_for("customer_dashboard"))
     
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
                flash("Your account is Terminated" , "danger")
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
        
    # return redirect("/")
    return render_template("login.html")

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


@app.route("/professional/dashboard")
def professional_dashboard():
    if(session):
        if(session["role_id"]==2):
            professional=Professional.query.get(session["uuid"])
            active_services = Bookings.query.join(Services).join(ServiceCategory).filter(
                ServiceCategory.name == professional.skill ,Bookings.status=="active").all()
            service_history=Bookings.query.join(Services).join(ServiceCategory).filter(
                Bookings.professional_id ==professional.uuid, Bookings.status=="closed" ).all()
            assigned_services=Bookings.query.filter(
                Bookings.professional_id ==professional.uuid, Bookings.status=="accepted"  ).all()

            # services=Bookings.query.filter_by(Bookings.service.category_id=user.skill)
            # add category_id in professional table
            # make dropdown options for skills in register form of  professional
            # admin can add new categories , add column status , in category 
            # show only  active categories in dropdown options
            # 1 professional can accept upto 3 request at any point
         
            if professional:
                # bookings= [booking for booking in Bookings ]
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

@app.route('/accept_booking/<int:booking_id>/<string:professional_id>', methods=['POST'])
def accept_booking(booking_id , professional_id):

    booking = Bookings.query.get_or_404(booking_id)

    if booking.status == "accepted":
        flash(f"This booking has already been accepted by {booking.professional.name} ", "info")
        return redirect(url_for('professional_dashboard'))

    booking.status = "accepted"
    booking.professional_id=professional_id
    db.session.commit()

    flash("Booking accepted successfully!", "success")
    return redirect("/professional/dashboard")

@app.route("/customer/dashboard", methods=["GET"])
def customer_dashboard():
    if "firstname" in session:
        # Retrieve the current user from the database using their UUID stored in the session
        user = User.query.filter_by(email=session["email"]).first()

        if user:
            categories=ServiceCategory.query.all() 
            services = Services.query.limit(8).all()
            all_bookings = [booking for booking in user.customer_bookings ]
            upcoming_bookings = [booking for booking in user.customer_bookings if (not booking.completion_date and booking.status != "canceled")]

            return render_template("/customer/customer_dashboard.html", services=services ,all_bookings=all_bookings, upcoming_bookings=upcoming_bookings ,categories=categories)
        else:
            flash("User not found", "error")
            return redirect('/')
    else:
        flash("You are not signed in", "error")
        return redirect('/')
    

@app.route("/viewservice" ,methods=["GET","POST"])
def view_service():
    # view all services
    # Fetch the specific service details from the database
    services = Services.query.all()
    return render_template('view_service.html', services=services)


@app.route('/book_service/<int:service_id>'  , methods=["POST"])
def book_service(service_id):
    if[session['role_id']==3]:
        request_date_str = request.form.get("request_date")
        
        if request_date_str:
            request_date = datetime.strptime(request_date_str, '%Y-%m-%d').date()
            booking = Bookings(service_id=service_id , cust_id = session["uuid"] ,request_date=request_date )
        db.session.add(booking)
        db.session.commit()
        
        flash("Booking Successful" , "success")
        return redirect("/customer/dashboard")
    else:
        return 404


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
            booking.status = "closed"
            booking.rating=rating
            booking.feedback=feedback
            booking.completion_date=datetime.utcnow()
            booking.updated_at=datetime.utcnow()
            # print("rating of booking",rating)
        
            professional.rating_sum = professional.rating_sum + rating
            professional.rated_services = professional.rated_services + 1

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


@app.route('/cancel_booking/<int:booking_id>' ,methods=["POST"])  
def cancel_booking(booking_id):
    feedback = request.form.get("feedback")
    booking = Bookings.query.get(booking_id)
    if(booking.status != "canceled"):

        if( session['uuid']==booking.cust_id):
            if(feedback):
                booking.feedback = feedback
            booking.status="canceled"
            booking.updated_at=datetime.utcnow()
            db.session.commit()
            flash("Booking has been canceled" , "success")
        else:
            flash("User id not matched" , "error")
    else:
        flash("This booking is already canceled" , "warning")
    return redirect("/customer/dashboard")


@app.route("/user_profile", methods=["GET","POST"])
def user_profile():
    user = User.query.get(session['uuid'])
    # if request.method == "POST":


    return render_template("/profile.html" , user=user)    

@app.route("/user/dashboard/bookings" , methods=["GET"])
def bookings():
    return "heres is your history of booking and active services"

@app.route("/admin/dashboard"  , methods=["GET"])
def admin_dashboard():
    
    if 'role_id' in session and session['role_id'] == 1:
        return render_template("/admin/dashboard_overview.html") 
    
    flash("only admins are allowed" , "error")
    return redirect("/")

@app.route("/admin/manage-users"  , methods=["GET" ,"POST"])
def manage_users():
    
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

    return render_template("/admin/manage_users.html",  customers=customers, professionals=professionals) 


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
                    db.session.commit()

            flash('Profile Updated Successfully!', 'success')
            return redirect(url_for('manage_users') if session["role_id"] == 1 else "/user_profile")
        else:
            flash('You are not authorized to edit this user', 'danger')
    else:
        flash('You are not signed in', 'danger')

    return redirect(url_for('manage_users') if session.get("role_id") == 1 else "/user_profile")

    


@app.route('/admin/toggle-status/<string:user_id>', methods=["GET" , 'POST'])
def toggle_status(user_id):
    if 'role_id' in session and session['role_id'] == 1:
        user = User.query.filter_by(uuid=user_id).first()

        if user:  # Check if the user exists in the database
            user.status = not user.status
            user.updated_at=datetime.utcnow()
            db.session.commit()
            print(user)

            if user.role_id == 2:  # Check if it's a professional
                professional = Professional.query.filter_by(uuid=user_id).first()
                if professional:  # Check if the professional exists
                    professional.status = not professional.status
                    professional.updated_at=datetime.utcnow()
                    db.session.commit()
            flash('User status updated successfully!', 'success')
        else:
            flash('User not found.', 'danger')
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
                if user.role_id == 2:  # Professional
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

@app.route("/admin/manage-bookings" , methods=["GET","POST"])
def manage_bookings():
    if session.get("signedin"):
        if session["role_id"] == 1:  # Only admins can manage bookings
            bookings = Bookings.query.all()
            return render_template("admin/manage_bookings.html", bookings=bookings)
        else:
            flash('You do not have permission to perform this action', 'danger')
            return redirect("/")
    else:
        flash('You are not signed in.', 'danger')
        return redirect("/")

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
