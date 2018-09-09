from __future__ import division, print_function, absolute_import

import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.normalization import local_response_normalization
from tflearn.layers.estimator import regression
import numpy as np
import json
import h5py
import os
CWD_PATH = os.getcwd()
from tflearn.data_utils import build_hdf5_image_dataset

network = tflearn.input_data(shape=[None, 128, 128, 3])
network = tflearn.batch_normalization(network)
network = conv_2d(network, 32, 3, activation='linear')
network = max_pool_2d(network, 2)
network = conv_2d(network, 64, 3, activation='linear')
network = conv_2d(network, 64, 3, activation='linear')
network = max_pool_2d(network, 2)
network = fully_connected(network, 512, activation='linear')
network = dropout(network, 0.7)
network = tflearn.batch_normalization(network)
network = fully_connected(network, 9, activation='sigmoid')
optimizer = tflearn.Momentum(0.005)
network = regression(network, optimizer=optimizer,
                     loss='binary_crossentropy')

model = tflearn.DNN(network, tensorboard_verbose=0,
                    clip_gradients=0.)

model.load('./single_prediction_3.tfl')


def encode(data):
    class MyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return super(MyEncoder, self).default(obj)

    return json.dumps(data, cls=MyEncoder)

def map_index_to_books(z):
	
	if z == 0:
		# return 'The probabilistic method'
		return '0471370460'
	if z == 1:
		# return 'The Novice (Summoner)'
		return '1841493147'
	if z == 2:
		return 'Vo cung tan nhan vo cung yeu thuong'
	if z == 3:
		# return '130693947X'
		return '9780273791751'
	if z == 4:
		return '817224925X'
	if z == 5:
		return 'How to make winning presentation'
	if z == 6:
		return '9780615345635'
	if z == 7:
		return 'The dog really did that?'
	if z == 8:
		return '9780140280197'
	return '?'

def top_3(arr):
	res = arr.tolist()
	print(res)
	res.sort(reverse=True)
	res = res[:3]
	idx = []
	for i in res:
		idx.append(arr.tolist().index(i))
	return idx


def predict(X):
	y = model.predict(X)
	y = np.squeeze(y, axis=0)
	# result = []
	# for i in range(len(y)):
	# 	if y[i] > 0.9:
	# 		result.append(map_index_to_books(i))
	# if len(result) == 0:
	result = [map_index_to_books(i) for i in top_3(y)]
		
	return result
# dataset_file = os.path.join(CWD_PATH, 'input_image.txt')
# output = os.path.join(CWD_PATH, 'input_image.h5')
# build_hdf5_image_dataset(dataset_file, image_shape=(128, 128), mode='file', output_path=output, categorical_labels=True, normalize=True)
# h5f = h5py.File(output, 'r')
# X = h5f['X'].value
# result = predict(X)
# print(result)

