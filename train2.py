from __future__ import division, print_function, absolute_import

import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.normalization import local_response_normalization
from tflearn.layers.estimator import regression
import numpy as np
import os
from PIL import Image
from tqdm import tqdm
import h5py
import os
h5f = h5py.File('dataset.h5', 'r')
X = h5f['X'].value
CWD_PATH = os.getcwd()

def load_image_into_numpy_array(image):
	im_width, im_height = image.size
	return np.array(image.getdata()).reshape(
		(im_height, im_width, 3)).astype(np.float64)

def to_multiple_categorical_label(size, arr):
	y = np.zeros(size)
	for i in arr:
		y[i] = 1
	return y.tolist()

def get_data():
	DATA_FOLDER = 'book_data'
	Y = []
	print('loading single label data')
	for root, dirs, files in os.walk(DATA_FOLDER):
		for name in tqdm(files):
			if name == '.DS_Store':
				continue
			[prefix, suffix] = name.split('_')
			categories = [int(z) - 2 for z in prefix[5:].split('&')]
			Y.append(to_multiple_categorical_label(9, categories))
	
	with open("data.txt", "a") as f:
		f.truncate(0)
		first = True
		MULTIPLE_LABEL_DATA = 'multilabel_data'
		print('loading multiple label data')
		for root, dirs, files in os.walk(MULTIPLE_LABEL_DATA):
			for name in tqdm(files):
				if name == '.DS_Store':
					continue
				[prefix, _] = name.split('_')
				categories = [int(z) for z in prefix.split('&')]
				Y.append(to_multiple_categorical_label(9, categories))
				image_path = os.path.join(MULTIPLE_LABEL_DATA, name)
				if first:
					f.write("{} 1".format(image_path))
					first = False
				else: 
					f.write("\n{} 1".format(image_path))
	with open("no_class.txt", "a") as f:
		f.truncate(0)
		first = True
		NO_CLASS_DATA = 'no_class'
		print('loading no class data')
		for root, dirs, files in os.walk(NO_CLASS_DATA):
			for name in tqdm(files):
				if name == '.DS_Store':
					continue
				Y.append(to_multiple_categorical_label(9, []))
				image_path = os.path.join(NO_CLASS_DATA, name)
				if first:
					f.write("{} 1".format(image_path))
					first = False
				else: 
					f.write("\n{} 1".format(image_path))
	return Y
			
Y = get_data()

# Real-time data augmentation
# img_aug = tflearn.ImageAugmentation()
# img_aug.add_random_flip_leftright()
# img_aug.add_random_90degrees_rotation (rotations=[0, 1, 2, 3])
# img_aug.add_random_crop([128, 128], padding=4)

network = tflearn.input_data(shape=[None, 128, 128, 3])
                        #  data_preprocessing=img_prep,
                        #  data_augmentation=img_aug)
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

model.fit(X, Y, n_epoch=250, validation_set=0.1,
          snapshot_epoch=False, snapshot_step=25,
          show_metric=True, batch_size=128, shuffle=True,
          run_id='resnext_cifar10')
model.save(os.path.join(CWD_PATH, 'single_prediction_3.tfl'))