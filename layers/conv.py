import tensorflow as tf
from .base import BaseLayer
from ..utils import Variable
from .. import init

__all__ = [
	"Conv1DLayer",
	"Conv2DLayer"
]


class Conv1DLayer(BaseLayer):
	"""1D convolutional layer"""

	def __init__(self, incoming, filter_size, num_filters, W=[],
				  strides=[], padding=[], **kwargs):

		self.filter_size = filter_size
		self.num_filters = num_filters
		
		dim = incoming.get_output_shape()[3].value
		shape = [filter_size, 1, dim, num_filters]
		self.shape = shape

		if not W:
			self.W = Variable(var=init.HeNormal(), shape=shape, **kwargs)
		else:
			self.W = Variable(var=W, shape=shape, **kwargs)
			
		self.strides = strides
		if not strides:
			self.strides = [1, 1, 1, 1]

		self.padding = padding
		if not padding:
			self.padding = 'VALID'
			
		# input data shape
		self.incoming_shape = incoming.get_output_shape()
		
		# output of convolution
		self.output = tf.nn.conv2d( input=incoming.get_output(), 
									filter=self.W.get_variable(), 
									strides=self.strides, 
								   	padding=self.padding, 
								   	**kwargs)
		# shape of the output
		self.output_shape = self.output.get_shape()
		
	def get_input_shape(self):
		return self.incoming_shape
	
	def get_output(self):
		return self.output
	
	def get_output_shape(self):
		return self.output_shape
	
	def get_variable(self):
		return self.W
	
	def set_trainable(self, status):
		self.W.set_trainable(status)
		
	def set_l1_regularize(self, status):
		self.W.set_l1_regularize(status)    
		
	def set_l2_regularize(self, status):
		self.W.set_l2_regularize(status)    
		
	def is_trainable(self):
		return self.W.is_trainable()
		
	def is_l1_regularize(self):
		return self.W.is_l1_regularize()    
		
	def is_l2_regularize(self):
		return self.W.is_l2_regularize()  
		


class Conv2DLayer(BaseLayer):
	"""1D convolutional layer"""

	def __init__(self, incoming, filter_size, num_filters, W=[],
				  strides=[], padding=[], **kwargs):

		self.filter_size = filter_size
		self.num_filters = num_filters
		
		dim = incoming.get_output_shape()[3].value

		if not isinstance(filter_size, list):
			self.shape = [filter_size, filter_size, dim, num_filters]
		else:
			self.shape = filter_size

		if not W:
			self.W = Variable(var=init.HeNormal(), shape=self.shape, **kwargs)
		else:
			self.W = Variable(var=W, shape=self.shape, **kwargs)
			

		if not strides:		
			self.strides = [1, 1, 1, 1]
		else:
			if not isinstance(strides, list):
				self.strides = [1, strides, strides, 1]
			else:
				self.strides = strides

		self.padding = padding
		if not padding:
			self.padding = 'VALID'
			
		# input data shape
		self.incoming_shape = incoming.get_output_shape()
		
		# output of convolution
		self.output = tf.nn.conv2d( input=incoming.get_output(), 
									filter=self.W.get_variable(), 
									strides=self.strides, 
								   	padding=self.padding, 
								   	**kwargs)
		# shape of the output
		self.output_shape = self.output.get_shape()
		
	def get_input_shape(self):
		return self.incoming_shape
	
	def get_output(self):
		return self.output
	
	def get_output_shape(self):
		return self.output_shape
	
	def get_variable(self):
		return self.W
	
	def set_trainable(self, status):
		self.W.set_trainable(status)
		
	def set_l1_regularize(self, status):
		self.W.set_l1_regularize(status)    
		
	def set_l2_regularize(self, status):
		self.W.set_l2_regularize(status)    
		
	def is_trainable(self):
		return self.W.is_trainable()
		
	def is_l1_regularize(self):
		return self.W.is_l1_regularize()    
		
	def is_l2_regularize(self):
		return self.W.is_l2_regularize()  
		