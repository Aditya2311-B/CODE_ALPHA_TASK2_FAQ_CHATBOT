import re

class RegistrationForm:
    def __init__(self, username, email, password, confirm_password):
        self.username = (username or '').strip()
        self.email = (email or '').strip()
        self.password = password or ''
        self.confirm_password = confirm_password or ''
        self.errors = {}

    def validate(self):
        # Username checks
        if not self.username:
            self.errors['username'] = "Username is required."
        elif len(self.username) < 3:
            self.errors['username'] = "Username must be at least 3 characters long."
        elif not re.match(r'^\w+$', self.username):
            self.errors['username'] = "Username can only contain alphanumeric characters and underscores."

        # Email checks
        if not self.email:
            self.errors['email'] = "Email is required."
        elif not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', self.email):
            self.errors['email'] = "Please enter a valid email address."

        # Password checks
        if not self.password:
            self.errors['password'] = "Password is required."
        elif len(self.password) < 6:
            self.errors['password'] = "Password must be at least 6 characters long."

        if self.password != self.confirm_password:
            self.errors['confirm_password'] = "Passwords do not match."

        return len(self.errors) == 0


class LoginForm:
    def __init__(self, username_or_email, password):
        self.username_or_email = (username_or_email or '').strip()
        self.password = password or ''
        self.errors = {}

    def validate(self):
        if not self.username_or_email:
            self.errors['username_or_email'] = "Username or Email is required."
        if not self.password:
            self.errors['password'] = "Password is required."
        return len(self.errors) == 0


class ProfileForm:
    def __init__(self, username, email, current_password=None, new_password=None, confirm_new_password=None):
        self.username = (username or '').strip()
        self.email = (email or '').strip()
        self.current_password = current_password or ''
        self.new_password = new_password or ''
        self.confirm_new_password = confirm_new_password or ''
        self.errors = {}

    def validate(self, user):
        if not self.username:
            self.errors['username'] = "Username is required."
        elif len(self.username) < 3:
            self.errors['username'] = "Username must be at least 3 characters long."

        if not self.email:
            self.errors['email'] = "Email is required."
        elif not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', self.email):
            self.errors['email'] = "Please enter a valid email address."

        if self.new_password:
            if not self.current_password:
                self.errors['current_password'] = "Current password is required to change password."
            elif not user.check_password(self.current_password):
                self.errors['current_password'] = "Incorrect current password."
            
            if len(self.new_password) < 6:
                self.errors['new_password'] = "New password must be at least 6 characters long."
            
            if self.new_password != self.confirm_new_password:
                self.errors['confirm_new_password'] = "Passwords do not match."

        return len(self.errors) == 0
