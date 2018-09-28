import os
import progressbar

text_dir = './texts/'

corpus_filepath = 'r-greentext-corpus.txt'
delim = '|'

num_txts = len([name for name in os.listdir(text_dir) if os.path.isfile(os.path.join(text_dir, name))])
bar = progressbar.ProgressBar(max_value=num_txts)	

with open(corpus_filepath, 'w') as corpus:

	files = os.listdir(text_dir)

	for filename in files:

		text_path = os.path.join(text_dir, filename)

		if os.path.isfile(text_path):

			with open(text_path, 'r') as datum:
				datum_txt = datum.read()
				if len(datum_txt) == 0:
					continue

				datum_txt = delim.join(datum_txt.split("\n"))
				corpus.write(datum_txt + "\n")

		bar += 1
