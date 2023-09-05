from flask import Flask,render_template,request,redirect,session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os
import ast


localServer = True
with open("templates/config.json",'r') as o:
    params = json.load(o)['params']

app = Flask(__name__)
app.secret_key = "sskey"
# app.config.update(
#     MAIL_SERVER = "smtp.gmail.com",
#     MAIL_PORT = "465",
#     MAIL_USE_SSL = True,
#     MAIL_USERNAME = params["mailUser"],
#     MAIL_PASSWORD = params["mailPassword"]
# )



if(localServer):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DURL")
    app.config["SQLALCHEMY_BINDS"] = {
    }
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['userdb']


db = SQLAlchemy(app)
# from project import app, db
# >>> app.app_context().push()
# >>> db.create_all()


class RegUsers(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    fpass = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    userprogress = db.Column(db.String(100),nullable = True)
    submission = db.Column(db.String(50000),nullable = True)
    # Add a one-to-many relationship to the InternDetails model
    internships = db.relationship('InternDetails', backref='user', lazy=True)

    idata = db.relationship('Idata', backref='user', lazy=True)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.name}"


class InternDetails(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    college = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    dob = db.Column(db.DateTime, nullable=False)
    mno = db.Column(db.String(50), nullable=False)
    internship = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer,nullable = False)
    
    # Add a foreign key to the RegUsers model
    user_id = db.Column(db.Integer, db.ForeignKey('reg_users.sno'), nullable=False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.name}"


class Idata(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    domain = db.Column(db.String(50), nullable=False)
    week = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(40000), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('reg_users.sno'), nullable=True)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.domain}"



    
@app.route("/createData", methods=['GET', 'POST'])
def createData():
    l = "/createData"

    # Check if the admin is logged in using session data
    admin_logged_in = session.get("admin_logged_in", False)

    if admin_logged_in:
        if request.method == "POST":
            domain = request.form['domain']
            week = request.form['week']
            day = request.form['day']
            content = request.form['content']

            idata = Idata(domain=domain, week=week, day=day, content=content)
            db.session.add(idata)
            db.session.commit()
            return redirect("/createData")

        return render_template("createData.html", l=l)
    else:
        # Redirect to admin login page if admin is not logged in
        return redirect("/adminlogin")

@app.route("/updateData/<string:model>/<int:sno>",methods=['GET','POST'])
def updateData(model,sno):
    
    admin_logged_in = session.get("admin_logged_in", False)

    if admin_logged_in:
        m = Idata.query.filter_by(domain=model, day=sno).first()
        if request.method == "POST":
            
            m.domain = request.form['domain']
            m.week = request.form['week']
            m.day = request.form['day']
            m.content = request.form['content']
            db.session.add(m)
            db.session.commit()
            return render_template("update.html",m =m)

        return render_template("update.html", m = m)
    
        
    else:
        # Redirect to admin login page if admin is not logged in
        return redirect("/adminlogin")


@app.route("/delateData/<string:model>/<int:sno>",methods=['GET','POST'])
def delateData(model,sno):
    
    admin_logged_in = session.get("admin_logged_in", False)

    if admin_logged_in:
        m = Idata.query.filter_by(domain=model, day=sno).first()
        db.session.delete(m)
        db.session.commit()
        return redirect("/admindashboard")
    
    return redirect("/adminlogin")





@app.route("/internship/<string:model>/<int:sno>",methods= ['GET','POST'])
def internship(model, sno):
    if 'user_id' in session:
        m = Idata.query.filter_by(domain=model, day=sno).first()
        user = RegUsers.query.get(session['user_id'])
        if request.method == "POST":
            code = request.form["code"]
            s = user.submission
            s = ast.literal_eval(s)
            s[model].append(code)
            user.submission = str(s)
            db.session.add(user)
            db.session.commit()
            if m is None or not m.content:
                return redirect("/dashboard")
            return redirect(f'/internship/{m.domain}/{m.day}')
        
        up = user.userprogress
        up  = ast.literal_eval(up)
        up[model] = sno
        user.userprogress = str(up)
        db.session.add(user)
        db.session.commit()
        if m is None or not m.content:
            return redirect("/dashboard")  # Redirect to dashboard.html
        return render_template("interns.html", m=m)
    else:
        # User is not logged in, redirect to the login page
        return redirect("/login")





@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = RegUsers.query.filter_by(email=email).first()

        if user:
            # Email found in the database, check password
            if user.password == password:
                # Authentication successful, set session to indicate the user is logged in
                session["user_id"] = user.sno
                # Redirect to a dashboard or profile page after successful login
                return render_template('index.html')  # Replace "dashboard" with the actual route for the dashboard
            else:
                # Wrong password
                pas = 1
                error_message = "Wrong email or password."
                return render_template("/login.html",pas = pas,error_message=error_message)
        else:
            # Email not found in the database, redirect to register page
            pas = 2
            error_message = "Email is not registered."
            return  render_template("/login.html",pas = pas, error_message = error_message)

    # For GET request, render the login page
    return render_template("login.html")

        
@app.route("/forgot",methods=['GET','POST'])
def forgot():
    if request.method == "POST":
        email = request.form["email"]

        # Check if the provided email exists in the database
        user = RegUsers.query.filter_by(email=email).first()

        if user:
            # Generate and store the OTP in the session for verification
            otp = generate_verification_token()
            session["otp"] = otp
            session["email"] = email

            # Send the OTP to the user's email
            a = "forgot"
            send_email("forgot",email, otp, a)

            # Redirect the user to the OTP verification page
            return redirect("/verify_otp")

        else:
            # If the email is not found in the database, show an error message.
            pas = 2
            return render_template("forgot.html",pas = pas)

    # For GET request, render the forgot password page
    return render_template("forgot.html")

@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        submitted_otp = request.form["otp"]
        email = session.get("email")  # Retrieve the email from the session
        otp = session.get("otp")  # Retrieve the OTP from the session

        if email and otp and submitted_otp == otp:
            # If OTP matches, redirect the user to reset password page
            return redirect("/reset_password")

        else:
            # If OTP does not match, show an error message.
            error_message = "Invalid OTP"
            return render_template("otp_verification.html", error_message=error_message)

    # For GET request, render the OTP verification page
    return render_template("otp_verification.html")


@app.route("/emailVerification",methods=["GET","POST"])
def verification():
    submitted_otp = request.form["otp"]
    email = session.get("email")  # Retrieve the email from the session
    otp = session.get("otp")  # Retrieve the OTP from the session

    if email and otp and submitted_otp == otp:
        # If OTP matches, add the user to the database
        user = RegUsers(name=session.get("name"), email=session.get("email"), password=session.get("password"), fpass=session.get("fpass"),userprogress = session.get("userprogress"),submission = session.get("submission"))
        db.session.add(user)
        db.session.commit()
        return render_template("login.html")
    else:
        pas = 5
        return render_template("otp.html",pas = pas)

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]
        email = session.get("email")

        # Check if the provided email exists in the session
        if email:
            if new_password == confirm_password:
                # Find the user by email and update the password
                user = RegUsers.query.filter_by(email=email).first()
                user.password = new_password
                db.session.commit()

                # Clear the session data after password reset
                session.pop("otp", None)
                session.pop("email", None)

                # Redirect the user to the login page with a success message
                
                return render_template("login.html")
            else:
                error_message = "Passwords do not match."
                return render_template("reset_password.html", error_message=error_message)

        else:
            # If the email is not found in the session, show an error message.
            error_message = "Email not found for password reset."
            return render_template("reset_password.html", error_message=error_message)

    # For GET request, render the reset password page
    return render_template("reset_password.html")

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        fpass = request.form["fpass"]
        userprogress = str({
            "Python":0,
            "C":0,
            "C++":0,
            "webd":0,
            "ai":0,
            "blockchain":0,
            "Java":0
        })
        submission = str({
            "Python":[],
            "C":[],
            "C++":[],
            "webd":[],
            "ai":[],
            "blockchain":[],
            "Java":[]
        })

        existing_user = RegUsers.query.filter_by(email=email).first()

        if existing_user:
            pas = 3
            return render_template("register.html",pas = pas)
        
        if(password==fpass):
            otp = generate_verification_token()
            # Store the OTP in the session for verification
            session["otp"] = otp
            session["name"] = name
            session["email"] = email
            session["password"] = password
            session["fpass"] = fpass
            session['userprogress'] = userprogress
            session['submission'] = submission
            send_email("otp",email, otp,name)
            return render_template("otp.html")

            #  user = RegUsers(name =name,email = email,password=password,fpass=fpass )
            #  db.session.add(user)
            #  db.session.commit()
            #  return redirect(f"otp.html",email = email,otp = otp)
             
            #  return "<body><script>alert('You Joined')</script></body>"
             
        else:
             pas = 4
             return render_template("register.html",pas = pas)
             
        

       
    user = RegUsers.query.all()
   
    return render_template("signin.html",user = user)

def send_email(r,receiver_email, otp,name):
    # Set up the MIMEText object to represent the email body
    sender_email =params['email'] 
    sender_password = params['pass']
    if r == "forgot":
        subject =  "Reset Your Password - Your OTP Inside"
        body = f'''Hello

To reset your password, 
here's your One-Time Password (OTP): {otp}

Enter this OTP on the reset page to regain access to your account. This code will expire in 2 minutes.

Stay secure,
CodeStream Team'''
    elif r == "apply":
        subject = "Congratulations on successfully enrolling for Codestream’s Internship Program"
        body = f'''Dear {name},

I hope this email finds you well. We are thrilled to welcome you aboard as our newest intern here at CODESTREAM. Your arrival marks the beginning of an exciting journey of learning.


During your internship, you'll have the opportunity to learn and grow, contribute your unique skills and perspectives, and gain valuable experience in your applied domain. We believe that your fresh enthusiasm will make a significant impact on your skillset. we recommend you to  share your offer letter(Will be sent to you in 24 Hours) on linked in to add up to its value.


As you settle in, please don't hesitate to contact our support team at codestream74@gmail.com or +91 78419 82719. Our team is here to support your every step of the way. All the best for your tasks and learnings. We can't wait to get you started with the learning odyssey! 


Best regards, 
CODESTREAM INDIA.
'''
    elif r == "otp":
        subject = "Thank You for Registering on CODESTREAM"
        body = f'''Dear {name},

We're thrilled to welcome you on CODESTREAM !. We encourage you to have a look at our exciting internship programs specially designed for the rookies to kickstart building up their skill set. Looking forward for you to apply

Your OTP for Registration : {otp}

Happy coding!
Warm regards,
Codestream'''
    
    
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server with TLS
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        # Enable debugging to see communication with the server (optional)
        server.set_debuglevel(1)

        # Log in to the SMTP server with your email credentials
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        # Enable debugging to see communication with the server (optional)
        server.set_debuglevel(1)

        # Log in to the SMTP server with your email credentials
        server.login("codestream74@gmail.com", "fyhmgapeexvlqkuf")

        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())
    finally:
        # Close the connection to the SMTP server
        server.quit()


def generate_verification_token():
    return str(random.randint(100000, 999999))

 

@app.route("/")
def home():
    return  render_template("index.html")


@app.route("/about")
def about():
    return  render_template("about.html")

@app.route("/service")
def serivce():
    return  render_template("service.html")


@app.route("/register")
def register():
    return  render_template("register.html")

@app.route("/details/<string:domain>")
def details(domain):
    if domain == "Python":
        return render_template("detailsPython.html")
    elif domain == "C":
        return render_template("detailsC.html")
    elif domain == "Cpp":
        return render_template("detailsCpp.html")
    elif domain == "Java":
        return render_template("detailsJava.html")
    elif domain == "AI":
        return render_template("detailsAI.html")
    elif domain == "Blockchain":
        return render_template("detailsBlockchain.html")
    elif domain == "WebD":
        return render_template("detailsWebD.html")


def send_email_to_admin(name,upiid,email,college,address,mobile,birthdate,internship,amount,user_id):
    # Set up the MIMEText object to represent the email body
    sender_email =params['email'] 
    sender_password = params['pass']
    subject = "New User Applied for Internship"
    body = f"Name : {name}\n UPI ID : {upiid}\nEmail : {email}\nCollege : {college}\nAddress : {address}\nMobile : {mobile}\nBirthdate : {birthdate}\nInternship : {internship}\nAmount : {amount}\nUserID : {user_id}"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = "codestream74@gmail.com"
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server with TLS
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        # Enable debugging to see communication with the server (optional)
        server.set_debuglevel(1)

        # Log in to the SMTP server with your email credentials
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, "codestream74@gmail.com", message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        # Enable debugging to see communication with the server (optional)
        server.set_debuglevel(1)

        # Log in to the SMTP server with your email credentials
        server.login("codestream74@gmail.com", "fyhmgapeexvlqkuf")

        # Send the email
        server.sendmail("codestream74@gmail.com", "codestream63@gmail.com", message.as_string())
    finally:
        # Close the connection to the SMTP server
        server.quit()


@app.route("/applyform/<string:domain>", methods=["GET", "POST"])
def applyform(domain):
    if 'user_id' not in session:
        # User is not logged in, redirect to the login page
        return redirect("/login")

    user = RegUsers.query.get(session['user_id'])
    if user:
        session['name'] = user.name
        session['email'] = user.email  # Add this line to set the email in the session

    if request.method == "POST":
        # Get the values submitted by the user in the form
        name = request.form["name"]
        email = request.form["email"]
        college = request.form["college"]
        address = request.form["address"]
        mobile = request.form["mobile"]
        birthdate = request.form["birthdate"]
        internship = request.form["internship"]
        amount = 180
        
        # Convert the date string to a Python datetime object
        dob = datetime.strptime(birthdate, "%Y-%m-%d")
        # send_email("apply",email,"user_id",name)
        # send_email_to_admin(name,upiid,email,college,address,mobile,birthdate,internship,amount,user_id)
        # intern_details = InternDetails(name = name,email = email,college = college,address = address,mno = mobile,dob = dob,amount=amount,internship= internship,upiid = upiid,user_id=user.sno)
        # db.session.add(intern_details)
        # db.session.commit()
        
        #Store the form data in the session for later use
        session['application_data'] = {
            'name': name,
            'email': email,
            'college': college,
            'address': address,
            'mobile': mobile,
            'dob': dob,
            'internship': internship,
            'amount': amount  # Store the amount for later reference
        }

        # Create the Razorpay payment order and redirect to checkout page
        # client = razorpay.Client(auth=("rzp_test_Zjom8IGzUOcgy1", "QTCPiD4BPPLsHcVtSN3DsUe4"))
        # data = {"amount": amount * 100, "currency": "INR", "receipt": f"{user.sno}"}
        # payment = client.order.create(data=data)

        # Redirect the user to the Razorpay checkout page
        return redirect("https://cosmofeed.com/vp/64ecbc82656bd0001dbbb054")

    return render_template("applyform.html",domain = domain)






@app.route("/paymentsuccess", methods=["GET"])
def update_database():
    
    application_data = session.get('application_data') 
    # Create a new InternDetails instance and add it to the database
    intern_details = InternDetails(amount=application_data['amount'], name=application_data['name'], email=application_data['email'],college=application_data['college'], address=application_data['address'], mno=application_data['mobile'],
        dob=application_data['dob'], internship=application_data['internship'], user_id=session['user_id'])
    email=application_data['email']
    name=application_data['name']
    
    db.session.add(intern_details)
    db.session.commit()
    send_email("apply",email,"user_id",name)
       
        # Clear the stored application data from the session
    session.pop('application_data', None)

        # Return a response indicating success (you can customize the response as needed)
    return render_template("issue.html")
       
    



@app.route("/adminlogin", methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        admin_username = request.form["admin_username"]
        admin_password = request.form["admin_password"]

        # Check if the provided admin credentials match the stored admin details
        if admin_username == params["admin"] and admin_password == params["adminPassword"]:
            # Admin authentication successful, set session to indicate the admin is logged in
            session["admin_logged_in"] = True
            return redirect("/admindashboard")
        else:
            # Wrong admin credentials
            return "Admin login failed."

    # For GET request, render the admin login page
    return render_template("adminlogin.html")

@app.route("/admindashboard")
def admindashboard():
    # Check if the admin is logged in
    admin_logged_in = session.get("admin_logged_in", False)

    if admin_logged_in:
        # If admin is logged in, retrieve all user details from the database
        users = RegUsers.query.all()
        return render_template("admindashboard.html", users=users)
    else:
        # If admin is not logged in, redirect to the admin login page
        return redirect("/adminlogin")
    
@app.route("/adminlogout")
def admin_logout():
    # Clear the admin_logged_in session variable to indicate that the admin is logged out
    session.pop("admin_logged_in", None)
    return redirect("/")
  

@app.route("/logout")
def logout():
    # Clear the user_id from the session to indicate the user is logged out
    session.pop('user_id', None)
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    
    if 'user_id' in session:
        # User is logged in, retrieve the name and email from the session
        user = RegUsers.query.get(session['user_id'])
        if user:
            session['name'] = user.name
            session['email'] = user.email  # Add this line to set the email in the session
        else:
            # User ID in the session is invalid, clear the session
            session['name'] = None
            session['email'] = None
    else:
        # User is not logged in, redirect to the login page
        return redirect("/login")

    if 'user_id' in session:
        # User is logged in, retrieve the internships they have enrolled in
        user = RegUsers.query.get(session['user_id'])
     
        if user:
            enrolled_internships = user.internships
            up = user.userprogress
            up  = ast.literal_eval(up) # Retrieve the list of enrolled internships
        else:
            enrolled_internships = []
    else:
        enrolled_internships = []

    return render_template("dashboard.html", enrolled_internships=enrolled_internships,up = up)

@app.route("/AdminApplyform", methods=["GET", "POST"])
def adminApplyform():

    admin_logged_in = session.get("admin_logged_in", False)

    if admin_logged_in:
        if request.method == "POST":
        # Get the values submitted by the user in the form
            name = request.form["name"]
            email = request.form["email"]
            college = request.form["college"]
            address = request.form["address"]
            mobile = request.form["mobile"]
            birthdate = request.form["birthdate"]
            internship = request.form["internship"]
            amount = 180
            upiid = request.form["upiid"]
            user_id = request.form["userID"]
            # Convert the date string to a Python datetime object
            dob = datetime.strptime(birthdate, "%Y-%m-%d")
            a = "apply"
            # send_email(email,"user_id",a)
            # send_email_to_admin(name,upiid,email,college,address,mobile,birthdate,internship,amount)
            intern_details = InternDetails(name = name,email = email,college = college,address = address,mno = mobile,dob = dob,amount=amount,internship= internship,upiid = upiid,user_id = user_id)
            db.session.add(intern_details)
            db.session.commit()
            return redirect("/AdminApplyform")
        return render_template("adminApplyfrom.html")

        
    else:
        # Redirect to admin login page if admin is not logged in
        return redirect("/adminlogin")
        
        # Store the form data in the session for later use
        # session['application_data'] = {
        #     'name': name,
        #     'email': email,
        #     'college': college,
        #     'address': address,
        #     'mobile': mobile,
        #     'dob': dob,
        #     'internship': internship,
        #     'amount': amount  # Store the amount for later reference
        # }

        # Create the Razorpay payment order and redirect to checkout page
        # client = razorpay.Client(auth=("rzp_test_Zjom8IGzUOcgy1", "QTCPiD4BPPLsHcVtSN3DsUe4"))
        # data = {"amount": amount * 100, "currency": "INR", "receipt": f"{user.sno}"}
        # payment = client.order.create(data=data)

        # Redirect the user to the Razorpay checkout page
        
@app.route("/veiwIntership",methods = ['GET','POST'])
def veiwInternship():
    admin_logged_in = session.get("admin_logged_in", False)

    if admin_logged_in:
        if request.method == "POST":
            m = request.form["domain"]
            data = Idata.query.filter_by(domain = m)
            return render_template("veiwInternData.html", data = data)
    else:
        # If admin is not logged in, redirect to the admin login page
        return redirect("/adminlogin")
