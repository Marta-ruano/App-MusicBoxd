from functools import wraps
from flask import session, redirect, abort, request

def check_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user") is None:
            return redirect("/auth/login")
        return f(*args, **kwargs)
    return wrapper

def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = session.get("user")
            if user is None:
                return redirect("/auth/login")
            if user.get("role") not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator