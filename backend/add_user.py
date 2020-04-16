#!/usr/bin/env python

import sys
from app.extensions  import *
from app.models import *
from app import create_app  
from app.models1 import *

username = sys.argv[1]
pawd = sys.argv[2]
role = sys.argv[3]
channel = sys.argv[4]
app = create_app()

with app.app_context():
    U = User()
    U.username = username
    U.email = '37150280@qq.com'
    U.set_password(pawd)
    role = Role.query.filter_by(name=role).first()
    channel = Channel.query.filter_by(name=channel).first()
    U.role = role
    U.channel = channel
    db.session.add(U)
    db.session.commit()
