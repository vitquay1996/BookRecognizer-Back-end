from __future__ import division, print_function, absolute_import

import tensorflow as tf
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_1d, global_max_pool, max_pool_1d
from tflearn.layers.merge_ops import merge
from tflearn.layers.estimator import regression
from tflearn.data_utils import to_categorical, pad_sequences
import numpy as np
tf.reset_default_graph()
network = input_data(shape=[None, 11], name='input')
network = tflearn.embedding(network, input_dim=1000, output_dim=128)
branch1 = conv_1d(network, 128, 3, padding='valid', activation='relu', regularizer="L2")
branch1 = max_pool_1d(branch1, 2)
branch2 = conv_1d(network, 128, 4, padding='valid', activation='relu', regularizer="L2")
branch2 = max_pool_1d(branch2, 2)
branch3 = conv_1d(network, 128, 5, padding='valid', activation='relu', regularizer="L2")
branch3 = max_pool_1d(branch3, 2)
network = merge([branch1, branch2, branch3], mode='concat', axis=1)
network = dropout(network, 0.5)
network = fully_connected(network, 2, activation='softmax')
network = regression(network, optimizer='adam', learning_rate=0.005,
                     loss='categorical_crossentropy', name='target')
# Training
model = tflearn.DNN(network, tensorboard_verbose=0)
model.load('./user.tfl')

def predict_which_book_might_like(X):
	# X = np.expand_dims(X, axis=0)
	X = pad_sequences(X, maxlen=11, value=0.)
	y = model.predict(X)
	y = np.argmax(y, axis=1)
	return y.tolist()

