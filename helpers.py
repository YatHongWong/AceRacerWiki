
from flask import session, flash, render_template
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            
            # Alert user that logging in is required
            flash("Logging in is required for this function")

            # Direct user to login page
            return render_template("login.html")
        return f(*args, **kwargs)
    return decorated_function

def trusted_required(f):
    """
    Decorate routes to require trusted status.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin") < 1:
            return ("must be at least trusted")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorate routes to require admin privilege.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin") != 1:
            return ("lacking admin privilages")
        return f(*args, **kwargs)
    return decorated_function