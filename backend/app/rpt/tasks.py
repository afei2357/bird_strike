import json
import os
import time
from datetime import datetime
# import celery 
from app.extensions import db
from app.rpt.reporter  import RunInfo
from app.models1 import OrderMed


# @celery.task(bind=True)
# def generate_report(self,id):
def generate_report(id):
    from app import create_app
    app = create_app()
    with app.app_context():
        # self.update_state(state='RUNNING')
        order = OrderMed.query.get_or_404(id)
        client_snp = {i.rs:i.gt for i in order.updata.gtinfo.all()}
        client_info = (order.to_dict())
        client_info['report_date'] = datetime.now().strftime("%Y-%m-%d") # order.report_date时间不能放在前面，不然会打乱状态控制
        outdir = "project_data/results/%s/%s"%('REO', datetime.now().strftime("%Y%m%d"))
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        ins = RunInfo(client_info, client_snp, outdir)
        order.report_date = datetime.now()
        order.docx_path = ins.docx_path
        order.pdf_path = ins.pdf_path
        db.session.commit()

# @celery.task(bind=True)
def add_together(self,x,y):
    #time.sleep(10) 
    for i in range(10):
        time.sleep(1)
        #self.update_state(state='RUNNING')
        self.update_state(state=f'-----------{i}')
    result = x+y
    print(result)
    return result
