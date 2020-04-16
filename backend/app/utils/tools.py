import time
import random
import os
import json
import sys
import logging
import datetime
import string
import random
logger = logging.getLogger('rpt')

def get_order_code(serial_no=None):
    if serial_no:
        order_no = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time()))) \
            + str(random.randint(10, 99)) + str("%04d"%(serial_no)) + str(random.randint(10, 99))
    else:
        order_no = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time()))) + str(random.randint(1000, 9999))
    return order_no

class SaveWebJson(object):
    def __init__(self, source, path, sample_id, extra_results=None):
        print('trans json for web!')
        self.sample_id = sample_id
        self._path = path + '/WebJson'
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        newdic_web = {}
        newdic_web.setdefault('DrugsItems', []).append(source)

        if extra_results:
            newdic_web.update(extra_results)
        self.json_path = self.to_json(newdic_web)
        print('json saved in %s!'%(self.json_path))

    def to_json(self, out_dic):
        json_path = self._path + '/' + self.sample_id + '.json'
        with open(json_path, 'w') as fh:
            json.dump(out_dic, fh, ensure_ascii=False, indent=2, separators=(',', ':'))
        return json_path

class FilePath(object):

    __slots__ = ['_pwd']

    def __init__(self):
        #self._pwd = os.path.abspath(sys.path[0])
        abspathpy = os.path.abspath(__file__)
        absdir = '/'.join((abspathpy.split('/')[:-4]))
        self._pwd = absdir
        logger.info('Basedir for FilePath: {}'.format(self._pwd))

    def random_string(self):
        chars = string.ascii_letters + string.digits
        random_str = ''.join(random.choice(chars) for _ in range(10))
        return random_str

    def get_common_report_path(self):
        '''
        默认报告输出目录。
        :return: 报告输出目录。
        '''
        dir = os.path.join(self._pwd, 'backend/project_data/results')
        if not os.path.exists(dir):
            os.mkdir(dir)
            if not os.path.exists(dir):
                logger.error('Fail to create path: {}'.format(dir))
        file_name = self.random_string()
        name = '.'.join([file_name, 'docx'])
        path = os.path.join(dir, name)
        return path


    def get_report_path(self):
        '''
        临时报告路径。
        :return: 报告路径。
        '''
        dir = os.path.join(self._pwd, 'backend/project_data/results')
        if not os.path.exists(dir):
            os.mkdir(dir)
            if not os.path.exists(dir):
                logger.error('Fail to create path: {}'.format(dir))
        file_name = self.random_string()
        name = '.'.join([file_name, 'docx'])
        path = os.path.join(dir, name)
        logger.info('Report path: {}'.format(path))
        return path

    def get_report_pdf_path(self, docx_path):
        if not isinstance(docx_path, str):
            docx_path = str(docx_path)
        path = docx_path.replace('docx', 'pdf')
        logger.info('PDF Report path: {}'.format(path))
        return path


    def get_word2pdf_java_path(self):
        path = os.path.join(self._pwd, 'backend/app/rpt/bin/word2pdf_index.jar')
        if not os.path.isfile(path):
            logger.warning('File not exist: {}'.format(path))
        logger.info('Java script which convert MS-word to pdf and update TOC path:\n{}'.format(path))
        return path
