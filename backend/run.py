#from app import create_app
from app  import create_app,db,celery
app = create_app()
app.debug = True

if __name__ == '__main__':
    #print(app.config)
    db.create_all(app=app)
    app.run(host='127.0.0.1', port=6000, debug=True)
    #app.run(host='0.0.0.0',port=6000, debug=True)
