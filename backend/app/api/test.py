# -*- coding: utf-8 -*-
import os,re,json
from flask import Flask, g, jsonify, make_response, request, render_template,current_app

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import shutil
from app.utils.tasks import add_together

from . import bp


executor = ThreadPoolExecutor(1)

#from app.views.auth_verify import auth

@bp.route('/test_celery')
#@auth.login_required
def test_celery():
    print('================ get test2 begin ================')
    result =add_together.delay(23,23)

    print(current_app)
    with current_app.app_context():
        print('22222222222')
    print('================ get test2 end  ================')
    return 'this test2  is the backend !! ,the id is :\n'+str(result.id)+'\n'

#@bp.route('/status/<task_id>')
@bp.route('/test_celery/<task_id>')
#@auth.login_required
def test_celery1(task_id):
    print('================ get test2 begin ================')
    #add_together.delay(23,23)

    task = add_together.AsyncResult(task_id)
    print(task.state)
    print(task.info)
    print(task.backend)
    #print(task.info.get('current',0))
    #print(task.info.get('total',1))
    print('================ get test2 end  ================')
    return 'task.state\n'#+str(result)

@bp.route('/report/<task_id>')
#@auth.login_required
def test_celery2(task_id):
    print('================ get test2 begin ================')
    add_together.delay(23,23)

    task = add_together.AsyncResult(task_id)
    print(task.state)
    print(task.info)
    print(task.info.get('current',0))
    print(task.info.get('total',1))
    print('================ get test2 end  ================')
    return 'task.state'#+str(result)

