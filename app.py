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
    cust_id         = db.Column(db.String(), db.ForeignKey("User.uuid") ,  nullable=False)
    professional_id = db.Column(db.String() , db.ForeignKey("Professional.uuid") ) 
    service_id      = db.Column(db.Integer, db.ForeignKey("Services.id") ,  nullable=False)
    status          = db.Column(db.String(), nullable=False ,default = "active")
    booking_date    = db.Column(db.Date, nullable=False ,  default = datetime.utcnow)
    completion_date = db.Column(db.Date)
    feedback        = db.Column(db.String())
    rating          = db.Column(db.Float, default=0)

    service = db.relationship("Services", backref="bookings", lazy=True)
    user = db.relationship("User", backref="bookings", lazy=True)

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

    # new_category1=ServiceCategory(name="cleaning")
    # new_category2=ServiceCategory(name="electrical")
    # new_category3=ServiceCategory(name="plumbing")
    # new_category4=ServiceCategory(name="maintenance")
    
    # db.session.add(new_category1)
    # db.session.add(new_category2)
    # db.session.add(new_category3)
    # db.session.add(new_category4)
    # db.session.commit()

    # new_categories = [
    #     ServiceCategory(name="health & wellness"), #5
    #     ServiceCategory(name="beauty & personal care"),#6
    #     ServiceCategory(name="automotive services"),#7
    #     ServiceCategory(name="technology support"),#8
    #     ServiceCategory(name="home improvement"),#9
    #     ServiceCategory(name="education & tutoring"),#10
    #     ServiceCategory(name="professional services"),#11
    #     ServiceCategory(name="pest control"),#12
    #     ServiceCategory(name="pet care"),#13
    #     ServiceCategory(name="event services"),#14
    #     ServiceCategory(name="fitness & sports"),#15
    #     ServiceCategory(name="moving & relocation"),#16
    #     ServiceCategory(name="appliance repair"),#17
    #     ServiceCategory(name="security services"),#18
    #     ServiceCategory(name="childcare"),#19
    #     ServiceCategory(name="gardening & landscaping"),#20
    #     ServiceCategory(name="legal & documentation"),#21
    #     ServiceCategory(name="photography & videography"),#22
    #     ServiceCategory(name="transportation & delivery"),#23
    #     ServiceCategory(name="waste management"),#24
    #     ServiceCategory(name="handyman services")#25
    # ]

    # db.session.add_all(new_categories)
    # db.session.commit()



    # new_service_1 = Services(name="room cleaning" , category_id = 1 , price=1000 , description ="cleaning of rooms" ,
    #                      duration=1)
    # new_service_2 = Services(name="home cleaning" , category_id = 1 , price=1000 , description ="cleaning of home" ,
    #                      duration=1)
    # new_service_2 = Services(name="house cleaning" , category_id = 1 , price=1000 , description ="cleaning of house" ,
    #                      duration=1)
    # new_service_3 = Services(name="toilet cleaning" , category_id = 1 , price=1000 , description ="cleaning of toilet" ,
    #                      duration=1)
    # new_service_4 = Services(name="Ac Repair & Service" , category_id = 2 , price=1000 , description ="Ac Repair & Service" ,
    #                      duration=1)
    # new_service_5 = Services(name="Gyser Repair & Service" , category_id = 2 , price=1000 , description ="Gyser Repair & Service" ,
    #                      duration=1)
    # new_service_6 = Services(name="Pipe fitings" , category_id = 3 , price=1000 , description ="Pipe fitings" ,
    #                      duration=1)
    # new_service_7 = Services(name="plumbing related" , category_id = 3 , price=1000 , description ="plumbing related" ,
    #                      duration=1)
    # new_service_8 = Services(name="wall repair" , category_id = 4 , price=1000 , description ="repairing of walls" ,
    #                      duration=1)
    # db.session.add_all([new_service_1,new_service_2,new_service_3,new_service_4,new_service_5,new_service_6,new_service_7,new_service_8])
    # db.session.commit()

    # new_services = [
    #     # Cleaning Services
    #     Services(name="deep cleaning", category_id=1, price=2000, description="thorough cleaning of the entire home", duration=3),
    #     Services(name="window cleaning", category_id=1, price=800, description="cleaning windows inside and out", duration=2),
    #     Services(name="carpet cleaning", category_id=1, price=1500, description="professional carpet cleaning", duration=2),
        
    #     # Electrical Services
    #     Services(name="wiring installation", category_id=2, price=3000, description="new wiring for your home", duration=4),
    #     Services(name="lighting installation", category_id=2, price=1200, description="installation of indoor and outdoor lighting", duration=2),
    #     Services(name="outlet repair", category_id=2, price=500, description="repair faulty electrical outlets", duration=1),
        
    #     # Plumbing Services
    #     Services(name="faucet installation", category_id=3, price=700, description="installing new faucets", duration=1),
    #     Services(name="drain cleaning", category_id=3, price=1000, description="cleaning clogged drains", duration=1),
    #     Services(name="water heater installation", category_id=3, price=2500, description="installing a new water heater", duration=3),
        
    #     # Maintenance Services
    #     Services(name="home maintenance checkup", category_id=4, price=1500, description="annual maintenance check for your home", duration=2),
    #     Services(name="furniture assembly", category_id=4, price=800, description="assembling furniture from flat-pack", duration=1),
        
    #     # Health & Wellness Services
    #     Services(name="personal training", category_id=5, price=1500, description="one-on-one personal training sessions", duration=1),
    #     Services(name="yoga classes", category_id=5, price=1200, description="group yoga sessions", duration=1.5),
        
    #     # Beauty & Personal Care Services
    #     Services(name="haircut & styling", category_id=6, price=500, description="professional haircut and styling", duration=1),
    #     Services(name="makeup services", category_id=6, price=1200, description="professional makeup for events", duration=2),
        
    #     # Automotive Services
    #     Services(name="car wash", category_id=7, price=400, description="full exterior and interior car wash", duration=1),
    #     Services(name="oil change", category_id=7, price=1000, description="oil change and filter replacement", duration=1),
        
    #     # Technology Support Services
    #     Services(name="computer setup", category_id=8, price=1500, description="setting up new computers and peripherals", duration=2),
    #     Services(name="virus removal", category_id=8, price=800, description="removing viruses and malware from computers", duration=1),

    #     # More services can be added similarly...
    #      Services(name="interior painting", category_id=9, price=3500, description="painting the interior of the home", duration=4),
    #     Services(name="flooring installation", category_id=9, price=4000, description="installing hardwood, laminate, or tile flooring", duration=5),

    #     # Education & Tutoring Services
    #     Services(name="online tutoring", category_id=10, price=800, description="one-on-one online tutoring sessions", duration=1),
    #     Services(name="homework help", category_id=10, price=600, description="assistance with homework and assignments", duration=1),

    #     # Professional Services
    #     Services(name="legal consultation", category_id=11, price=3000, description="consultation with a legal expert", duration=1),
    #     Services(name="financial planning", category_id=11, price=2000, description="personal financial planning services", duration=2),

    #     # Pest Control Services
    #     Services(name="general pest control", category_id=12, price=1500, description="treatment for common pests", duration=2),
    #     Services(name="termite inspection", category_id=12, price=2000, description="inspection for termite infestations", duration=1.5),

    #     # Pet Care Services
    #     Services(name="dog walking", category_id=13, price=500, description="daily dog walking services", duration=1),
    #     Services(name="pet grooming", category_id=13, price=1200, description="grooming services for pets", duration=1.5),

    #     # Event Services
    #     Services(name="event planning", category_id=14, price=5000, description="complete event planning services", duration=8),
    #     Services(name="catering services", category_id=14, price=3000, description="catering for events and parties", duration=3),

    #     # Fitness & Sports Services
    #     Services(name="personal training sessions", category_id=15, price=1500, description="personal training for fitness goals", duration=1),
    #     Services(name="group fitness classes", category_id=15, price=800, description="join group fitness sessions", duration=1),

    #     # Moving & Relocation Services
    #     Services(name="local moving", category_id=16, price=3000, description="moving services within the local area", duration=4),
    #     Services(name="packing services", category_id=16, price=1200, description="packing services for relocations", duration=2),

    #     # Appliance Repair Services
    #     Services(name="washing machine repair", category_id=17, price=1500, description="repair services for washing machines", duration=2),
    #     Services(name="refrigerator repair", category_id=17, price=2000, description="repair services for refrigerators", duration=3),

    #     # Security Services
    #     Services(name="home security installation", category_id=18, price=2500, description="installation of home security systems", duration=3),
    #     Services(name="security patrol services", category_id=18, price=3000, description="security patrol for properties", duration=4),

    #     # Childcare Services
    #     Services(name="nanny services", category_id=19, price=2000, description="full-time or part-time nanny services", duration=8),
    #     Services(name="babysitting services", category_id=19, price=800, description="occasional babysitting services", duration=2),

    #     # Gardening & Landscaping Services
    #     Services(name="lawn care", category_id=20, price=1000, description="care and maintenance of lawns", duration=2),
    #     Services(name="landscaping design", category_id=20, price=3000, description="designing and installing landscapes", duration=4),

    #     # Legal & Documentation Services
    #     Services(name="will writing", category_id=21, price=1500, description="writing legal wills", duration=2),
    #     Services(name="contract drafting", category_id=21, price=2500, description="drafting contracts and agreements", duration=3),

    #     # Photography & Videography Services
    #     Services(name="event photography", category_id=22, price=4000, description="photography for events", duration=4),
    #     Services(name="video editing services", category_id=22, price=2500, description="editing video content for clients", duration=3),

    #     # Transportation & Delivery Services
    #     Services(name="parcel delivery", category_id=23, price=800, description="delivery of parcels and packages", duration=1),
    #     Services(name="airport transfer services", category_id=23, price=2500, description="transfers to and from the airport", duration=2),

    #     # Waste Management Services
    #     Services(name="garbage collection", category_id=24, price=1000, description="regular garbage collection services", duration=2),
    #     Services(name="recycling services", category_id=24, price=800, description="recycling of various materials", duration=1),

    #     # Handyman Services
    #     Services(name="furniture repair", category_id=25, price=1200, description="repairing and restoring furniture", duration=2),
    #     Services(name="small home repairs", category_id=25, price=800, description="handling minor repairs around the house", duration=1)

    # ]

    # db.session.add_all(new_services)
    # db.session.commit()



    # id=uuid.uuid4()
    # customer1 = User(uuid = str(id) ,email="p1@gmail.com" , password = "1234" , firstname="p1", lastname="p1",
    #                             address="address" , pincode="111111", phone_number=1234567890
    #                 ,role_id = 3  )
    
    # id1=uuid.uuid4()
    # admin= User(uuid = str(id1) ,email="admin@gmail.com" , password = "1111" , firstname="admin", lastname="admin",
    #                             address="address" , pincode="111111", phone_number=1234567890
    #                 ,role_id = 1 )
    # db.session.add_all([cu stomer1 , admin] )
    # db.session.commit()
    
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
                                role_id = 2 , profile_image=profile_image  )
        

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
    user=User.query.filter_by(uuid=session["uuid"])
    professional = Professional.
    if user:
        bookings= [booking for booking in user.]

        return render_template("/professional/professional_dashboard.html",user=user , bookings=bookings )
    else:
        flash("You are not signed in" , "error")

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
    

@app.route('/view_service/')
def view_service():
    # view all services
    # Fetch the specific service details from the database
    services = Services.query.all()
    return render_template('view_service.html', services=services)

@app.route('/book_service/<int:service_id>')
def book_service(service_id):
    if[session['role_id']==3]:
        booking = Bookings(service_id=service_id , cust_id = session["uuid"] )
        db.session.add(booking)
        db.session.commit()
        flash("Booking Successful" , "success")
        return redirect("/customer/dashboard")
    else:
        return 404


@app.route('/cancel_booking/<int:booking_id>' ,methods=["POST"])  
def cancel_booking(booking_id):
    feedback = request.form.get("feedback")
    booking = Bookings.query.get(booking_id)
    if(booking.status != "canceled"):

        if( session['uuid']==booking.cust_id):
            if(feedback):
                booking.feedback = feedback
            booking.status="canceled"
            db.session.commit()
            flash("Booking has been canceled" , "success")
        else:
            flash("User id not matched" , "error")
    else:
        flash("This booking is already canceled" , "warning")
    return redirect("/customer/dashboard")


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
