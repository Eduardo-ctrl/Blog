# 针对用户业务逻辑处理的视图和路由的定义
from flask import render_template
from . import user
from .. import db
from ..models import *


@user.route("/user")
def user_index():
    return "这是 user 中的首页"
