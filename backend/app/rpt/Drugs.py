import json
import re
import requests
from app.models1 import Indicates

class Drugs(object):
    def __init__(self, indicate_name, client_snp):
        self.client_snp = client_snp
        self.indicate_name = indicate_name
        self.results = self.drug_get_results(self.indicate_name, self.client_snp)

    def split_job(self, indicate_info, clinet_SNP):
            """
            module_dict:{ 2:{ATM:[{siteinfo1},{siteinfo2}}}
            """
            conclusions = {}
            module_dict = {}
            gene_results = []
            advices = []
            level = 0
            conclusion = ''
            for siteinfo in indicate_info['site_result']:
                try:
                    module_dict.setdefault(siteinfo['interpretation_label'], {}).\
                    setdefault(siteinfo['gene'], []).append(siteinfo)
                except:
                    pass
            for module in module_dict:
                if int(module) == 2:
                    ins = DrugModule2(drug_id=indicate_info['indicate_name'], client_SNP=clinet_SNP, sites_dict=module_dict[module])
                elif int(module) == 1:
                    ins = DrugModule1(drug_id=indicate_info['indicate_name'], client_SNP=clinet_SNP, sites_dict=module_dict[module], conclusion_result=indicate_info['conclusion_result'])

                if ins.level > level:
                    conclusion = ins.conclusion
                    level = ins.level
                    conclusions = {}
                    conclusions[conclusion] = ins.level

                gene_results.extend(ins.gene_result)
                advices.extend(ins.advices)
                
            return conclusions, gene_results, advices

    def drug_get_results(self, indicate_name, client_SNP):        
        indicates = Indicates.query.filter_by(name = indicate_name).first()
        if indicates:
            each_info = {}
            indicate_info = indicates.json_info
            indicate_info = json.loads(indicate_info)
            
            try:
                indicate_info['conclusion_result'] = json.loads(indicate_info['conclusion_result'])
            except:
                pass

            indicate_info['site_result'] = json.loads(indicate_info['site_result'])

            conclusions, gene_results, advices = self.split_job(indicate_info, client_SNP)   
            each_info['name'] = indicate_name
            each_info['conclusion'] = list(conclusions.keys())[0]
            each_info['tableData'] = []
            each_info['explanation'] = []
            each_info['medication_advice'] = []

            for each in gene_results:
                table={}
                table['geneName'] = each[0]
                if type(each[1]) == list:
                    table.setdefault('geneSite', each[1])
                else:
                    table.setdefault('geneSite', []).append(each[1])
                table['GT'] = each[2]
                table['explain'] = each[3]
                table['tips'] = each[4]
                each_info['tableData'].append(table)
            
            
            for each in advices:
                tmp = {}
                tmp.setdefault('content',each)
                each_info['medication_advice'].append(tmp)

            each_info['explanation'].append({'content':indicate_info['explanation']})
            
            return each_info
            

class DrugModuleCommon(object):

    def __init__(self, drug_id, client_SNP, sites_dict):
        self.indicate_name = drug_id
        self.client_SNP = client_SNP
        self.sites_dict = sites_dict

        self.advices = []
        self.conclusion = None #
        self.level = None #
        self.gene_result = [] #?????????:?????? ???????????? ????????? ?????? ????????????
        
    def mut_type(self, site, ref, alt, GT):
        """
        'rs_name': 'rs730012', 'ref': 'A', 'alt': 'C,T'
         GT: client SNP : C/C
        """
        def len_base(alt):#??????Alt????????????indel ??????????????????????????????????????????
            len_base = 1
            for base in alt.split(','):
                if len(base) != 1:
                    len_base = len(base)
            return len_base

        mutype = ''
        gt = set(tuple(GT)) # GG ?????????'G'???,AG?????????'A','G'???
        if (len(gt) == 1): #??????
            if len(gt & set(['A', 'T', 'C' ,'G'])) == 1: #SNP??????????????????????????????????????????
                if ref in gt: #???????????????
                    mutype = '?????????'
                elif len(gt & set(alt.split(','))) == 1: #???????????????
                    mutype = '?????????,??????'
                else:
                    print ("Error {} not exists".format(GT))
                    #print (siteinfo)
            elif len(gt & set(['I', 'D'])) == 1: #InDel???I???????????????,D???????????????
                if len(ref) != 1 or len_base(alt) != 1: #???????????????????????????????????????InDel
                    if list(gt)[0] == 'I':
                        mutype = '?????????'
                    elif list(gt)[0] == 'D':
                        mutype = '??????,??????'
                else:
                    print ('Error not exists InDel mutation, ref:{} alt{}'.format(ref, alt))
        elif (len(gt) == 2): #??????
            if len(gt & set(['A', 'T', 'C' , 'G'])) == 2: #SNP?????????????????????????????????????????? 
                if ref in gt or len(gt & set(alt.split(','))) == 1:
                    mutype = '?????????,??????'
                else:
                    print ("Error {} not exits".format(GT))
            elif len(gt & set(['I', 'D'])) == 2: #InDel???I???????????????,D???????????????
                if len(ref) != 1 or len_base(alt) != 1: #???????????????????????????????????????InDel
                    mutype = '??????,??????'
        return mutype
    
    def get_user_muttype(self, siteinfo):
        '''
        get user and ref GT, and return mutype
        '''
        site = siteinfo['rs_name']
        ref = siteinfo['ref'] #????????????
        #alt = siteinfo['alt_db'] #??????alt_db??????
        alt = siteinfo['alt'] #??????????????????????????????','??????
        try:
            GT = self.client_SNP[site].replace('/', '').replace('|', '') #????????????????????????????????????????????????
        except:
            print ("Error {} not exists Genotypes info").format(site)
        return site, GT, self.mut_type(site, ref, alt, GT)


class DrugModule2(DrugModuleCommon):
    """
    Site Depended Results
    """
    def __init__(self, drug_id, client_SNP, sites_dict):
        super(DrugModule2, self).__init__(drug_id, client_SNP, sites_dict)
        self.get_result_model() #function???get genotype info

    def get_result_model(self):
        '''
        Get geneotype and add each SNP result to detail.
        :return: gene_types: Dict with gene, dbSNP and genotype. Example: {'SJDK9': {'rs2898': '???????????????'}}
        '''
        priority_gene_module = 0
        medication_tips_module = ''
        medication_advice_module = ''


        for gene, Gene in self.sites_dict.items():
            priority_gene = 0
            medication_tips_gene = ''
            medication_advice_gene = ''

            #?????????????????????????????????????????????????????????????????????   
            for siteinfo in Gene:
                priority_site = 0 #??????????????????priority???????????????0
                site, GT, mutype = self.get_user_muttype(siteinfo)
                if  mutype == siteinfo['phenotype'].replace('???', ','):
                    #ATM rs11212617 AC ?????????,?????? ????????????
                    self.gene_result.append([gene, siteinfo['rs_name'], GT, siteinfo['phenotype'], siteinfo['medication_tips']])
                    priority_site = int(siteinfo['priority'])
                if  priority_gene < priority_site: #???????????????site???priority????????????site??????
                    priority_gene = priority_site
                    medication_advice_gene = siteinfo['medication_advice']
                    medication_tips_gene = siteinfo['medication_tips']

            self.advices.append(medication_advice_gene)
            if priority_gene_module < priority_gene : #???????????????gene???priority?????????gene??????
                priority_gene_module = priority_gene
                medication_tips_module = medication_tips_gene
                #medication_advice_module = medication_advice_gene

        self.level = priority_gene_module
        self.conclusion = medication_tips_module

        #self.advices.append(medication_advice_module)
        

class DrugModule14(DrugModuleCommon):
    def __init__(self, drug_id, client_SNP, sites_dict):
        super(DrugModule14, self).__init__(drug_id, client_SNP, sites_dict)
    
    def get_pheo_geno(self, gene, genotype):
        '''
        get IM, PM, PM from genotype 
        '''
        ##json_data = requests.get(main_config['remote_api']['genotype_phenotype'], params=param).json()        
        type_dict = json.load(open('app/rpt/config/{}.json'.format(gene), 'r'))

        type_m = type_dict[genotype[0]][genotype[1]]
        return type_m

    def _type2info(self, conclusion_result):
        type2info = {}
        for each in conclusion_result:
            type_m = each['phenotype'].replace(' ', '')
            type2info.setdefault(type_m, {}).setdefault('medication_tips', each['medication_tips'])
            type2info.setdefault(type_m, {}).setdefault('medication_advice', each['medication_advice'])
            type2info.setdefault(type_m, {}).setdefault('priority', each['priority'])
        return type2info

class DrugModule1(DrugModule14):
    def __init__(self, drug_id, client_SNP, sites_dict, conclusion_result):
        super(DrugModule1, self).__init__(drug_id, client_SNP, sites_dict)
        self.__conclusion_result = conclusion_result
        self.get_result_model() #function???get genotype info

    def bubble_sort(self, lst, priority):
        '''
        ??????priority????????????, ???????????????
        '''
        n = len(lst)
        if n <= 1:
            return lst
        for i in range(0, n):
            for j in range(0, n-i-1):
                if priority[lst[j]] < priority[lst[j+1]]:
                    lst[j], lst[j+1] = lst[j+1], lst[j]
        return lst

    def get_result_model(self):
        '''
        Get gene subtypes.
        :return: gene_types: python dict with gene name and subtypes. {gene, subtypes},
        example {'CYP2D6', ('CYP2D6*1', 'CYP2D6*2')}
        '''
        try:
            type_info = self._type2info(self.__conclusion_result) # get infomation for each coclusion type
        except:
            print ('Error: conclusion result something error {}'.format(self.__conclusion_result))

        priority_gene_module = 0
        medication_tips_module = ''
        medication_advice_module = ''
        
        for gene, Gene in self.sites_dict.items():
            priority_gene = 0
            medication_tips_gene = ''
            medication_advice_gene = ''
            priority_type = {} # this is gene type priority, for each type 'CYP2D6*1', 'CYP2D6*2'

            wild_type = gene + '_1' # each genetype, _1 set to wild type
            genotype = [wild_type, wild_type] # 
            priority_type[wild_type] = 0
            sites = []
            
            for siteinfo in Gene:
                site, GT, mutype = self.get_user_muttype(siteinfo)
                sites.append(site)
                priority_type.setdefault(siteinfo['phenotype'],int(siteinfo['priority']))
                if re.search(r'??????', mutype):
                    genotype.append(siteinfo['phenotype'])
                elif re.search(r'??????',mutype):
                    genotype.append(siteinfo['phenotype'])
                    genotype.append(siteinfo['phenotype'])

                genotype = self.bubble_sort(genotype, priority_type)[0:2] #???????????????????????????
            type_m = self.get_pheo_geno(gene, genotype)
            genotype_simple = '*' + genotype[0].split('_')[1] + '/' + '*' + genotype[1].split('_')[1]
            try:
                self.gene_result.append([gene, sites, genotype_simple, type_m, type_info[type_m]['medication_tips']])
            except:
                 self.gene_result.append([gene, sites, genotype_simple, type_m, ""])           
            try:
                priority_gene_module < type_info[type_m]['priority'] #this is medication tips priority
                priority_gene_module = type_info[type_m]['priority']
                medication_tips_module = type_info[type_m]['medication_tips']
                medication_advice_module = type_info[type_m]['medication_advice']
            except:
                pass

        #??????????????????priority???priority??????1,???????????????priority???????????????prority??????????????????
        #??????priority???0????????????priority???????????????????????????????????????(2???)???????????????
        ##????????????????????????????????????????????????
        if priority_gene_module == 0:
            if len(self.gene_result) == 2:
                #

                gene1 = self.gene_result[0][0]
                gene2 = self.gene_result[1][0]
                con1 = self.gene_result[0][3]
                con2 = self.gene_result[1][3]
                genename = gene1 + '_' + gene2 #CYP2D6_CYP2C19
                genotype = [gene1 + '_' + con1, gene2 + '_' + con2] # CYP2D6_IM???CYP2C19_PM
                type_m = self.get_pheo_geno(genename, genotype) # ??????conclusions
                self.gene_result[0][4] = type_info[type_m]['medication_tips']
                self.gene_result[1][4] = type_info[type_m]['medication_tips']
                self.level = 1 #?????????????????????????????????level???0????????????????????????????????????????????????
                self.conclusion = type_info[type_m]['medication_tips']
                self.advices.append(type_info[type_m]['medication_advice'])

        else:
            self.level = priority_gene_module
            self.conclusion = medication_tips_module
            self.advices.append(medication_advice_module)