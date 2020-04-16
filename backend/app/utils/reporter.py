import json
import requests
import os
import re
import datetime as dt
import pysnooper
from app.models1 import Products, Indicates
from app.utils.Drugs import Drugs
from app.utils.tools import SaveWebJson
from RptSer.Scripts.NewHealthIO import NewHealthIO
from RptSer.Scripts.Report.Report import Report
from RptSer.Scripts.WebReport.Report import WebReport
from RptSer.Config.Parser import run_config
from RptSer.Scripts.Input.preExplain import FetchCategory
from RptSer.Scripts.WebReport.Json2Doctpl import Json2Doc
import logging
main_config = run_config()
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

    def product_info(self, product_name):
        """
        从线上获取产品数据
        """
        product_indicate_info = {}
        print(product_name)
        product_dict_info = json.loads(requests.get(main_config['remote_api']['product2indicate'], \
                                       params={'product_name': product_name}).json()) #远程API中提取产品和z
        product_dict_info['front_end_json'] = json.loads(product_dict_info['front_end_json']) #进一步解码json
        #得到指标列表
        for item in product_dict_info['front_end_json']:
            o_indicate_set = []
            for subitem in item['children']:
                for indicate in subitem['detail'].split(','):
                    o_indicate_set.append(indicate)
            product_indicate_info.setdefault(item['event'], set(o_indicate_set))
        return product_indicate_info


    def module1(self, product_indicate_info, product_name, client_info, sample_id):
        """
        通用型模板
        """
        logger.info('Get product_rsgt')
        product_rsgt = self.get_rs_gt(product_name) #客户snp
        ins = NewHealthIO(client_info, product_rsgt, self.output_path, {product_name : product_indicate_info})
        out_doc = self.output_path + '/' + sample_id + '.docx'
        rp_ins = Report(ins.result_json, out_doc)
        logger.info('Finished Job')
        
        #extra_result = {}
        #extra_result.setdefault('SampleInfo',client_info)
        #将结果进行转换，转换为特定项目需要的json文件
        #WebReport(ins.result_json, self.output_path, extra_result)

        self.docx_path = rp_ins.report_path
        self.pdf_path = rp_ins.pdf_path

    def mut_category(self, category_dict):
        total_mut = 0
        total_B = 0
        total_P = 0
        total_VUS = 0
        mutdis = {}
        for gene in category_dict:
            mutdis.setdefault(gene, category_dict[gene]['Total'])
            total_mut = total_mut + category_dict[gene]['Total']
            total_P = total_P + category_dict[gene]['P']
            total_B = total_B + category_dict[gene]['B']
            total_VUS = total_VUS + category_dict[gene]['VUS']
        category = {}
        category.setdefault('TotalVusMutCount', total_VUS)
        category.setdefault('TotalLBAndBMutCount', total_B)
        category.setdefault('TotalP', total_P)
        category.setdefault('TotalMutCount', total_mut)
        category.setdefault('MutDis', mutdis)
        return category

    def module2(self, product_indicate_info, product_name, client_info, sample_id, tempalte, extra_data = ''):
        """
        适用于NGS数据
        """
        ins_info = FetchCategory(self.data_path, self.output_path)
        client_snp = ins_info.med_dict[sample_id] #药物及风险位点
        client_category = self.mut_category(ins_info.category_dict[sample_id]) #变异数据分类统计
        
        #增加额外的信息，称谓及日期
        client_info.setdefault('chengwei', '先生') if (client_info['gender']) == '男' else client_info.setdefault('chengwei', '女士')
        report_date_split = re.search(r'(\d{4})-(\d{2})-(\d{2})', str(client_info['report_date'])).groups()[0:3]
        client_info['rpt_y'] = report_date_split[0]
        client_info['rpt_m'] = report_date_split[1].lstrip('0')
        client_info['rpt_d'] = report_date_split[2]
        client_info['birthday']

        extra_result = {}
        if extra_data:
            with open (extra_data, 'r') as fi:
                 extra_result.setdefault('SampleInfo', json.load(fi))
        #替换到一些关键信息
        for k in extra_result['SampleInfo']:
            if extra_result['SampleInfo'][k] == 'unknown': extra_result['SampleInfo'][k] = '未知'
            if extra_result['SampleInfo'][k] == False: extra_result['SampleInfo'][k] = '否'
            if extra_result['SampleInfo'][k] == 'no': extra_result['SampleInfo'][k] = '否'
            if extra_result['SampleInfo'][k] == 'yes': extra_result['SampleInfo'][k] = '是'

        #extra_result.setdefault('SampleInfo', client_info) #添加客户信息,原200项流程把客户信息放在外层，额外信息中再放入一层SampleInfo中
        extra_result['SampleInfo'].update(client_info)
        extra_result.setdefault('MendelItems', client_category) #变异分类信息，遗传
        ins_results = NewHealthIO(client_info, client_snp, \
                                  self.output_path, \
                                  {product_name : product_indicate_info}, extra_result)
        #将结果进行转换，转换为特定项目需要的json文件
        rp_ins = WebReport(ins_results.result_json, self.output_path, extra_result)
        #Json转为包括
        out_doc = self.output_path + '/' + sample_id + '.docx'
        rp_ins = Json2Doc(rp_ins.json_path, out_doc, main_config['Tpl'][tempalte])
        self.docx_path = rp_ins.report_path
        self.pdf_path = rp_ins.pdf_path

    def module3(self, product_indicate_info, product_name, client_info, sample_id, tempalte, cover=False):
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
        rp_ins = Json2Doc(rp_ins.json_path, out_doc, main_config['Tpl'][tempalte], cover=cover)
        self.docx_path = rp_ins.report_path
        self.pdf_path = rp_ins.pdf_path       

    @pysnooper.snoop()
    def run(self):
        client_info = self.get_classify_info(self.results_info, 'client_info') #客户信息
        client_info['detection_items'] = client_info['detection_items'].split('@')[0]
        #order_info = self.get_classify_info(self.results_info, 'order_info') #订单信息
        products_info = self.get_classify_info(self.results_info, 'products_info') #产品信息
        client_info['template_info'] = self.get_classify_info(self.results_info, 'template_info') #模板信息        
        sample_code = client_info.get('sample_code')
        self.output_path = self.output_path + '/%s'%(sample_code)

        product_name = products_info['detection_items']
        template = client_info['template_info']['template']
        product_indicate_info = self.product_info(product_name) #产品对应指标信息
        logger.info('Get product_indicate_info')
        if template in ['s1']:
            self.module2(product_indicate_info, product_name, client_info, sample_code, template, self.results_info['extra_path'])
        elif template in ['d1', 'd2']:
            self.module3(product_indicate_info, product_name, client_info, sample_code, template)
        elif template in ['h1']:
            self.module3(product_indicate_info, product_name, client_info, sample_code, template, cover=True)
        else:
            self.module1(product_indicate_info, product_name, client_info, client_info['sample_code'])
        

