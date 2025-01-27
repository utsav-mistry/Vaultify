from sqlite3 import IntegrityError
from flask import render_template, redirect, url_for, flash, request, session
from app import app, db, bcrypt
from app.models import User, Password
from app.utils import generate_otp, send_otp_email
from app.forms import RegistrationForm, LoginForm, PasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from app.utils import generate_aes_key, sha256_hash, aes_encrypt, aes_decrypt
from datetime import datetime, timedelta
from flask_mail import Message
from sqlalchemy import text

# OTP expiration time (e.g., 5 minutes)
OTP_EXPIRATION_TIME = timedelta(minutes=5)


@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Check if the username or email already exists
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            if existing_user.username == form.username.data:
                form.username.errors.append("Username already taken. Please choose a different one.")
            if existing_user.email == form.email.data:
                form.email.errors.append("Email already registered. Please use a different email.")
        else:
            # Generate OTP
            otp = generate_otp()

            # Store OTP, email, and expiration time in session
            session['otp'] = otp
            session['email'] = form.email.data
            session['otp_expiration'] = (datetime.now() + OTP_EXPIRATION_TIME).timestamp()  # Expiry time as timestamp
            session['username'] = form.username.data
            session['password'] = form.password.data 

            send_otp_email(form.email.data, otp)

            flash('A verification OTP has been sent to your email. Please check your inbox.', 'success')
            return redirect(url_for('verify_otp'))  # Redirect to OTP verification page
    
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    return render_template('login.html', form=form)


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    passwords = Password.query.filter_by(user_id=current_user.id).all()

    # Create a list to store the Password model instances directly
    password_list = []
    for pw in passwords:
        decrypted_password = aes_decrypt(current_user.aes_key, pw.encrypted_password).decode()
        pw.decrypted_password = decrypted_password  # Add decrypted password as a property
        password_list.append(pw)

    # Handle search
    search_query = request.args.get('search')
    results = password_list  # Default: all passwords
    if search_query:
        # Filter results based on the search query
        search_query = search_query.lower()
        results = [pw for pw in password_list if search_query in pw.website.lower()]

    return render_template('dashboard.html', passwords=results)



@app.route('/delete_profile', methods=['GET', 'POST'])
@login_required
def delete_profile():
    if request.method == 'POST':
        # Delete all passwords associated with the user
        passwords = Password.query.filter_by(user_id=current_user.id).all()
        for password in passwords:
            db.session.delete(password)  # Delete each password
        
        # Now delete the user profile
        user = User.query.get(current_user.id)
        db.session.delete(user)  # Delete the user profile

        # Commit the changes to the database
        db.session.commit()

        flash('Your account and all associated passwords have been deleted.', 'success')
        # Log out the user (optional)
        logout_user()

        return redirect(url_for('index'))  # Redirect to homepage or login page

    # Render the confirmation page
    return render_template('delete_profile.html')


# Add Password Route
@app.route("/add_password", methods=['GET', 'POST'])
@login_required
def add_password():
    form = PasswordForm()
    if form.validate_on_submit():
        hashed_website = sha256_hash(form.website.data)  # You can remove this if you want to store the website in plaintext
        encrypted_password = aes_encrypt(current_user.aes_key, form.password.data)
        password_entry = Password(website=form.website.data,  # Store the website in plaintext
                                  username=form.username.data,
                                  encrypted_password=encrypted_password,
                                  user_id=current_user.id)
        db.session.add(password_entry)
        db.session.commit()
        flash('Password saved!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_password.html', form=form)


@app.route("/edit_password/<int:password_id>", methods=['GET', 'POST'])
@login_required
def edit_password(password_id):
    password_entry = Password.query.get_or_404(password_id)
    form = PasswordForm()

    if form.validate_on_submit():
        # Update the existing password entry
        password_entry.website = form.website.data  # Update website (now in plaintext)
        password_entry.username = form.username.data
        password_entry.encrypted_password = aes_encrypt(current_user.aes_key, form.password.data)  # Encrypt the new password
        db.session.commit()
        flash('Password updated!', 'success')
        return redirect(url_for('dashboard'))

    # Pre-fill the form with existing data for editing
    form.website.data = password_entry.website  # Show website as plaintext
    form.username.data = password_entry.username
    form.password.data = aes_decrypt(current_user.aes_key, password_entry.encrypted_password).decode()

    return render_template('add_password.html', form=form)


# Delete Password Route
@app.route("/delete_password/<int:password_id>", methods=['POST'])
@login_required
def delete_password(password_id):
    password_entry = Password.query.get_or_404(password_id)
    if password_entry.user_id != current_user.id:
        flash('You cannot delete someone else\'s password.', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(password_entry)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/profile')
@login_required
def profile():
    # Direct SQL query to fetch logs for the current user
    query = text("SELECT * FROM logs WHERE user_id = :user_id ORDER BY timestamp DESC")
    logs = db.session.execute(query, {'user_id': current_user.id}).fetchall()
    
    # Pass logs to the profile.html template
    return render_template('profile.html', logs=logs)

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form.get('otp')

        # Retrieve OTP and expiration from session
        session_otp = session.get('otp')
        otp_expiration = session.get('otp_expiration')
        email = session.get('email')

        if not email or not session_otp:
            flash('Invalid request. Please register first.', 'danger')
            return redirect(url_for('register'))
        
        # Convert otp_expiration to a datetime object if it's a float
        if isinstance(otp_expiration, float):
            otp_expiration = datetime.fromtimestamp(otp_expiration)

        # Check if OTP is expired
        if datetime.now() > otp_expiration:
            flash('OTP has expired. Please request a new one.', 'danger')
            return redirect(url_for('register'))

        # Check if OTP is correct
        if otp != session_otp:
            flash('Invalid OTP. Please try again.', 'danger')
            return render_template('verify_otp.html')

        # OTP is correct and not expired, now add the user to the database
        hashed_password = bcrypt.generate_password_hash(session['password']).decode('utf-8')  # Assuming password was stored in session
        aes_key = generate_aes_key()

        user = User(
            username=session['username'],
            email=email,
            password=hashed_password,
            aes_key=aes_key
        )
        db.session.add(user)
        db.session.commit()

        # Clear session data after successful registration
        session.pop('otp', None)
        session.pop('email', None)
        session.pop('otp_expiration', None)
        session.pop('username', None)
        session.pop('password', None)

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('verify_otp.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate OTP for password reset
            otp = generate_otp()
            # Store OTP and email in session
            session['reset_otp'] = otp
            session['reset_email'] = email
            session['reset_otp_expiration'] = (datetime.now() + OTP_EXPIRATION_TIME).timestamp()

            # Send the OTP to the user's email
            send_otp_email(email, otp)

            flash('A password reset OTP has been sent to your email. Please check your inbox.', 'success')
            return redirect(url_for('reset_password'))  # Redirect to OTP verification page
        else:
            flash('No account found with that email address.', 'danger')

    return render_template('forgot_password.html')

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        # Get the new password from the form
        new_password = request.form['password']
        
        # Ensure the new password is not empty
        if not new_password:
            flash('Password cannot be empty.', 'danger')
            return render_template('reset_password.html')  # Stay on the reset page with the error
            
        # Get OTP and email from session
        reset_otp = session.get('reset_otp')
        reset_email = session.get('reset_email')
        reset_otp_expiration = session.get('reset_otp_expiration')
        
        if not reset_otp or not reset_email:
            flash('Invalid request. Please request a password reset first.', 'danger')
            return redirect(url_for('forgot_password'))

        # Check if OTP has expired
        if datetime.now() > datetime.fromtimestamp(reset_otp_expiration):
            flash('OTP has expired. Please request a new one.', 'danger')
            return redirect(url_for('forgot_password'))

        # Check if the OTP provided by the user matches the one stored in session
        otp = request.form['otp']
        if otp != reset_otp:
            flash('Invalid OTP. Please try again.', 'danger')
            return render_template('reset_password.html')  # Stay on the reset page with the error

        # Now hash the new password and update it in the database
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        # Retrieve the user from the database
        user = User.query.filter_by(email=reset_email).first()
        
        if user:
            user.password = hashed_password  # Update the user's password
            db.session.commit()  # Save the changes
            flash('Your password has been reset successfully.', 'success')
            
            # Clear session data after successful password reset
            session.pop('reset_otp', None)
            session.pop('reset_email', None)
            session.pop('reset_otp_expiration', None)
            
            return redirect(url_for('login'))  # Redirect to the login page

        else:
            flash('No account found with that email address.', 'danger')
            return redirect(url_for('forgot_password'))  # Redirect to forgot password page

    return render_template('reset_password.html')




@app.route("/learn_more", methods=['GET'])
def learn_more():
    return render_template("learn_more.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))
