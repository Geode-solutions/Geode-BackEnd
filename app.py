''' Packages '''
import flask
import flask_cors
import os
from blueprint import routes

''' Global config '''
app = flask.Flask(__name__)

''' Config variables '''
FLASK_ENV = os.environ['FLASK_ENV']
print('Python is running in ' + FLASK_ENV + ' mode')

if FLASK_ENV == "production":
    app.config.from_object('config.ProdConfig')

if FLASK_ENV == "test":
    app.config.from_object('config.TestConfig')

elif FLASK_ENV == "development":
    app.config.from_object('config.DevConfig')

ID = app.config.get('ID')
PORT = int(app.config.get('PORT'))
CORS_HEADERS = app.config.get('CORS_HEADERS')
UPLOAD_FOLDER = app.config.get('UPLOAD_FOLDER')
DEBUG = app.config.get('DEBUG')
TESTING = app.config.get('TESTING')
ORIGINS = app.config.get('ORIGINS')

if ID != None:
    app.register_blueprint(routes, url_prefix="/" + ID)
else:
    app.register_blueprint(routes, url_prefix="/")

flask_cors.CORS(app, origins=ORIGINS)

''' Main '''
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT,
            threaded=False, ssl_context='adhoc')
