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

@main.route("/leave/",methods=["GET","POST"])
@loginValid
def leave():
    if request.method == "POST":
        data = request.form
        request_user = data.get("request_username")
        request_type = data.get("request_type")
        request_start_time = data.get("request_start_time")
        request_end_time = data.get("request_end_time")
        request_days = data.get("request_days")
        request_phone = data.get("request_phone")
        request_description = data.get("request_description")

        leave = Leave()
        leave.request_id = request.cookies.get("id")
        leave.request_name = request_user
        leave.request_type = request_type
        leave.request_start_time = request_start_time
        leave.request_end_time = request_end_time
        leave.request_days = request_days
        leave.request_phone = request_phone
        leave.request_description = request_description
        leave.request_status = "0"
        leave.save()
        return redirect('/leave_list/1/')
    return render_template("leave.html")

from .cut_page import Pager
@main.route("/leave_list/<int:page>/")
@loginValid
def leave_list(page):
    leaves = Leave.query.all()
    pager = Pager(leaves,2)
    page_data = pager.page_data(page)
    return render_template("leave_list.html",**locals())

from app import api
from flask_restful import Resource
@api.resource("/Api/leave/")
class LeaveApi(Resource):
    def __init__(self):
        """定义返回的格式"""
        super(LeaveApi, self).__init__()
        self.result = {
            "version":"1.0",
            "data":""
        }
    def set_data(self,leave):
        """定义返回的数据"""
        result_data = {
            "request_name":leave.request_name,
            "request_type":leave.request_type,
            "request_start_time":leave.request_start_time,
            "request_end_time":leave.request_end_time,
            "request_days":leave.request_days,
            "request_description":leave.request_description,
            "request_phone":leave.request_phone,
        }
        return result_data

    def get(self):
        """处理get请求
        """
        data = request.args #获取请求的数据
        id = data.get("id") #获取id
        if id :
            leave = Leave.query.get(int(id))
            result_data = self.set_data(leave)
        else: #id不存在  返回所有数据
            leaves = Leave.query.all()
            result_data = []
            for leave in leaves:
                result_data.append(self.set_data(leave))
        self.result["data"] = result_data
        return self.result

    def post(self):
        """这是post请求，负责保存数据"""
        data = request.form
        request_id = data.get("request_id")
        request_name = data.get("request_name")
        request_type = data.get("request_type")
        request_start_time = data.get("request_start_time")
        request_end_time = data.get("request_end_time")
        request_days = data.get("request_days")
        request_description = data.get("request_description")
        request_phone = data.get("request_phone")

        leave = Leave()
        leave.request_id = request_id
        leave.request_name = request_name
        leave.request_type = request_type
        leave.request_start_time = request_start_time
        leave.request_end_time = request_end_time
        leave.request_days = request_days
        leave.request_description = request_description
        leave.request_phone = request_phone
        leave.request_status = "0"
        leave.save()

        self.result["data"] = self.set_data(leave)
        return self.result

    def put(self):
        """put请求，负责修改数据"""
        data = request.form  #请求数据，类字典对象
        id = data.get("id")   #data里面的id
        leave = Leave.query.get(int(id)) #在数据库里面找到
        for key,value in data.items():
            if key != "id":
                setattr(leave,key,value)
        leave.save()
        self.result["data"] = self.set_data(leave)
        return self.result

    def delete(self):
        """delete请求，负责删除数据"""
        data = request.form
        id = data.get("id")
        leave = Leave.query.get(int(id))
        leave.delete()
        self.result["data"] = "%s 删除成功"%id
        return self.result
