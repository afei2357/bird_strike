from flask_script import Manager
from flask_script.commands import ShowUrls
from app import create_app,db
from app.models import User


app = create_app()
manager = Manager(app)
manager.add_command("showurls",ShowUrls())


@manager.shell
def make_shell_context():
    return dict(app=app,db=db,User=User)
# 使用方法：
# python  run_shell.py shell
if __name__ == '__main__':
    manager.run()

