import flask
import flask_cors
import os
import functions
import GeodeObjects
import InspectorFunctions
import werkzeug

validitychecker_routes = flask.Blueprint('validitychecker_routes', __name__)
flask_cors.CORS(validitychecker_routes)

@validitychecker_routes.before_request
def before_request():
    functions.create_lock_file()

@validitychecker_routes.teardown_request
def teardown_request(exception):
    functions.remove_lock_file()

@validitychecker_routes.route('/versions', methods=['GET'])
def validitychecker_versions():
    list_packages = ['OpenGeode-core', 'OpenGeode-IO', 'OpenGeode-Geosciences', 'OpenGeode-GeosciencesIO', 'OpenGeode-Inspector']
    return flask.make_response({"versions": functions.GetVersions(list_packages)}, 200)

@validitychecker_routes.route('/allowedfiles', methods=['GET'])
def vaditychecker_allowedfiles():
    extensions = functions.ListAllInputExtensions()
    return {"status": 200, "extensions": extensions}

@validitychecker_routes.route('/allowedobjects', methods=['POST'])
def validitychecker_allowedobjects():
    filename = flask.request.form.get('filename')
    if filename is None:
        return flask.make_response({"error_message": "No file sent"}, 400)
    file_extension = os.path.splitext(filename)[1][1:]
    objects = functions.ListObjects(file_extension)
    return flask.make_response({"objects": objects}, 200)

@validitychecker_routes.route('/uploadfile', methods=['POST'])
def vaditychecker_uploadfile():
    try:
        UPLOAD_FOLDER = flask.current_app.config['UPLOAD_FOLDER']
        file = flask.request.form.get('file')
        filename = flask.request.form.get('filename')
        filesize = flask.request.form.get('filesize')
        if file is None:
            return flask.make_response({"error_message": "No file sent"}, 400)
        if filename is None:
            return flask.make_response({"error_message": "No filename sent"}, 400)
        if filesize is None:
            return flask.make_response({"error_message": "No filesize sent"}, 400)
          
        uploadedFile = functions.UploadFile(file, filename, UPLOAD_FOLDER, filesize)
        if not uploadedFile:
            flask.make_response({"error_message": "File not uploaded"}, 500)
            
        return flask.make_response({"message": "File uploaded"}, 200)
    except Exception as e:
        print("error : ", str(e))
        return flask.make_response({"error_message": str(e)}, 500)

@validitychecker_routes.route('/testsnames', methods=['POST'])
def vaditychecker_testnames():
    try:
        object = flask.request.form.get('object')
        if object is None:
            return flask.make_response({"error_message": "No object sent"}, 400)
        modelChecks = InspectorFunctions.json_return(InspectorFunctions.Inspectors()[object]['testsnames'])
        return flask.make_response({"modelChecks": modelChecks}, 200)

    except Exception as e:
        print("error : ", str(e))
        return flask.make_response({"error_message": str(e)}, 500)

@validitychecker_routes.route('/inspectfile', methods=['POST'])
def vaditychecker_inspectfile():
    try:
        UPLOAD_FOLDER = flask.current_app.config['UPLOAD_FOLDER']
        object = flask.request.form.get('object')
        filename = flask.request.form.get('filename')
        test = flask.request.form.get('test')

        if object is None:
            return flask.make_response({"error_message": "No object sent"}, 400)
        if filename is None:
            return flask.make_response({"error_message": "No filename sent"}, 400)
        if test is None:
            return flask.make_response({"error_message": "No test sent"}, 400)
        
        secureFilename = werkzeug.utils.secure_filename(filename)
        filePath = os.path.join(UPLOAD_FOLDER, secureFilename)
        model = model = GeodeObjects.ObjectsList()[object]['load'](filePath)
        if 'model' in flask.session:
            model = flask.session['model']
        inspector = InspectorFunctions.Inspectors()[object]['inspector'](model)
        testResult = getattr(inspector, test)()
        expectedValue = InspectorFunctions.InpectorExpectedResults()[test]

        if testResult != expectedValue or type(testResult) != type(expectedValue):
            print(test, ' : ', testResult)
            if type(testResult) is dict:
                for key in testResult:
                    new_key = key.string()
                    testResult[new_key] = testResult.pop(key)

        result = testResult == expectedValue and type(testResult) == type(expectedValue)

        return flask.make_response({"Result": result, "list_invalidities": str(testResult)}, 200)

    except Exception as e:
        print("error : ", str(e))
        return flask.make_response({"error_message": str(e)}, 500)
