from flask import render_template,redirect,session

from app.models import *
from . import main
import functools

import hashlib
#密码加密
def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result


from flask import request
@main.route("/register/",methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        user = User()
        user.user_name = username
        user.email = email
        user.password = setPassword(password)
        user.save()
    return render_template("register.html")


def loginValid(fun):
    @functools.wraps(fun)
    def inner(*args,**kwargs):
        username = request.cookies.get('username')
        id = request.cookies.get("id","0")
        user = User.query.get(int(id))
        session_username = session.get("username")
        if user:
            if user.user_name == username and username == session_username:
                return fun(*args,**kwargs)
            else:
                return redirect("/login/")
        else:
            return redirect("/login/")
    return inner

@main.route("/login/",methods=["GET","POST"])
def login():
    error = ""
    if request.method == "POST":
        form_data = request.form
        email = form_data.get("email")
        password = form_data.get("password")
        user = User.query.filter_by(email = email).first()
        if user:
            db_password = user.password
            password = setPassword(password)
            if password == db_password:
                response = redirect("/index/")
                response.set_cookie("username",user.user_name)
                response.set_cookie("email",user.email)
                response.set_cookie("id",str(user.id))
                session["username"] = user.user_name
                return response
            else:
                error = "密码错误"
        else:
            error = "用户不存在"
    return render_template("login.html",**locals())

@main.route("/logout/")
def logout():
    response = redirect("/login/")
    response.delete_cookie("username")
    response.delete_cookie("email")
    response.delete_cookie("id")
    del session["username"]
    return response


@main.route("/base/")
def base():
    return render_template("base.html")


@main.route("/index/")
@loginValid
def index():
    return render_template("index.html",**locals())

from .get_Time import Calendar
import datetime
@main.route("/userinfo/")
@loginValid
def userinfo():
    calendar = Calendar().return_month()
    now = datetime.datetime.now()
    month = now.month
    return render_template("userinfo.html",**locals())