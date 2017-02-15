from __future__ import print_function 
from tfomics import layers
from tfomics import init

from collections import OrderedDict

__all__ = [
	"build_network"
]


def build_network(model_layers):
	""" build all layers in the model """

	network, lastlayer = build_layers(model_layers)
	network['output'] = network[lastlayer]
	return network


def build_layers(model_layers, network=OrderedDict()):

	# loop to build each layer of network
	lastlayer = ''
	for model_layer in model_layers:
		layer = model_layer['layer']
		name = model_layer['name']

		if layer == "input":

			# add input layer
			network[name] = single_layer(model_layer, network)
			lastlayer = name

		else:
			if layer == 'residual-conv1d':
				if 'dropout' in model_layer:
					dropout = model_layer['dropout']
				else:
					dropout = []
				if 'function' in model_layer:
					activation = model_layer['function']
				else:
					activation = 'relu'

				network = conv1d_residual_block(network, lastlayer, 
											model_layer['name'], 
										 	model_layer['filter_size'], 
										 	model_layer['is_training'], 
										 	dropout=dropout, 
										 	activation=activation)
				lastlayer = name+'_resid'

			elif layer == 'residual-conv2d':
				if 'dropout' in model_layer:
					dropout = model_layer['dropout']
				else:
					dropout = []
				if 'function' in model_layer:
					activation = model_layer['function']
				else:
					activation = 'relu'

				network = conv2d_residual_block(network, lastlayer, 
											model_layer['name'], 
										 	model_layer['filter_size'], 
										 	model_layer['is_training'], 
										 	dropout=dropout, 
										 	activation=activation)
				lastlayer = name+'_resid'

			elif layer == 'residual-dense':
				if 'dropout' in model_layer:
					dropout = model_layer['dropout']
				else:
					dropout = []

				if 'function' in model_layer:
					activation = model_layer['function']
				else:
					activation = 'relu'

				network = dense_residual_block(network, lastlayer, 
												model_layer['name'], 
												model_layer['is_training'], 
												dropout=dropout, 
												activation=activation)
				lastlayer = name+'_resid'

			else:
				# add core layer
				newlayer = name #'# str(counter) + '_' + name + '_batch'
				network[newlayer] = single_layer(model_layer, network[lastlayer])
				lastlayer = newlayer

				# add bias layer
				if 'b' in model_layer:
					newlayer = name+'_bias'
					network[newlayer] = layers.BiasLayer(network[lastlayer], b=model_layer['b'])
					lastlayer = newlayer    


		# add Batch normalization layer
		if 'batch_norm' in model_layer:
			newlayer = name + '_batch' #str(counter) + '_' + name + '_batch'
			network[newlayer] = layers.BatchNormLayer(network[lastlayer], model_layer['batch_norm'])
			lastlayer = newlayer

		# add activation layer
		if 'activation' in model_layer:
			newlayer = name+'_active'
			network[newlayer] = layers.ActivationLayer(network[lastlayer], function=model_layer['activation']) 
			lastlayer = newlayer

		# add max-pooling layer
		if 'pool_size' in model_layer:  
			newlayer = name+'_pool'  # str(counter) + '_' + name+'_pool' 
			if isinstance(model_layer['pool_size'], (tuple, list)):
				network[newlayer] = layers.MaxPool2DLayer(network[lastlayer], pool_size=model_layer['pool_size'])
			else:
				network[newlayer] = layers.MaxPool2DLayer(network[lastlayer], pool_size=(model_layer['pool_size'], 1))
			lastlayer = newlayer       

		# add dropout layer
		if 'dropout' in model_layer:
			newlayer = name+'_dropout' # str(counter) + '_' + name+'_dropout'
			network[newlayer] = layers.DropoutLayer(network[lastlayer], keep_prob=model_layer['dropout'])
			lastlayer = newlayer


	return network, lastlayer


def single_layer(model_layer, network_last):
	""" build a single layer"""

	# input layer
	if model_layer['layer'] == 'input':
		network = layers.InputLayer(model_layer['inputs'])

	# dense layer
	elif model_layer['layer'] == 'dense':
		if 'W' not in model_layer.keys():
			model_layer['W'] = init.HeNormal()
		if 'b' not in model_layer.keys():
			model_layer['b'] = init.Constant(0.05)
		network = layers.DenseLayer(network_last, num_units=model_layer['num_units'],
											 W=model_layer['W'],
											 b=model_layer['b'])

	# convolution layer
	elif (model_layer['layer'] == 'conv2d'):
		if 'W' not in model_layer.keys():
			W = init.HeNormal()
		else:
			W = model_layer['W']
		if 'padding' not in model_layer.keys():
			padding = 'VALID'
		else:
			padding = model_layer['padding']
		if 'strides' not in model_layer.keys():
			strides = (1, 1)
		else:
			strides = model_layer['strides']

		network = layers.Conv2DLayer(network_last, num_filters=model_layer['num_filters'],
											  filter_size=model_layer['filter_size'],
											  W=W,
											  padding=padding,
											  strides=strides)
	elif model_layer['layer'] == 'conv1d':
		if 'W' not in model_layer.keys():
			W = init.HeNormal()
		else:
			W = model_layer['W']
		if 'padding' not in model_layer.keys():
			padding = 'VALID'
		else:
			padding = model_layer['padding']
		if 'strides' not in model_layer.keys():
			strides = 1
		else:
			strides = model_layer['strides']


		network = layers.Conv1DLayer(network_last, num_filters=model_layer['num_filters'],
											  filter_size=model_layer['filter_size'],
											  W=W,
											  padding=padding,
											  strides=strides)

	return network


def conv1d_residual_block(network, lastlayer, name, filter_size, is_training, **kwargs):

	# original residual unit
	shape = network[lastlayer].get_output_shape()
	num_filters = shape[-1].value

	if not isinstance(filter_size, (list, tuple)):
		filter_size = (filter_size, 1)

	activation = 'relu'
	if 'activation' in kwargs.keys():
		activation = kwargs['activation']

	network[name+'_1resid'] = layers.Conv2DLayer(network[lastlayer], num_filters=num_filters, filter_size=filter_size, padding='SAME')
	network[name+'_1resid_norm'] = layers.BatchNormLayer(network[name+'_1resid'], is_training)
	network[name+'_1resid_active'] = layers.ActivationLayer(network[name+'_1resid_norm'], function=activation)

	if 'dropout' in kwargs.keys():
		network[name+'_dropout1'] = layers.DropoutLayer(network[name+'_1resid_active'], keep_prob=kwargs['dropout'])
		lastname = name+'_dropout1'
	else:
		lastname = name+'_1resid_active'

	network[name+'_2resid'] = layers.Conv2DLayer(network[lastname], num_filters=num_filters, filter_size=filter_size, padding='SAME')
	network[name+'_2resid_norm'] = layers.BatchNormLayer(network[name+'_2resid'], is_training)
	network[name+'_resid_sum'] = layers.ElementwiseSumLayer([network[lastlayer], network[name+'_2resid_norm']])
	network[name+'_resid'] = layers.ActivationLayer(network[name+'_resid_sum'], function=activation)
	return network



def conv2d_residual_block(network, lastlayer, name, filter_size, is_training, **kwargs):

	# original residual unit
	shape = network[lastlayer].get_output_shape()
	num_filters = shape[-1].value

	if not isinstance(filter_size, (list, tuple)):
		filter_size = (filter_size, 1)

	activation = 'relu'
	if 'activation' in kwargs.keys():
		activation = kwargs['activation']

	network[name+'_1resid'] = layers.Conv2DLayer(network[lastlayer], num_filters=num_filters, filter_size=filter_size, padding='SAME')
	network[name+'_1resid_norm'] = layers.BatchNormLayer(network[name+'_1resid'], is_training)
	network[name+'_1resid_active'] = layers.ActivationLayer(network[name+'_1resid_norm'], function=activation)

	if 'dropout' in kwargs.keys():
		network[name+'_dropout1'] = layers.DropoutLayer(network[name+'_1resid_active'], keep_prob=kwargs['dropout'])
		lastname = name+'_dropout1'
	else:
		lastname = name+'_1resid_active'

	network[name+'_2resid'] = layers.Conv2DLayer(network[lastname], num_filters=num_filters, filter_size=filter_size, padding='SAME')
	network[name+'_2resid_norm'] = layers.BatchNormLayer(network[name+'_2resid'], is_training)
	network[name+'_resid_sum'] = layers.ElementwiseSumLayer([network[lastlayer], network[name+'_2resid_norm']])
	network[name+'_resid'] = layers.ActivationLayer(network[name+'_resid_sum'], function=activation)
	return network



def dense_residual_block(network, lastlayer, name, is_training, **kwargs):

	# original residual unit
	shape = network[lastlayer].get_output_shape()
	num_units = shape[-1].value

	activation = 'relu'
	if 'activation' in kwargs.keys():
		activation = kwargs['activation']

	network[name+'_1resid'] = layers.DenseLayer(network[lastlayer], num_units=num_units, b=None)
	network[name+'_1resid_norm'] = layers.BatchNormLayer(network[name+'_1resid'], is_training)
	network[name+'_1resid_active'] = layers.ActivationLayer(network[name+'_1resid_norm'], function=activation)

	if 'dropout' in kwargs.keys():
		network[name+'_dropout1'] = layers.DropoutLayer(network[name+'_1resid_active'], keep_prob=kwargs['dropout'])
		lastname = name+'_dropout1'
	else:
		lastname = name+'_1resid_active'

	network[name+'_2resid'] = layers.DenseLayer(network[lastname], num_units=num_units, b=None)
	network[name+'_2resid_norm'] = layers.BatchNormLayer(network[name+'_2resid'], is_training)
	network[name+'_resid_sum'] = layers.ElementwiseSumLayer([network[lastlayer], network[name+'_2resid_norm']])
	network[name+'_resid'] = layers.ActivationLayer(network[name+'_resid_sum'], function=activation)
	return network

