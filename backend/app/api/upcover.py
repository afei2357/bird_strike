import os
from datetime import datetime
from flask import jsonify,request,g
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import error_response
from app.models import Permission
from app.models1 import Channel,Upcover
from app.extensions import db
from app.utils.tools import *

# 添加一个数据
@bp.route('/upcover/<mainName>', methods=['POST'])
@token_auth.login_required
def add_cover_info(mainName):
    data = request.files.get("image")
    print(data)
    ## 渠道
    channel = g.current_user.channel
    ## 保存图片到路径
    dir_file = "project_data/upload/channelFig/%s"%(channel.code)
    if not os.path.exists(dir_file):
        #os.mkdir(dir_file)
        os.makedirs(dir_file)
    
    file_path = os.path.join(dir_file, channel.code + get_order_code() + '.' + data.mimetype.split('/')[1])
    data.save(file_path)
    ## 存在数据库
    upcover = Upcover()
    if os.path.exists(file_path):
        upcover.url = file_path
        upcover.types = mainName
        upcover.channel =  channel
        db.session.add(upcover)
        db.session.commit()

        new_data = {
            'image': upcover.url,
            'id' : upcover.id
        }
        return jsonify({'code': 200, 'msg': "添加成功", 'data':new_data})
    return jsonify({'code': 200, 'msg': "添加失败"})

# 列出数据
@bp.route('/upcover/<mainName>', methods=['GET'])
@token_auth.login_required
def get_cover_info(mainName):
    upcover = Upcover()
    upcover = Upcover.query.filter(Upcover.channel == g.current_user.channel, Upcover.types == mainName).all()
    data = []
    for each in upcover:
        data.append(each.to_dict())
    #data = upcover.to_dict()
    return jsonify({'code': 200, 'msg': "请求成功", 'data':data})


@bp.route('/upcover/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_cover_info(id):
    upcover = Upcover.query.get_or_404(id)
    os.remove(upcover.url)
    db.session.delete(upcover)
    db.session.commit()
    return jsonify({'code': 200, 'msg': "删除成功"})
