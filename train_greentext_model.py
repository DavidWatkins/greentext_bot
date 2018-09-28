# coding: utf-8

import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

from textgenrnn import textgenrnn

from tensorflow.python.client import device_lib

textgen = textgenrnn()
textgen.train_from_file('r-greentext-corpus.txt', num_epochs=1)
textgen.save('greentext_weights.hdf5')
textgen.generate(interactive=True, top_n=5)
