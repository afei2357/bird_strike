from flask import jsonify, g
from app.api import bp
from app.api.auth import basic_auth
from app.api.auth import token_auth
from app.models import User
from app.extensions import db


@bp.route('/login', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = g.current_user.get_jwt()
    # 每次用户登录（即成功获取 JWT 后），更新 last_seen 时间
    g.current_user.ping()
    db.session.commit()
    return jsonify({'code': 200, 'msg': "验证成功", 'token': token})
    ##return jsonify({'token': token})


@bp.route('/user/info', methods=['GET'])
@token_auth.login_required
def get_useinfo():
    user  = g.current_user
    data = {
        'username': user.username,
        'roles': [user.role.name],
        'avatar':  user.avatar(128),
        'channel': user.channel.name,
        'id': user.id
    }
    return jsonify({'code': 200, 'msg': "登录成功", 'data': data})


@bp.route('/user/logout', methods=['POST'])
def logout():
    return jsonify({'code': 200, 'msg': "登出成功"})