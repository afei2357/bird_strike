import os
from datetime import datetime
from flask import jsonify,request,g
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import error_response
from app.models import Permission
from app.models1 import Channel,Pkcolor
from app.extensions import db

# 添加或修改一个数据
@bp.route('/pkcolor/<mainName>', methods=['POST'])
@token_auth.login_required
def add_color_info(mainName):
    ## 存在数据库
    data = request.get_json()
    color = data['color']
    channel = g.current_user.channel
    pkcolor = Pkcolor.query.filter(Pkcolor.channel == g.current_user.channel, \
                                   Pkcolor.types == mainName).first()
    if not pkcolor:
        pkcolor = Pkcolor()
    pkcolor.color = color
    pkcolor.types = mainName
    pkcolor.channel = channel
    db.session.add(pkcolor)
    db.session.commit()
    return jsonify({'code': 200, 'msg': "添加成功"})

# 列出数据
@bp.route('/pkcolor/<mainName>', methods=['GET'])
@token_auth.login_required
def get_color_info(mainName):
    pkcolor = Pkcolor()
    pkcolor = Pkcolor.query.filter(Pkcolor.channel == g.current_user.channel, Pkcolor.types == mainName).first()
    data = ""
    if pkcolor:
        data = pkcolor.to_dict()
    return jsonify({'code': 200, 'msg': "请求成功", 'data':data})
