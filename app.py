from flask import Flask, request, Response
import os
import jsonpickle
import helper
from crop_objects import *
from predict2 import *
import h5py
import selenium
from tflearn.data_utils import build_hdf5_image_dataset
from PIL import Image
from predict_user_nn import *
UPLOAD_FOLDER = './images'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = {
	'0471370460': [7,3,4,6,3,5,1,9,1,9,6],
	'1841493147': [8,7,6,4,7,3,6,5,3,2,1],
	'Vo cung tan nhan vo cung yeu thuong': [5,6,4,6,4,2,4,6,7,9,2],
	'9780273791751': [1,2,3,4,5,5,1,9,7,8,4],
	'817224925X': [5,6,3,5,6,7,3,7,3,7,2],
	'How to make winning presentation': [6,2,5,6,7,5,2,9,6,8,9],
	'9780615345635': [9,9,7,4,2,4,5,6,5,3,2],
	'The dog really did that?': [7,8,5,2,5,6,7,8,9,1,2],
	'9780140280197': [7,8,6,6,3,5,1,2,3,4,1]
}

@app.route("/")
def hello():
	return "Hello World!"

# route http posts to this method
@app.route('/upload_ggimage', methods=['POST'])
def upload_ggimage():
	r = request
	print(r.files)
	if ('file' not in r.files):
		return "No file"
	file = request.files['file']
	filename = file.filename
	print(filename)
	save_path = os.path.join(app.config['UPLOAD_FOLDER'], "default.jpeg")
	file.save(save_path)
	
	# open an image file (.bmp,.jpg,.png,.gif)
	# change image filename to something you have in the working folder
	im1 = Image.open(save_path)
	# rotate 60 degrees counter-clockwise
	im2 = im1.rotate(90)
	# brings up the modified image in a viewer, simply saves the image as
	# a bitmap to a temporary file and calls viewer associated with .bmp
	# make certain you have an image viewer associated with this file type

	# save the rotated image as d.gif to the working folder
	# you can save in several different image formats, try d.jpg or d.png  
	# PIL is pretty powerful stuff and figures it out from the extension
	im2.save(save_path)
	# convert string of image data to uint8
	# nparr = np.fromstring(r.data, np.uint8)
	# decode image
	# img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
	# call function from helper to retrieve isbn
	crop_objects(save_path)
	res = []
	for dirpath,_,filenames in os.walk('./output'):
		for f in filenames:
			image = os.path.join(dirpath, f)
			try:
				isbn_number = helper.get_isbn_from_image(image)
			except selenium.common.exceptions.ElementClickInterceptedException:
				isbn_number = -1
			except selenium.common.exceptions.TimeoutException:
				isbn_number = -1
			finally:
				res.append(isbn_number)
	try:
		isbn_number = helper.get_isbn_from_image(save_path)
	except selenium.common.exceptions.ElementClickInterceptedException:
		isbn_number = -1
	except selenium.common.exceptions.TimeoutException:
		isbn_number = -1
	finally:
		res.append(isbn_number)
	# print("ISBN Number: {}".format(isbn_number))
	"""
	# for debugging
	response = {'message': 'image received',
	'books': ['0439136369','0439785960','0439064872','0439064872']
	}
	"""
	response = {
		'message': 'image received',
		'books': [res],
	}
	response_pickled = jsonpickle.encode(response)
	return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/upload_nn', methods=['POST'])
def upload_nn():
	r = request
	print(r.files)
	if ('file' not in r.files):
		return "No file"
	file = request.files['file']
	filename = file.filename
	print(filename)
	save_path = os.path.join(app.config['UPLOAD_FOLDER'], "default.jpeg")
	file.save(save_path)

	dataset_file = os.path.join(CWD_PATH, 'input.txt')
	output = os.path.join(CWD_PATH, 'input.h5')
	build_hdf5_image_dataset(dataset_file, image_shape=(128, 128), mode='file', output_path=output, categorical_labels=True, normalize=True)
	h5f = h5py.File(output, 'r')
	X = h5f['X'].value
	result = predict(X)
	print(result)
	books_features = []
	for i in result:
		books_features.append(db[i])
	likey = predict_which_book_might_like(books_features)

	data = {
		'message': 'image received',
		'books': result,
		'likey': likey
	}
	response_pickled = jsonpickle.encode(data)
	return Response(response=response_pickled, status=200, mimetype="application/json")
