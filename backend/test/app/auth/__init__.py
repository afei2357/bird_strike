from flask import Blueprint
from app import login_manager

# 注册蓝图
auth_bp = Blueprint('auth_bp', __name__)