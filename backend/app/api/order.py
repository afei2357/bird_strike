import re
from datetime import datetime
from flask import jsonify,request,g
from app.api import bp
from app.api.auth import token_auth
from flask_babel import gettext as _
from app.api.errors import error_response
from app.models import Permission
from app.models1 import OrderMed, UpData, Products
from app.extensions import db
from app.rpt.tasks import generate_report
from app.utils.tools import get_order_code
from config import db_dic
from app.utils.tools import *


# 列出订单页面
@bp.route('/order', methods=['GET'])
@token_auth.login_required
def get_orders():
    def search(orders):
        ### 搜索关键词
        if sample_code:
            orders = [i for i in orders if re.search(r'%s'%(sample_code), i.sample_code)]
        if name:
            orders = [i for i in orders if re.search(r'%s'%(name), i.name)]
        if order_num:
            orders = [i for i in orders if i.order_num and re.search(r'%s'%(order_num), i.order_num)]
        if orderstate:
            orders = [i for i in orders if i.orderstate and re.search(r'%s'%(orderstate), i.orderstate)]
        return orders

    def check_state(orders):
        for order in orders:
            if order.report_date:
                if order.jobstate == 'FAILURE':
                    order.orderstate = '报告失败'
                elif order.jobstate == 'SUCCESS':
                    order.orderstate = '报告完成'
            elif order.updata:
                order.orderstate = '解读中'
            elif order.receive_date:
                order.orderstate = '检测中'
            else:
                order.orderstate = '未到样'
            db.session.commit()
        return orders  

    ### 获取 get过来的信息
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    name = request.args.get('name',type=str, default=None)
    sample_code = request.args.get('sample_code',type=str, default=None)
    order_num = request.args.get('order_num',type=str, default=None)
    orderstate = request.args.get('orderstate',type=str, default=None)

    ## 总的项目管理
    if g.current_user.can(Permission.SUPERPM):
        orders = OrderMed.query.filter().all()
    ## 管理员
    elif g.current_user.can(Permission.ADMIN):
        orders = OrderMed.query.filter().all()
    ## 一般操作员
    else:
        ## 不同模块
        orders = g.current_user.orders_medicine.all()
    
    orders = search(orders) ## 搜索
    orders = check_state(orders) ## 刷新订单状态
    order_ids = [i.id for i in orders]
    
    data = OrderMed.to_collection_dict(
        ##db_dic[mainName].query.filter_by(owner_id = order_ids)\
        OrderMed.query.filter(OrderMed.id.in_(order_ids))\
                                .order_by(OrderMed.create_time.desc()), \
                                page, page_size)
    return jsonify({'code': 200, 'infos': data})

# 添加一个订单
@bp.route('/order', methods=['POST'])
@token_auth.login_required
def add_order_info():
    data = request.get_json()
    if not data:
        return bad_request(_('You must post JSON data.'))
    ## 判定订单是否有重复，样本编号 + 产品名称

    ## 关联产品
    if len(data['detection_items']) <=6:
        return jsonify({'code': 405, 'msg': "%stoo short"%(data['detection_items'])})
    products = Products.query.filter(Products.product_name.startswith(data['detection_items'])).first()
    orders = OrderMed.query.filter(OrderMed.sample_code == data['sample_code'], \
                               OrderMed.products == products).all()
    for order in orders:
        if order.owner.channel == g.current_user.channel:
            return jsonify({'code': 417, 'msg': "%s 渠道的 %s 产品已存在%s的订单"\
                   %(g.current_user.channel.name, products.product_name, data['sample_code'])})
     
    ### 重新新建订单
    order = OrderMed()
    order.from_dict(data)
    ## 关联用户
    order.owner_id = g.current_user.id
    ###订单

    ## 提取流水号
    channel = g.current_user.channel
    start_time = channel.serial_time
    serial_num = channel.serial_num
    if not serial_num:
        serial_num = 1
    create_time = datetime.now()
    ## 一天内重置流水码
    flag = False
    if start_time:
        if (create_time - start_time).days >= 1:
            flag = True
    else:
        flag = True
    if flag:
        serial_num = 1
        channel.serial_time = datetime.now()
    else:
        serial_num = serial_num + 1
    
    ## 订单号 渠道商编号 + 模块简写 + 随机码 + 流水码
    channel.serial_num = serial_num
    order_num = 'DRUG' + get_order_code(serial_num)
    order.order_num = order_num
    
    ## 时间
    order.create_time = datetime.now()
    ## 关联数据
    updata = UpData.query.filter_by(sample_id = data['sample_code']).first()
    if updata:
        order.updata = updata
    ## 关联产品
    if products:
        order.products = products
    
    
    ## 增加渠道，增加订单
    db.session.add(channel)
    db.session.add(order)
    db.session.commit()
    return jsonify({'code': 200, 'msg': "添加成功"})

# 修改一个订单
@bp.route('/order/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_order_info(id):
    order = OrderMed.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return bad_request(_('You must post JSON data.'))
    if data.get('detection_items', None):
        products = Products.query.filter(Products.product_name.startswith(data['detection_items'])).first()
        orders = OrderMed.query.filter(OrderMed.sample_code == data['sample_code'], \
                                OrderMed.products == products).all()
        for order_b in orders:
            if order_b.owner.channel == g.current_user.channel and order_b.id != order.id:
                return jsonify({'code': 417, 'msg': "%s 渠道的 %s 产品已存在%s的订单"\
                    %(g.current_user.channel.name, products.product_name, data['sample_code'])})
            ## 关联产品
        if products:
            order.products = products
    
    order.from_dict(data)
    if order.jobstate != 'SUCCESS':
        order.jobstate = ''

    if data.get('receive_date', None):
        order.receive_date = datetime.now()
    
    if data.get('sample_code', None):
        updata = UpData.query.filter(UpData.sample_id == order.sample_code).first()
        if not updata:
            order.updata = None
            order.report_date = None
        else:
            if order.updata:
                if not order.updata == updata:
                    order.updata = updata
            else:
                order.updata = updata

    db.session.commit()
    return jsonify({'code': 200, 'msg': "修改成功"})

# 删除一个订单
@bp.route('/order/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_order(id):
    order = OrderMed.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'code': 200, 'msg': "删除成功"})

# 罗列产品选择
@bp.route('/order/products', methods=['GET'])
@token_auth.login_required
def get_channel_products():
    products = g.current_user.channel.productsinfo
    products_info = {i.id:i.product_name.split('@')[0].split('#')[0] for i in products}
    return jsonify({'code': 200, 'msg': "添加成功", 'infos': products_info})


# 下载数据
@bp.route('/order/download/<int:id>/<flag>', methods=['GET'])
@token_auth.login_required
def getDownLoad(id, flag):
    order = OrderMed.query.get_or_404(id)
    if flag == 'pdf':
        result_url = order.pdf_path
    elif flag == 'docx':
        result_url = order.docx_path
    return jsonify({'code': 200, 'url': result_url, 'msg': "下载开始"})

# 任务运行
@bp.route('/order/run/<int:id>', methods=['GET', 'POST'])
@token_auth.login_required
def job_run_order(id):
    ###celery之前
    ## 加入celery后
    task = generate_report.delay(id)
    ##task = generate_report(mainName,id)
    order = OrderMed.query.get_or_404(id)
    if order:
        order.docx_path = ''
        order.pdf_path = ''
    db.session.commit()

    print('--------------task.info============')
    print(task.info)
    print(task.id)
    print(task.state)
    print('--------------task.state============')
    return jsonify({'code': 200, 'msg': "ID%s递交成功"%(str(id)),'task_id':task.id})

@bp.route('/order/run/<int:id>/<task_id>', methods=['PUT'])
@token_auth.login_required
def job_run_order_state(id, task_id):
    task =  generate_report.AsyncResult(task_id)
    order = OrderMed.query.get_or_404(id)
    order.jobstate = task.state
    db.session.commit()    
    return jsonify({'code': 200, 'msg': task.state}) # 一共有四种状态： PENDING,RUNNING,SUCCESS,FAILURE

