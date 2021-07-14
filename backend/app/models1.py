from app.extensions import db
from datetime import datetime
from flask import url_for
import re

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, **kwargs):
        # 如果当前没有任何资源时，或者前端请求的 page 越界时，都会抛出 404 错误
        # 由 @bp.app_errorhandler(404) 自动处理，即响应 JSON 数据：{ error: "Not Found" }
        resources = query.paginate(page, per_page)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            }
        }
        return data

channel_products = db.Table('channel_products',
                       db.Column('channal_id',db.Integer,db.ForeignKey("channel.id"),primary_key=True),
                       db.Column('products_id',db.Integer,db.ForeignKey("products.id"),primary_key=True)
                       )

class Upcover(db.Model):
    __tablename__ = 'upcover'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(64))
    types = db.Column(db.String(64))
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))

    def to_dict(self):
        data = {
            'id': self.id,
            'url': self.url
        }
        return data

class Pkcolor(db.Model):
    __tablename__ = 'pkcolor'
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(64))
    types = db.Column(db.String(64))
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))

    def to_dict(self):
        data = {
            'id': self.id,
            'color': self.color
        }
        return data

        
class Channel(PaginatedAPIMixin, db.Model):
    __tablename__ = 'channel'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    code = db.Column(db.String(64))
    invited_code = db.Column(db.String(64))
    products = db.Column(db.String(64))
    create_time = db.Column(db.DateTime, default=datetime.now())# 录入时间
    update_time = db.Column(db.DateTime, default=datetime.now()) # 邀请码更新时间
    serial_num = db.Column(db.Integer)
    serial_time = db.Column(db.DateTime, default=datetime.now())
    users = db.relationship('User', backref='channel', lazy='dynamic')
    updata = db.relationship('UpData', backref='channel', lazy='dynamic')
    upcover = db.relationship('Upcover', backref='channel', lazy='dynamic')
    pkcolor = db.relationship('Pkcolor', backref='channel', lazy='dynamic')
    def __init__(self,code,name):
        self.code = code
        self.name = name
        
    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            if key in ['create_time', 'update_time']:
                # value = getattr(self, key).strftime("%Y-%m-%d %H:%M:%S")
                value = getattr(self, key)
                if value and isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d %H:%M")
            else:
                value = getattr(self, key)
            result[key] = value
        result['products'] = [i.product_name.split('@')[0].split('#')[0] for i in self.productsinfo.all()]
        manager = [i for i in self.users.all() if str(i.role)  == '渠道管理员']
        if manager:
            result['phone'] = manager[0].phone
            result['admin'] = manager[0].username
            result['contact'] = manager[0].name
            result['address'] = manager[0].location
            result['email'] = manager[0].email
        return result

    def from_dict(self, data):
        for field in ['name', 'code', 'invited_code']:
            if field in data:
                setattr(self, field, data[field])


products_indicates = db.Table('products_indicates',
                       db.Column('Products_id',db.Integer,db.ForeignKey("products.id"),primary_key=True),
                       db.Column('Indicates_id',db.Integer,db.ForeignKey("indicates.id"),primary_key=True)
                       )

class Products(PaginatedAPIMixin, db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(64))
    product_class = db.Column(db.String(64))
    state = db.Column(db.String(64))
    users = db.Column(db.String(64))
    diseases = db.Column(db.String(64))
    drug = db.Column(db.String(64))
    personality = db.Column(db.String(64))
    front_end_json = db.Column(db.String(64))
    last_edit = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    order_health = db.relationship('OrderHlth', backref='products', lazy='dynamic')
    order_medicine = db.relationship('OrderMed', backref='products', lazy='dynamic')
    channel_info = db.relationship('Channel', secondary=channel_products, backref=db.backref('productsinfo',lazy='dynamic'), lazy='dynamic')

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            if key in ['last_edit', 'update_time']:
                # value = getattr(self, key).strftime("%Y-%m-%d %H:%M:%S")
                value = getattr(self, key)
                if value and isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d %H:%M")
            else:
                value = getattr(self, key)
            result[key] = value
        return result

    def from_dict(self, data):
        for field in ['product_name', 'product_class', 'state', 'users', \
                      'front_end_json', 'personality', 'drug', 'diseases']:
            if field in data:
                if field in ['users','personality','drug','diseases']:
                    setattr(self, field, ';'.join(data[field]))
                else:
                    setattr(self, field, data[field])

class Indicates(db.Model):
    __tablename__ = 'indicates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    primary_name = db.Column(db.String(64))
    primary_code = db.Column(db.String(12))
    secondary_name = db.Column(db.String(64))
    json_info = db.Column(db.Text)
    update_time = db.Column(db.DateTime)
    products_id = db.relationship('Products', secondary=products_indicates, backref=db.backref('indicatesinfo',lazy='dynamic'), lazy='dynamic')

class OrderHlth(PaginatedAPIMixin, db.Model):
    __tablename__ = 'order_health'
    id = db.Column(db.Integer, primary_key=True)
    order_num = db.Column(db.String(64)) # 订单号 
    customer_code = db.Column(db.String(64))      #客户编码
    name = db.Column(db.String(64))     # 姓名
    gender = db.Column(db.String(10))     # 性别
    birthday = db.Column(db.DateTime)    # 出生日期
    phone = db.Column(db.String(30))     # 手机号
    sample_code = db.Column(db.String(64)) #样本编号
    sample_class = db.Column(db.String(100))     # 样品类型
    create_time = db.Column(db.DateTime)      # 录入时间
    sample_date = db.Column(db.DateTime)      # 采样时间
    receive_date = db.Column(db.DateTime)      # 到样时间
    report_date = db.Column(db.DateTime) # 报告时间
    ##detection_items = db.Column(db.String(100)) #检测项目
    channel_name = db.Column(db.String(300)) #客户来源
    template = db.Column(db.String(64)) # 公司模板
    pdf_path = db.Column(db.String(64)) # pdf结果路径
    docx_path = db.Column(db.String(64)) #docx结果路径
    orderstate = db.Column(db.String(64))  #订单状态
    jobstate = db.Column(db.String(64))
    
    ### 该订单的用户
    products_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    updata_id = db.Column(db.Integer, db.ForeignKey('updata.id'))# 样品编码
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 传递给前端
    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            if key in ['sample_date', 'receive_date', 'report_date','birthday']:
                # value = getattr(self, key).strftime("%Y-%m-%d %H:%M:%S")
                value = getattr(self, key)
                if value and isinstance(value,datetime):
                    value = value.strftime("%Y-%m-%d")
            else:
                value = getattr(self, key)
            result[key] = value
        try:
            result['detection_items'] = self.products.product_name.split('@')[0].split('#')[0]
        except:
            result['detection_items'] = None
        try:
            result['template'] = re.search(r'@([d|s|g|h]\d)', self.products.product_name).groups()[0]
        except:
            result['template'] = None
        
        upcovers = self.owner.channel.upcover.all()
        pkcolor = self.owner.channel.pkcolor.all()
        result['front_cover'] = []
        result['end_cover'] = []
        
        for upcover in upcovers:
            if upcover.types == 'front_cover':
                result['front_cover'].append(upcover.url)
            elif upcover.types == 'end_cover':
                result['end_cover'].append(upcover.url)
        
        color_info = {}
        for pkcolor in self.owner.channel.pkcolor.all():
            color_info.setdefault(pkcolor.types, pkcolor.color)
        result['color'] = color_info
            ## 关联数据
        return result

    def from_dict(self, data):
        for field in ['name', 'gender', 'birthday','sample_code', 'detection_items', 'channel_name', 'phone']:
            if field in data:
                if field in ['birthday']:
                    setattr(self, field, datetime.strptime(data[field],'%Y-%m-%d'))
                else:
                    setattr(self, field, data[field])
        #if data.get('receive_date'):
        #   self.receive_date = datetime.strptime(data['receive_date'],'%Y-%m-%d')

class OrderGnic(PaginatedAPIMixin, db.Model):
    __tablename__ = 'order_genetic'
    id = db.Column(db.Integer, primary_key=True)     
    info_code = db.Column(db.String(64))      #信息卡编号
    customer_code = db.Column(db.String(64))      #客户编码
    name = db.Column(db.String(64))     # 姓名
    gender = db.Column(db.String(10))     # 性别
    #grade = db.Column(db.String(64))     
    #birthday = db.Column(db.DateTime, default=datetime.now())
    birthday = db.Column(db.String(30))     # 出生日期
    height = db.Column(db.String(10))     # 身高
    #weight = db.Column(db.String(10))     # 体重
    #waist = db.Column(db.String(10))     #  腰围
    national = db.Column(db.String(20))     #  民族
    origin = db.Column(db.String(70))     #  籍贯
    phone = db.Column(db.String(30))     # 手机号
    id_number = db.Column(db.String(70))     # 身份证号码
    address = db.Column(db.String(300))     # 联系地址
    #wechat = db.Column(db.String(30))     # 微信
    email = db.Column(db.String(100))     # 邮箱
    sample_code = db.Column(db.String(100))      # 样品编码
    sample_class = db.Column(db.String(100))     # 样品类型
    number = db.Column(db.String(64))     # 数量
    create_time = db.Column(db.DateTime, default=datetime.now())      # 录入时间
    sample_date = db.Column(db.DateTime, default=datetime.now())      # 采样时间
    receive_date = db.Column(db.DateTime, default=datetime.now())     # 到样时间
    report_date = db.Column(db.DateTime, default=datetime.now()) # 报告时间
    #detections = db.Column(db.String(64))     #
    detection_items = db.Column(db.String(100)) #检测项目
    channel_name = db.Column(db.String(300)) #渠道名称
    template = db.Column(db.String(64)) # 公司模板
    results = db.Column(db.String(64))
    results2 = db.Column(db.String(64))
    #report_date = db.Column(db.String(64))
    data_path = db.Column(db.String(64))
    power = db.Column(db.Text(2000))     #
    hospital = db.Column(db.String(64))
    department = db.Column(db.String(64))
    doctor = db.Column(db.String(64))
    clinical_bg = db.Column(db.String(64))
    # -------add------
    raw_file = db.Column(db.Boolean)
    flag = db.Column(db.String(10))

    # ---------add-------

    # 传递给前端
    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            if key == 'sample_date' or key == 'receive_date' or key == 'report_date':
                # value = getattr(self, key).strftime("%Y-%m-%d %H:%M:%S")
                value = getattr(self, key)
                if value and isinstance(value,datetime): 
                    value = value.strftime("%Y-%m-%d")
            else:
                value = getattr(self, key)
            result[key] = value
        return result
    
    def from_dict(self, data):
        for field in ['name', 'gender', 'sample_code', 'detection_items', 'channel_name', 'phone']:
            if field in data:
                setattr(self, field, data[field])  

        
class OrderMed(PaginatedAPIMixin, db.Model):
    __tablename__ = 'order_medicine'
    id = db.Column(db.Integer, primary_key=True)
    order_num = db.Column(db.String(64)) # 订单号 
    customer_code = db.Column(db.String(64))      #客户编码
    name = db.Column(db.String(64))     # 姓名
    gender = db.Column(db.String(10))     # 性别
    birthday = db.Column(db.DateTime)    # 出生日期
    phone = db.Column(db.String(30))     # 手机号
    sample_class = db.Column(db.String(100))     # 样品类型
    create_time = db.Column(db.DateTime)      # 录入时间
    sample_date = db.Column(db.DateTime)      # 采样时间
    receive_date = db.Column(db.DateTime)      # 到样时间
    report_date = db.Column(db.DateTime)  # 报告时间
    ## detection_items = db.Column(db.String(100)) #检测项目
    hospital = db.Column(db.String(64))  #医院名称
    department = db.Column(db.String(64)) #科室
    doctor = db.Column(db.String(64)) #送检医生
    clinical_bg = db.Column(db.String(64)) #临床背景
    pdf_path = db.Column(db.String(64)) # pdf结果路径
    docx_path = db.Column(db.String(64)) #docx结果路径
    jobstate = db.Column(db.String(64))  #任务运行状态
    orderstate = db.Column(db.String(64))  #订单状态
    sample_code = db.Column(db.String(64)) # 样品编码
    ### 该订单的用户
    products_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    updata_id = db.Column(db.Integer, db.ForeignKey('updata.id'))# 样品编码
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 传递给前端
    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            if key in ['sample_date', 'receive_date', 'report_date','birthday']:
                # value = getattr(self, key).strftime("%Y-%m-%d %H:%M:%S")
                value = getattr(self, key)
                if value and isinstance(value,datetime):
                    value = value.strftime("%Y-%m-%d")
            else:
                value = getattr(self, key)
            result[key] = value
        try:
            result['detection_items'] = self.products.product_name.split('@')[0].split('#')[0]
        except:
            result['detection_items'] = None
        try:
            result['template'] = re.search(r'@([d|s|g|h]\d)', self.products.product_name).groups()[0]
        except:
            result['template'] = None
        return result

    def from_dict(self, data):
        for field in ['name', 'gender','sample_code', 'hospital', 'department', 'clinical_bg', 'doctor', 'phone']:
            if field in data:
                setattr(self, field, data[field])
        
        if data.get('birthday'):
            self.birthday = datetime.strptime(data['birthday'],'%Y-%m-%d')
        else:
            self.birthday = None

updata_rs = db.Table('updata_rsgt',
                       db.Column('Sample_id',db.Integer,db.ForeignKey("updata.id"),primary_key=True),
                       db.Column('Rs_id',db.Integer,db.ForeignKey("rsgt.id"),primary_key=True)
                       )

class UpData(PaginatedAPIMixin, db.Model):
    __tablename__ = 'updata'
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    data_num = db.Column(db.String(64)) # 订单号 
    sample_id = db.Column(db.String(64))
    creation_time = db.Column(db.String(64))
    update_time = db.Column(db.String(64))
    rs_num = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    order_health = db.relationship('OrderHlth', backref='updata', lazy='dynamic')
    order_medicine = db.relationship('OrderMed', backref='updata', lazy='dynamic')
    
    ### 传给前端
    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            if key == 'update_time' or key == 'creation_time':
                # value = getattr(self, key).strftime("%Y-%m-%d %H:%M:%S")
                value = getattr(self, key)
                if value and isinstance(value,datetime): 
                    value = value.strftime("%Y-%m-%d")
            else:
                value = getattr(self, key)
            result[key] = value
        try:
            result['channel'] = Channel.query.get(self.channel_id).name
        except Exception as e:
            print(e)
        return result

class ComVar(PaginatedAPIMixin, db.Model):
    __tablename__ = 'rsgt'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rs = db.Column(db.String(64))
    gt = db.Column(db.String(64))
    datacode = db.relationship('UpData', secondary=updata_rs, backref=db.backref('gtinfo',lazy='dynamic'), lazy='dynamic')
    
    #gene_id	= db.Column(db.String(64))
    #delete_at = db.Column(db.String(64))
    #ref	= db.Column(db.String(64))
    #alt_db	= db.Column(db.String(64))
    #chr = db.Column(db.String(64))
    #pos	= db.Column(db.String(64))
    #hgvs = db.Column(db.String(64))

class OrderSeq(PaginatedAPIMixin, db.Model):
    __tablename__ = 'order_seq'
    id = db.Column(db.Integer, primary_key=True)
    sample_code         = db.Column(db.String(30)) #
    detection_items     = db.Column(db.String(30)) #
    department          = db.Column(db.String(30)) #
    order_date          = db.Column(db.String(30)) #
    order_num           = db.Column(db.String(30)) # 订单号
    report_date         = db.Column(db.String(30)) #
    conclusion          = db.Column(db.String(30)) #
    customer_code = db.Column(db.String(64))      #客户编码
    sample_class = db.Column(db.String(100))     # 样品类型
    #create_time = db.Column(db.DateTime)      # 录入时间
    #sample_date = db.Column(db.DateTime)      # 采样时间
    #receive_date = db.Column(db.DateTime)      # 到样时间
    #report_date = db.Column(db.DateTime)  # 报告时间

    create_time = db.Column(db.String(30))      # 录入时间
    sample_date = db.Column(db.String(30))      # 采样时间
    receive_date =db.Column(db.String(30))      # 到样时间
    report_date = db.Column(db.String(30))  # 报告时间
    ## detection_items = db.Column(db.String(100)) #检测项目
    pdf_path = db.Column(db.String(64)) # pdf结果路径
    docx_path = db.Column(db.String(64)) #docx结果路径
    jobstate = db.Column(db.String(64))  #任务运行状态
    orderstate = db.Column(db.String(64))  #订单状态
    ### 该订单的用户

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    delivery = db.relationship('Delivery')
    #DNA_info = db.relationship('DNAInfo',backref=db.backref('order_seq'))
    #seqData = db.relationship('SeqData')

    #def __init__(self,order_num,sample_date):
    #    self.order_num = order_num
    #    self.sample_date = sample_date
        
    def from_dict(self, data):
        columns = self.__table__.columns.keys()
        for field in columns:
            if field in data:
                setattr(self, field, data[field])
        
class DNAInfo(PaginatedAPIMixin, db.Model):
    __tablename__ = 'DNAInfo_tb'
    id              = db.Column(db.Integer, primary_key=True)
    sample_code     = db.Column(db.String(30)) #
    concentration   = db.Column(db.String(200)) #
    volumes         = db.Column(db.String(30)) #
    quantity        = db.Column(db.String(30)) #
    OD260_OD230     = db.Column(db.String(30)) #
    OD260_OD280     = db.Column(db.String(30)) #
    extraction_date = db.Column(db.String(30)) #

    # 一个样品可能会对几个基因测序,所欲Delivery与SeqData是一对多关系
    delivery = db.relationship('Delivery')
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'))

    #def __init__(self):
    #    pass

    def from_dict(self, data):
        columns = self.__table__.columns.keys()
        for field in columns:
            if field in data:
                setattr(self, field, data[field])
        
class Delivery(PaginatedAPIMixin, db.Model):
    __tablename__ = 'delivery'
    id = db.Column(db.Integer, primary_key=True)
    sample_code           = db.Column(db.String(30)) #
    event_flight          = db.Column(db.String(30)) #
    event_describe        = db.Column(db.String(200)) #
    event_date            = db.Column(db.String(30)) #
    event_date_region     = db.Column(db.String(30)) #
    sample_person         = db.Column(db.String(30)) #
    event_place           = db.Column(db.String(30)) #
    sample_type           = db.Column(db.String(30)) #
    sample_preservation   = db.Column(db.String(30)) #
    sample_status         = db.Column(db.String(30)) #
    delivery_person       = db.Column(db.String(30)) #
    delivery_person_phone = db.Column(db.String(30)) #
    delivery_date         = db.Column(db.String(30)) #
    express_company       = db.Column(db.String(30)) #
    express_num           = db.Column(db.String(30)) #
    receive_date          = db.Column(db.String(30)) #
    remarks               = db.Column(db.String(100)) #
    delivery_num          = db.Column(db.String(30)) #

    # 一个订单可能有各个样品,所欲Order_seq与Delivery是一对多关系
    orderSeq_id = db.Column(db.Integer, db.ForeignKey('order_seq.id'))
    orderSeq = db.relationship('OrderSeq')
    #def __init__(self):
    #    pass

    # 一个样品可能会对几个基因测序,所欲Delivery与SeqData是一对多关系
    seqData = db.relationship('SeqData')
    DNA_Info = db.relationship('DNAInfo')

    def from_dict(self, data):
        columns = self.__table__.columns.keys()
        for field in columns:
            if field in data:
                setattr(self, field, data[field])


class SeqData(PaginatedAPIMixin, db.Model):
    __tablename__ = 'seqData'
    id = db.Column(db.Integer, primary_key=True)
    data_num = db.Column(db.String(64)) 
    path = db.Column(db.String(200)) # 下机数据的路径 
    gene_name = db.Column(db.String(10))     # 基因
    FR = db.Column(db.String(64))      #测序是正向或者反向
    #date = db.Column(db.DateTime)     # 日期
    date = db.Column(db.String(64))     # 日期
    info = db.Column(db.String(100))    # 
    raw_data = db.Column(db.String(2000)) # 保存原始测序数据
    creation_time = db.Column(db.String(64))
    update_time = db.Column(db.String(64))
    delete_at = db.Column(db.DateTime)    # 删除日期

    # 一个样品可能会对几个基因测序,所欲Delivery与SeqData是一对多关系
    delivery = db.relationship('Delivery')
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'))

    #def __init__(self,path,gene,FR,date,info):
    #    self.path= path
    #    self.gene = gene
    #    self.FR = FR
    #    self.date = date
    #    self.info  = info

    def from_dict(self, data):
        columns = self.__table__.columns.keys()
        columns.remove('id')
        for field in columns:
            if field in data:
                setattr(self, field, data[field])
