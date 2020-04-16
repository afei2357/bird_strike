import re
import random
import time
from datetime import datetime
import string
from flask import jsonify,request,g
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import error_response
from app.models import Permission
from app.models1 import Channel, Products, Pkcolor
from app.extensions import db


# 列出渠道页面
@bp.route('/channel', methods=['GET'])
@token_auth.login_required
def get_channels():
    def search(channels):
        if name:
            channels = [i for i in channels if re.search(r'%s'%(name), i.name)]
        return channels

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    name = request.args.get('name',type=str, default=None)
    
    if name:
        #print(Channel.query.filter(Channel.name.like('%{}%'.format(name))).all())
        data = Channel.to_collection_dict(
            Channel.query.filter(Channel.name.like('%'+name+'%'))\
                                .order_by(Channel.update_time.desc()), \
                                page, page_size)
    else:
        data = Channel.to_collection_dict(Channel.query.order_by(Channel.id.desc()), page, page_size)
    return jsonify({'code': 200, 'infos': data})


# 添加一个渠道
@bp.route('/channel', methods=['POST'])
@token_auth.login_required
def add_channel_info():
    data = request.get_json()
    if not data:
        return bad_request(_('You must post JSON data.'))
    channel = Channel()
    channel.from_dict(data)
    channel.invited_code = data['code'] + ''.join(random.sample(string.ascii_letters + string.digits, 8))
    channel.create_time = datetime.now()
    channel.update_time = datetime.now()
    db.session.add(channel)
    db.session.commit()
    return jsonify({'code': 200, 'msg': "添加成功"})

# 修改一个渠道
@bp.route('/channel/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_channel_info(id):
    channel = Channel.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return bad_request(_('You must post JSON data.'))
    ## 邀请码
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    try:
        channel.invited_code = channel.code + ''.join(random.sample(string.ascii_letters + string.digits, 8))
    except:
        channel.invited_code = data['code'] + ''.join(random.sample(string.ascii_letters + string.digits, 8))
    
    ## 产品,存ID
    channel.productsinfo = []
    input_products = [Products.query.filter(Products.product_name.startswith(i)).first() for i in data['products']]
    for i in input_products:
        channel.productsinfo.append(i)
    channel.from_dict(data)
    channel.update_time = datetime.now()
    db.session.add(channel)
    db.session.commit()
    return jsonify({'code': 200, 'msg': "修改成功"})

# 删除一个渠道
@bp.route('/channel/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_channel(id):
    channel = Channel.query.get_or_404(id)
    #if not g.current_user.can(Permission.ADMIN):
    #    return error_response(403)
    db.session.delete(channel)
    db.session.commit()
    return jsonify({'code': 200, 'msg': "删除成功"})

