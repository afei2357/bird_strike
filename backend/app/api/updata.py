import re
import time
from flask import jsonify,request,g
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import error_response,bad_request
from app.models import Permission
from app.models1 import ComVar, UpData
#from app.models1 import *
from app.extensions import db
from app.utils.tools import *
from sqlalchemy import or_
from flask_babel import gettext as _

# 添加一个数据
@bp.route('/updata', methods=['POST'])
@token_auth.login_required
def add_data_info():
    results = request.get_json()
    if not results:
        return bad_request(_('You must post JSON data.'))
    if results['header'][0] != 'ID':
        return bad_request(_('You must upload file including ID on col1.'))
    for each in results['data']:
        ### 先获取ID,没有ID一组数将被忽略掉
        try:
            rsid = each['ID'].replace(" ","")
        except:
            continue
        ### 每个样本信息，从一组数的第二个
        for item in results['header'][1:]:
            ### 处理基因型 去掉空白，正反匹配都OK
            gt = each[item].replace(" ","") ## 替换空白
            comvars = ComVar.query.filter(ComVar.rs == rsid).all()
             ### 获取这个样本数据
            updata = UpData.query.filter(UpData.sample_id == item.replace(' ','')).first()
            comvar = None
            ## 有rs则变量，则遍历基因型，找到基因行一致的则返回。如果基因型不一致，且存在与这个样本有关联的rs，则删除。
            if comvars:
                for comvar_i in comvars:
                    if updata in comvar_i.datacode:
                        comvar_i.datacode.remove(updata)
                        db.session.commit()
                    if len(set(comvar_i.gt) -  set(gt)) == 0  and len(set(gt) -  set(comvar_i.gt)) == 0:
                        comvar = comvar_i
                            
            ### 没有则新存,

            if not comvar:
                comvar = ComVar()
                comvar.rs = rsid
                comvar.gt = each[item]
            
            if not updata:
                updata = UpData()
                updata.sample_id = item.replace(' ','')
                updata.owner = g.current_user
                
                updata.creation_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                updata.data_num = 'DRUG' + get_order_code()

            ### 更新时间 更新基因型
            updata.sample_id = item.replace(' ','')
            updata.update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            ### 增加关系
            comvar.datacode.append(updata)

            ### 保存
            db.session.add(comvar)
            db.session.add(updata)
            db.session.commit()

    for item in results['header'][1:]:
        updata = UpData.query.filter(UpData.sample_id == item.replace(' ','')).first()
        updata.rs_num = len(updata.gtinfo.all())
        db.session.add(updata)
        db.session.commit()
    return jsonify({'code': 200, 'msg': "添加成功"})


# 列数据页面
@bp.route('/updata', methods=['GET'])
@token_auth.login_required
def get_updata():
    def search(updatas):
        if sample_code:
            updatas = [i for i in updatas if re.search(r'%s'%(sample_code), i.sample_id)]
        if data_num:
            updatas = [i for i in updatas if re.search(r'%s'%(data_num), i.data_num)]        
        return updatas

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    sample_code = request.args.get('sample_code',type=str, default=None)
    data_num = request.args.get('data_num',type=str, default=None)

    data = UpData.to_collection_dict(
            UpData.query.order_by(UpData.update_time.desc()), \
                                page, page_size)

    return jsonify({'code': 200, 'infos': data})
    


# 删除一个订单
@bp.route('/updata/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_updata(id):
    '''删除一个数据'''
    updata = UpData.query.get_or_404(id)
    updata.gtinfo = []
    db.session.delete(updata)
    db.session.commit()
    return jsonify({'code': 200, 'msg': "删除成功"})
