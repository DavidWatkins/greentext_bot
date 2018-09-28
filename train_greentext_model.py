# coding: utf-8

import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

from textgenrnn import textgenrnn

from tensorflow.python.client import device_lib

textgen = textgenrnn()

textgen.train_from_file(
	'r-greentext-corpus.txt', 
	num_epochs=10, 
	rnn_bidirectional=True,
	max_length=200,
	rnn_layers=6,
	max_words=100000,
	batch_size=128
)
textgen.save('greentext_weights.hdf5')
responses = textgen.generate(n=10, return_as_list=True, max_gen_length=2000, temperature=0.5)

for response in responses:
	print(response.replace("|", "\n"))
	print("_____________________________")


print(textgen.model.summary())
