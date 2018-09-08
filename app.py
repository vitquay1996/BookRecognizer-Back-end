from flask import Flask, request, Response
import os
import jsonpickle

UPLOAD_FOLDER = './images'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def hello():
    return "Hello World!"

# route http posts to this method
@app.route('/upload', methods=['POST'])
def upload():
    r = request
    print(r.files)
    if ('file' not in r.files):
        return "No file"
    file = request.files['file']
    filename = file.filename
    print(filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], "default.jpeg"))
    # convert string of image data to uint8
    # nparr = np.fromstring(r.data, np.uint8)
    # decode image
    # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    response = {'message': 'image received',
                'books': ['0439136369','0439785960','0439064872','0439064872']
                }
                
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")