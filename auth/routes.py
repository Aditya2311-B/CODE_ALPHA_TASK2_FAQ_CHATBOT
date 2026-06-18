from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from database import db, User
from auth.forms import RegistrationForm, LoginForm, ProfileForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        form = RegistrationForm(username, email, password, confirm_password)
        if form.validate():
            # Check if user already exists
            existing_user = User.query.filter(
                (User.username == form.username) | (User.email == form.email)
            ).first()
            
            if existing_user:
                if existing_user.username == form.username:
                    form.errors['username'] = "Username is already taken."
                else:
                    form.errors['email'] = "Email is already registered."
            else:
                # Create user
                user = User(username=form.username, email=form.email)
                user.set_password(form.password)
                
                # Make the first user an admin (default), and others regular users or just keep default is_admin=True
                # Let's count existing users. If 0, then definitely admin. Else standard.
                if User.query.count() == 0:
                    user.is_admin = True
                
                db.session.add(user)
                db.session.commit()
                
                flash("Registration successful! Please log in.", "success")
                return redirect(url_for('auth.login'))

        # If errors, flash them
        for field, error in form.errors.items():
            flash(f"{error}", "danger")

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))

    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        form = LoginForm(username_or_email, password)
        if form.validate():
            # Search user by username or email
            user = User.query.filter(
                (User.username == form.username_or_email) | (User.email == form.username_or_email)
            ).first()

            if user and user.check_password(form.password):
                login_user(user, remember=remember)
                flash(f"Welcome back, {user.username}!", "success")
                
                # Handle standard next redirection
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('chat'))
            else:
                flash("Invalid username/email or password.", "danger")
        else:
            for field, error in form.errors.items():
                flash(f"{error}", "danger")

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')

        form = ProfileForm(username, email, current_password, new_password, confirm_new_password)
        if form.validate(current_user):
            # Check unique username/email excluding current user
            conflict_user = User.query.filter(
                (User.id != current_user.id) & 
                ((User.username == form.username) | (User.email == form.email))
            ).first()

            if conflict_user:
                if conflict_user.username == form.username:
                    flash("Username is already taken.", "danger")
                else:
                    flash("Email is already in use by another account.", "danger")
            else:
                current_user.username = form.username
                current_user.email = form.email
                
                if form.new_password:
                    current_user.set_password(form.new_password)
                    
                db.session.commit()
                flash("Profile updated successfully!", "success")
                return redirect(url_for('auth.profile'))
        else:
            for field, error in form.errors.items():
                flash(f"{error}", "danger")

    return render_template('profile.html')
