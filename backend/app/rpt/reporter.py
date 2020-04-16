import json
import requests
import os
import re
import datetime as dt
import pysnooper
from app.models1 import Products, Indicates
from app.rpt.Drugs import Drugs
from app.utils.tools import SaveWebJson

from app.rpt.Json2Doctpl import Json2Doc
import logging
logger = logging.getLogger('Rpt')

class RunInfo(object):
    def __init__(self, info_dict, client_snp, results_folder):
        #self.client_path = client_path #客户信息,json格式
        self.results_info = info_dict
        self.client_snp = client_snp
        self.output_path = results_folder # 项目数据路径
        self.docx_path = ''
        self.pdf_path = ''
        self.run()

    def get_classify_info(self, results_info, classify):
        """
        @results_info: 从omics传过来的订单信息
        @classify: 信息分类，客户、订单等等
        处理订单信息，将提取客户，订单及产品信息。针对fgdp，还需要提取基因型信息？(暂未做)
        """
        new_results = {}
        items = []
        if classify == 'client_info':
            #results_info['gender'] =u'男' if str(results_info['gender']) == '1' else  u'女'
            
            #items = ['user_id', 'gender', 'name', 'weight', 'sample_no', \
            #'phone', 'birth', 'waistline', 'nation', 'height', 'product', 'sampled_at', 'ReceiveDate', 'ReportDate']
            '''age count'''            
            try:
                yb = dt.datetime.strptime(results_info['birthday'],'%Y-%m-%d').year
                yc = dt.datetime.today().year
                results_info['age'] = yc - yb
            except:
                results_info['age'] = None
            #results_info['report_date'] = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d")
            items = ['id', 'gender', 'name', 'sample_code', 'phone', 'birthday', 'age', \
                     'sample_date', 'report_date', 'receive_date', 'detection_items', 'channel_name', 'template','hospital', 'department','doctor', 'clinical_bg']
        elif classify == 'order_info':
            items = ['order_no','order_id']
        elif classify == 'products_info':
            items = ['detection_items','template']
        elif classify == 'template_info':
            items = ['template','end_cover','front_cover','color']
        else:
            logger.fatal('Not support input type: {}'.format(classify))
        for item in items:
            try:
                new_results.setdefault(item, results_info[item])
            except:
                pass

        return new_results


    def get_rs_gt(self, product_name):
        """
        获取产品rs信息，及对应的基因型信息
        get rs and gt from ASA array 
        @indicate_lst: indicate list
        """
        product_rs_info = requests.get(main_config['remote_api']['product2rs'], params={'product_name': product_name}).json()
        #product_rs_info = requests.get(main_config['remote_api']['product2rs'], params={'product_name': product_name}).json()
        rs_list = product_rs_info['rs_list']
        product_rsgt = {}
        not_in_db = []
        for i in rs_list:
            try:
                i = i.replace(" ", "")
                product_rsgt.setdefault(i, self.client_snp[i])
            except:
                not_in_db.append(i)
        if len(not_in_db) >1:
            print (not_in_db)
        return product_rsgt


    def module3(self, product_name, client_info, sample_id, tempalte, cover=False):
        extra_result = {}
        extra_result.setdefault('SampleInfo',client_info)
        out_doc = self.output_path + '/' + sample_id + '.docx'
        
        products = Products.query.filter(Products.product_name.startswith(product_name)).first()
        if len (products.indicatesinfo.all()) >0:
            results = {}
            for indicate in products.indicatesinfo.all():
                ins = Drugs(indicate.name, self.client_snp)
                results.setdefault('sub',[]).append(ins.results)
            rp_ins = SaveWebJson(results, self.output_path, sample_id, extra_result)
        else:
            product_rsgt = self.get_rs_gt(product_name) #客户snp
            ins_results = NewHealthIO(client_info, product_rsgt, self.output_path, {product_name : product_indicate_info})
            #将结果进行转换，转换为特定项目需要的json文件
            rp_ins = WebReport(ins_results.result_json, self.output_path, extra_result)
        #Json转为word
        rp_ins = Json2Doc(rp_ins.json_path, out_doc, 'app/rpt/config/clinical_drug.docx', cover=cover)
        self.docx_path = rp_ins.report_path
        self.pdf_path = rp_ins.pdf_path 

    @pysnooper.snoop()
    def run(self):
        client_info = self.get_classify_info(self.results_info, 'client_info') #客户信息
        client_info['detection_items'] = client_info['detection_items'].split('@')[0]
        products_info = self.get_classify_info(self.results_info, 'products_info') #产品信息
        client_info['template_info'] = self.get_classify_info(self.results_info, 'template_info') #模板信息        
        sample_code = client_info.get('sample_code')
        self.output_path = self.output_path + '/%s'%(sample_code)

        product_name = products_info['detection_items']
        template = client_info['template_info']['template']
        if template in ['d1', 'd2']:
            self.module3(product_name, client_info, sample_code, template)
        
