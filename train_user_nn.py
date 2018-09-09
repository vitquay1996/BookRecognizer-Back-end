from __future__ import division, print_function, absolute_import

import tensorflow as tf
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_1d, global_max_pool, max_pool_1d
from tflearn.layers.merge_ops import merge
from tflearn.layers.estimator import regression
from tflearn.data_utils import to_categorical, pad_sequences
def get_user_data():
	f = open('user_history.txt', 'r')
	x = f.read().splitlines()
	X = []
	Y = []
	for line in x:
		line = [float(z) for z in line.split(',')]
		X.append(line[:-1])
		Y.append(line[len(line) - 1])

	return X, Y



X, Y = get_user_data()
# Data preprocessing
# Sequence padding
X = pad_sequences(X, maxlen=11, value=0.)
Y = to_categorical(Y, 2)

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
model.fit(X, Y, n_epoch = 100, shuffle=True, validation_set=0.2, show_metric=True, batch_size=32)

model.save('./user.tfl')