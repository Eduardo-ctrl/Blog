# 主业务逻辑中的视图和路由的定义
import datetime
import os

from flask import render_template, request, session, redirect
# 导入蓝图程序，用于构建路由

from . import main
# 导入db，用于操作数据库
from .. import db
# 导入实体类，用于操作数据库
from ..models import *


# 主页的访问路径
@main.route('/')
def index():
    # 查找 id 为1的 user 的信息
    # user = User.query.filter_by(id=1).first()
    # print(user.uname)
    # topics = user.topics.all()
    # for topic in topics:
    #     print(topic.title + ":" + topic.user.uname + ":" + topic.category.cate_name + ":" + topic.blogtype.type_name)
    categories = Category.query.all()
    topics = Topic.query.all()
    if "uid" in session and "uname" in session:
        user = User.query.filter_by(id=session["uid"]).first()
    return render_template('index.html', params=locals())


# 登录页面的访问路径
@main.route("/login", methods=["GET", "POST"])
def login_views():
    if request.method == "GET":
        if "uid" in session:
            return redirect("/")
        else:
            return render_template('login.html')
    else:
        loginname = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(loginname=loginname, upwd=password).first()
        if user:
            session["uid"] = user.id
            session["uname"] = user.uname
            return redirect("/")
        else:
            errMsg = "用户名或密码不正确"
            return render_template("login.html", errMsg=errMsg)


# 退出的访问路径
@main.route("/logout")
def logout_views():
    if "uid" in session and "uname" in session:
        del session["uid"]
        del session["uname"]
    return redirect("/")


# 注册页面的访问路径
@main.route("/register", methods=["GET", "POST"])
def register_views():
    if request.method == "GET":
        return render_template("register.html")
    else:
        user = User()
        user.loginname = request.form["loginname"]
        user.uname = request.form["username"]
        user.email = request.form["email"]
        user.url = request.form["url"]
        user.upwd = request.form["password"]
        # 将数据保存进数据库 - 注册
        db.session.add(user)
        # 手动提交，目的是为了获取提交后的 user 的 id
        db.session.commit()
        # 当 user 成功插入进数据库之后，程序会自动将所有信息取出来再赋值给 user
        session["uid"] = user.id
        session["uname"] = user.uname
        return redirect("/")


# 验证登录名是否已存在
@main.route("/register_test")
def register_test():
    loginname = request.args["loginname"]
    user = User.query.filter_by(loginname=loginname).first()
    if user:
        return "true"
    else:
        return "false"


# 发表博客的访问路径
@main.route('/release', methods=["GET", "POST"])
def release_views():
    if request.method == "GET":
        if "uid" not in session or "uname" not in session:
            return redirect("/login")
        else:
            uid = session["uid"]
            user = User.query.filter_by(id=uid).first()
            if user.is_author == 1:
                categories = Category.query.all()
                blogtypes = BlogType.query.all()
                return render_template("release.html", params=locals())
            else:
                return redirect("/")
    else:
        # 处理 post 请求，即发表博客的处理
        topic = Topic()
        topic.title = request.form["author"]
        topic.pub_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        topic.content = request.form["content"]
        if request.files["picture"]:
            file = request.files["picture"]
            last = file.filename.split(".")[1]
            dtime = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            filename = dtime + "." + last
            topic.images = "upload/" + filename
            # paths = os.path.dirname(__file__)
            paths = os.path.dirname(os.path.dirname(__file__))
            fdir = os.path.join(paths, "static/upload/", filename)
            file.save(fdir)
        topic.blogtype_id = request.form["list"]
        topic.category_id = request.form["category"]
        topic.user_id = session["uid"]
        db.session.add(topic)
        return redirect("/")


@main.route("/info",methods=["GET","POST"])
def info_views():
    if request.method == "GET":
        categories = Category.query.all()
        if "uid" in session and "uname" in session:
            uid = session["uid"]
            user = User.query.filter_by(id=uid).first()
        topic_id = request.args["topic_id"]
        topic = Topic.query.filter_by(id=topic_id).first()
        # 更新阅读量
        topic.read_num += 1
        db.session.add(topic)
        # 查找上一篇，下一篇
        topics = Topic.query.all()
        now_index = topics.index(topic)
        if now_index == 0:
            bf_topic = False
            af_topic = topics[now_index + 1]
        elif now_index == len(topics) - 1:
            bf_topic = topics[now_index - 1]
            af_topic = False
        else:
            bf_topic = topics[now_index - 1]
            af_topic = topics[now_index + 1]
        return render_template("info.html", params=locals())
    else:
        pass


@main.route('/list')
def list_views():
    return render_template('list.html')
