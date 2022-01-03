import flask as F
import flask_cors as F_C
import os
import opengeode as O_G  # Importe le package OpenGeode
import base64 as B64
import GeodeObjects as G_O
import threading as T

app = F.Flask(__name__)
F_C.CORS(app,
         origins="https://test.geode-solutions.com")
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CORS_HEADERS'] = 'Content-Type'
# app.config['APPLICATION_ROOT'] = ID
isAlive = False

ID = os.environ['ID']


def update_or_kill(update):
    global isAlive
    print("T", T.get_ident())
    if update:
        isAlive = True
    else:
        if not isAlive:
            os._exit(0)
        else:
            print("isAlive", isAlive, flush=True)
            isAlive = False
            print("isAlive", isAlive, flush=True)


def set_interval(func, args, sec):
    def func_wrapper():
        set_interval(func, args, sec)
        func(args)
    t = T.Timer(sec, func_wrapper)
    t.start()
    return t


@app.route('/' + ID + '/', methods=['GET'])
def test():
    return "Coucou"


@app.route('/' + ID + '/start', methods=['POST'])
def start():
    print("ID : ", ID)
    print(isAlive)
    set_interval(update_or_kill, False, 40)
    print(isAlive)
    return {"status": 200}


@app.route('/ping', methods=['GET'])  # , methods=['POST']
def Revive():
    response = F.jsonify(message="Simple server is running")

    update_or_kill(True)
    # print(isAlive)
    # return {"status": 200}
    # return response
    # response = F.jsonify({'some': 'data'})
    return response


@app.route('/allowedfiles', methods=['GET'])
def AllowedFiles():
    ObjectsList = G_O.ObjectsList()
    response = F.jsonify({"extensions": ListExtensions(ObjectsList)})
    return response


@app.route('/allowedObjects', methods=['GET', 'OPTIONS'])
@F_C.cross_origin(supports_credentials=True)
def AllowedObjects():
    FileName = F.request.form['fileName']
    (_, file_extension) = os.path.splitext(FileName)
    ObjectsList = G_O.ObjectsList()
    return {"objects": ListObjects(ObjectsList, file_extension[1:])}


@app.route('/readfile', methods=['GET'])
@F_C.cross_origin(supports_credentials=True)
def UploadFile():
    File = F.request.form['file']
    if File:
        FileDecoded = B64.b64decode(File.split(',')[1])
        filename = os.path.join(
            app.config['UPLOAD_FOLDER'], F.request.form['filename'])
        f = open(filename, "wb")
        f.write(FileDecoded)  # Writes in the file
        f.close()  # Closes

        model = O_G.load_brep(filename)
        # model = getattr(O_G, "load_brep")(filename)
        return {"status": 200, "nb surfaces": model.nb_surfaces(), "name": model.name()}
    else:
        return {"status": 500}


def ListObjects(ObjectsList, Extension):
    """
    Purpose:
        Function that returns a list of objects that can handle the file, given his extension
    Args:
        Extension -- The exention of the file
        ObjectsList -- A list of objects with their InputFactory/OutputFactory/Name
    Returns:
        An ordered list of object's names
    """
    List = []  # Initializes an empty list
    for type, values in ObjectsList.items():  # Loops through objects
        # If object can handle this extension
        if values['input'].has_creator(Extension):
            if type not in List:  # If object's name isn't already in the list
                List.append(type)  # Adds the object's name to the list
    return List  # Returns the final list


def ListExtensions(ObjectsList):
    """
    Purpose:
        Function that returns a list of extensions that can handled by the objects given in parameter
    Args:
        ObjectsList -- A list of objects with their InputFactory/OutputFactory/Name
    Returns:
        An ordered list of file extensions
    """
    List = []  # Initializes an empty list
    for values in ObjectsList.values():  # Loops through objects
        # List of extensions this object can handle
        Creators = values['input'].list_creators()
        for Creator in Creators:  # Loop through
            if Creator not in List:  # If object's name isn't already in the list
                List.append(Creator)  # Adds the object's name to the list
    return List  # Returns the final list


if __name__ == '__main__':
    if not os.path.exists("./uploads"):
        os.mkdir("./uploads")

    # set_interval(update_or_kill, False, 30)

    app.run(debug=True, host='0.0.0.0', port=5000,
            threaded=False, ssl_context='adhoc')  # , ssl_context='adhoc'
