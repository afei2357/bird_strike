import re
from datetime import datetime
from flask import jsonify,request,g
from app.api import bp
from app.api.auth import token_auth
from flask_babel import gettext as _
from app.api.errors import error_response
from app.model.models import Permission
from app.model.models1 import  UpGtData, Channel, Products, Detecter
from app.model.models_orders import OrderHlth, OrderGnic, OrderMed
from app.extensions import db
from app.utils.reporter import RunInfo
from app.utils.tasks import generate_report_risk
from app.utils.tools import get_order_code
from app.utils.getrisk import cvdrisk10,cvdrisk10_expect,get_cvd_risk_pic,check_value
from config import db_dic
from app.utils.tools import *


# 列出信息的订单页面
@bp.route('/order_risk/info/<mainName>', methods=['GET'])
@token_auth.login_required
def get_orders_risk(mainName):
    print('=========----------------')
    def search(orders):
        ### 搜索关键词
        if sample_code:
            orders = [i for i in orders if re.search(r'%s'%(sample_code), i.sample_code)]
        if channel_name:
            # 用( i.channel_name or '') 的原因是，有部分订单并没有设定渠道名称。
            orders = [i for i in orders if re.search(r'%s'%(channel_name), ( i.channel_name or '')  )]
        if name:
            orders = [i for i in orders if re.search(r'%s'%(name), i.name)]
        if order_num:
            orders = [i for i in orders if i.order_num and re.search(r'%s'%(order_num), i.order_num)]
        if orderstate:
            orders = [i for i in orders if i.orderstate and re.search(r'%s'%(orderstate), i.orderstate)]
        return orders

    def check_state(orders):
        for order in orders:
            if order.jobstate == 'FAILURE':
                order.orderstate = '报告失败'
            elif order.jobstate == 'SUCCESS':
                order.orderstate = '报告完成'             
            elif order.img_path:
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
    channel_name = request.args.get('channel_name',type=str, default=None)
    sample_code = request.args.get('sample_code',type=str, default=None)
    order_num = request.args.get('order_num',type=str, default=None)
    orderstate = request.args.get('orderstate',type=str, default=None)
    # 如果没有查询条件:
    if not (sample_code or channel_name or name or order_num or orderstate):
        ## 总的项目管理
        if g.current_user.can(Permission.SUPERPM):
            paginate_query = db_dic[mainName].query.filter(db_dic[mainName].delete_at== None)\
                             .order_by(db_dic[mainName].create_time.desc())\
                             .paginate(page, page_size)
            orders = paginate_query.items

        ## 渠道管理员
        elif g.current_user.can(Permission.ADMIN):
            ## 获取该渠道所有的成员
            all_chnel_users = Channel.query.filter_by(id = g.current_user.channel_id).first().users.all()
            ## 获取这些成员下所有各个模块的所有订单id
            users_id = [i.id for i in  all_chnel_users]
            paginate_query = db_dic[mainName].query.filter(db_dic[mainName].owner_id.in_(users_id))\
                             .filter(db_dic[mainName].delete_at== None)\
                             .order_by(db_dic[mainName].create_time.desc())\
                             .paginate(page, page_size)
            orders = paginate_query.items
        ## 一般操作员
        else:
            users_id = [ g.current_user.id ]
            paginate_query = db_dic[mainName].query.filter(db_dic[mainName].owner_id.in_(users_id))\
                             .filter(db_dic[mainName].delete_at== None)\
                             .order_by(db_dic[mainName].create_time.desc())\
                             .paginate(page, page_size)
            orders = paginate_query.items

        orders = check_state(orders) ## 刷新订单状态
        data = {'items': [item.to_dict() for item in orders],
                '_meta': {
                    'page': page,
                    'per_page': page_size,
                    'total_pages': paginate_query.pages, 
                    'total_items': paginate_query.total 
                    }
                }

    # 如果有查询条件,则用原来的逻辑：
    else:
        ## 总的项目管理
        if g.current_user.can(Permission.SUPERPM):
            orders = db_dic[mainName].query.filter().all()
        ## 渠道管理员
        elif g.current_user.can(Permission.ADMIN):
            ## 获取该渠道所有的成员
            all_chnel_users = Channel.query.filter_by(id = g.current_user.channel_id).first().users.all()
            ## 获取这些成员下所有各个模块的所有订单id
            if mainName == 'health':
                orders =  [j for i in  all_chnel_users for j in i.orders_health.all()]
            if mainName == 'medicine':
                orders =  [j for i in  all_chnel_users for j in i.orders_medicine.all()]
            if mainName == 'genetic':
                orders =  [j for i in  all_chnel_users for j in i.orders_genetic.all()]
            if mainName == 'info':
                orders =  [j for i in  all_chnel_users for j in i.order_info.all()]
            
        ## 一般操作员
        else:
            ## 不同模块
            if mainName == 'health':
                orders = g.current_user.orders_health.all()
            if mainName == 'medicine':
                orders = g.current_user.orders_medicine.all()
            if mainName == 'genetic':
                orders = g.current_user.orders_genetic.all()
            if mainName == 'info':
                orders = g.current_user.order_info.all()
    
        orders = search(orders) ## 搜索
        orders = check_state(orders) ## 刷新订单状态
        order_ids = [i.id for i in orders]
        data = db_dic[mainName].to_collection_dict(
            ##db_dic[mainName].query.filter_by(owner_id = order_ids)\
            db_dic[mainName].query.filter(db_dic[mainName].id.in_(order_ids))\
                                    .filter(db_dic[mainName].delete_at== None)\
                                    .order_by(db_dic[mainName].create_time.desc()), \
                                    page, page_size)
    return jsonify({'code': 200, 'infos': data})


# 添加一个订单
@bp.route('/order_risk/<mainName>', methods=['POST'])
@token_auth.login_required
def add_order_info_risk(mainName):
    data = request.get_json()
    if not data:
        return bad_request(_('You must post JSON data.'))
    
    ## 渠道
    channel = g.current_user.channel
    ## 关联产品
    if mainName == 'cvdrisk':
        data['detection_items'] = 'RHM017心血管事件风险评估'

    data['sample_code'] = data['name'] 
    data.setdefault('age',int((datetime.now() - datetime.strptime(data['birthday'],"%Y-%m-%d")).days/365))
    info,msg1 =  check_value(data)
    risk,msg2 = cvdrisk10(info)
    expect_risk,expect_msg = cvdrisk10_expect(info)
    data['risk'] = risk
    data['expect_risk'] = expect_risk

    outdir = "project_data/results/%s/CvdRisk/%s"%(channel.code,data['sample_code'])
    data['img_path'] = get_cvd_risk_pic(check_value(data)[0] ,outdir=outdir)
    data['orderstate'] = '解读中'

    ### 添加到受检者表单
    detecter = Detecter.query.filter_by(name=data['name'], phone=data['phone'], gender=data['gender']).first()
    ### 没有受检者则添加受检者
    if not detecter:
        detecter = Detecter()
        detecter.owner_id = g.current_user.id
        detecter.channel_id = channel.id
        detecter.detecter_code = channel.code + get_order_code()
        detecter.create_time = datetime.now()
    detecter.update_time = datetime.now()

    order = ''
    ### 存在受检者的风险订单，且产品名称一致
    if len(detecter.order_risk.all())>=1:
        for each in detecter.order_risk.all():
            if each.products.product_name == data['detection_items']:
                order = each
    if order:
        order.from_dict(data)
        detecter.from_dict(data)
    else:
        ### 重新新建订单
        order = db_dic[mainName]()
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
        order_num = channel.code + mainName.upper()[0:2] + get_order_code(serial_num)
        order.order_num = order_num
        ## 时间
        order.create_time = datetime.now()
       
        ## 关联产品
        products = Products.query.filter(Products.product_name.startswith(data['detection_items'])).first()
        if products:
            order.products = products

        ## 增加渠道，增加订单
        order.detecter.append(detecter)
        detecter.from_dict(data)
        db.session.add(channel)
        db.session.add(order)
        db.session.add(detecter)
    
    
    db.session.commit()
    #order_clininfo = order.detecter.first().infos[-1].to_dict()
    

    #order_clininfo.setdefault('risk',risk)
    return jsonify({'code': 200, 'msg': "添加成功"})

# 修改一个订单
@bp.route('/order_risk/<mainName>/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_order_info_risk(mainName, id):
    order = db_dic[mainName].query.get_or_404(id)
    data = request.get_json()
    if not data:
        return bad_request(_('You must post JSON data.'))
    
    detecter = order.detecter.first()
    order.from_dict(data)
    
    detecter.update_time = datetime.now()
    detecter.from_dict(order.to_dict())
    db.session.commit()
    return jsonify({'code': 200, 'msg': "修改成功"})
    

# 删除一个订单
@bp.route('/order_risk/<mainName>/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_order_risk(mainName, id):
    order = db_dic[mainName].query.get_or_404(id)
    #if not g.current_user.can(Permission.ADMIN):
    #    return error_response(403)
    #order.delete_at =   datetime.now().strftime('%Y.%m.%d_%H.%M.%S')
    order.delete_at = datetime.now()
    #detecter = Detecter.query.filter_by(name=order.name, phone=order.phone, gender=order.gender).first()
    for detecter in order.detecter:
        order.detecter.remove(detecter)
    #db.session.delete(order)
    db.session.commit()
    return jsonify({'code': 200, 'msg': "删除成功"})


# 下载数据
@bp.route('/order_risk/download/<mainName>/<int:id>/<flag>', methods=['GET'])
@token_auth.login_required
def getDownLoad_risk(mainName, id, flag):
    order = db_dic[mainName].query.get_or_404(id)
    if flag == 'pdf':
        result_url = order.pdf_path
    elif flag == 'docx':
        result_url = order.docx_path
    return jsonify({'code': 200, 'url': result_url, 'msg': "下载开始"})

# 任务运行
@bp.route('/order_risk/run/<mainName>/<int:id>', methods=['GET', 'POST'])
@token_auth.login_required
def job_run_order_risk(mainName, id):
    ###celery之前
    """
    order = db_dic[mainName].query.get_or_404(id)
    client_snp = {i.rs:i.gt for i in order.updata.gtinfo.all()}
    client_info = (order.to_dict())
    ins = RunInfo(client_info, client_snp, "project_data/results")
    order.docx_path = ins.docx_path
    order.pdf_path = ins.pdf_path
    order.report_date = datetime.now()
    db.session.commit()
    return jsonify({'code': 200, 'msg': "ID%s递交成功"%(str(id))})
    """
    from config import basedir
    ## 加入celery后
    from app import create_app
    from config import basedir
    app = create_app()
    task = generate_report_risk.delay(mainName,id, g.current_user.channel.code)
    ##task = generate_report(mainName,id)
    ## 此时任务状态是PENNDING，重置所有
    order = db_dic[mainName].query.get_or_404(id)
    if order:
        try:
            os.remove(os.path.join(basedir,order.docx_path))
            os.remove(os.path.join(basedir,order.pdf_path))
        except Exception as e:
            order.docx_path = ''
            order.pdf_path = ''
            order.taskid = task.task_id
    db.session.commit()
    
    """
    print('--------------task.info============')
    print(task.info)
    print(task.id)
    print(task.state)
    print('--------------task.state============')
    """
    return jsonify({'code': 200, 'msg': "ID%s递交成功"%(str(id)),'task_id':task.id})


@bp.route('/order_risk/run/<mainName>/<int:id>/<task_id>', methods=['GET'])
#@token_auth.login_required
def job_run_order_state_risk(mainName, id, task_id):
    task =  generate_report.AsyncResult(task_id)
    print(task)
    order = db_dic[mainName].query.get_or_404(id)
    order.jobstate = task.state
    print(task.state)
    db.session.commit()    
    return jsonify({'code': 200, 'msg': task.state}) # 一共有四种状态： PENDING,RUNNING,SUCCESS,FAILURE

