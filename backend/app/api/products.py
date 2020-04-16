from datetime import datetime
from flask import jsonify,request,g
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import error_response
from app.models1 import Products
from app.extensions import db


# 列出产品页面
@bp.route('/products', methods=['GET'])
@token_auth.login_required
def get_products():
    def search(products):
        if name:
            productss = [i for i in productss if re.search(r'%s'%(name), i.name)]
        return productss

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    name = request.args.get('name',type=str, default=None)

    if name:
        #print(products.query.filter(products.name.like('%{}%'.format(name))).all())
        data = Products.to_collection_dict(
            Products.query.filter(Products.product_name.like('%'+name+'%'))\
                                .order_by(Products.update_time.desc()), \
                                page, page_size)
    else:
        data = Products.to_collection_dict(Products.query.order_by(Products.id), page, page_size)
    return jsonify({'code': 200, 'infos': data})


# 添加产品信息
@bp.route('/products', methods=['POST'])
@token_auth.login_required
def add_products_info():
    datas = request.get_json()

    if not datas:
        return bad_request(_('You must post JSON data.'))
    
    exits_ids = [i.id for i in Products.query.all()]
    current_ids = [i['id'] for i in datas]

    del_ids = set(exits_ids) - set(current_ids)
    for id in del_ids:
        product = Products.query.get_or_404(id)
        db.session.delete(product)
    db.session.commit()

    for data in datas:
        products = Products.query.get(data['id'])
        if not products:
            products = Products()
            products.id = data['id']
        
        products.from_dict(data)
        products.last_edit = datetime.strptime(data['last_edit'],"%Y-%m-%d %H:%M:%S")
        products.update_time = datetime.now()
        db.session.add(products)
        db.session.commit()
    return jsonify({'code': 200, 'msg': "添加成功"})
