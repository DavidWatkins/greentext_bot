# import the necessary packages
from PIL import Image
import pytesseract
import argparse
from sklearn.cluster import MiniBatchKMeans
import cv2
import os
import numpy as np
import pytesseract
from PIL import Image
from PIL import ImageFilter
from StringIO import StringIO
import enchant
import re
from PIL import ImageEnhance
import progressbar
import enchant
import pathos
import threading
import sys
import tqdm

# dictionary = enchant.Dict("en_US")

number_of_threads = 16
images_dir = './images/'
text_dir = './texts/'

def change_contrast(img, level):
    factor = (259 * (level + 255)) / (255 * (259 - level))
    def contrast(c):
        return 128 + factor * (c - 128)
    return img.point(contrast)


def image_to_text(filename, verbose=False):
	global dictionary

	# load the example image and convert it to grayscale
	image = Image.open(filename)
	image = image.convert('L')                 # Convert to grayscale
	image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
	image = change_contrast(image, 75)         # Increase the constrast

	# Scale the image to width of 1000
	basewidth = 1000
	wpercent = (basewidth/float(image.size[0]))
	hsize = int((float(image.size[1])*float(wpercent)))
	image = image.resize((basewidth,hsize), Image.ANTIALIAS)

	# load the image as a PIL/Pillow image, apply OCR, and then delete
	# the temporary file
	text = pytesseract.image_to_string(image, config="-c tessedit_char_whitelist=>0123456789ABCDEFGHIJKLMONPQRSTUVWXYZ-abcdqefghijklmnopqrstuvwxyz.?,$:\\' -psm 6")

	out_string = ""
	found_greentext_start = False

	for line in text.split("\n"):
		if not line.startswith(">") and not found_greentext_start:
			continue

		found_greentext_start = True

		truncated_line = line.strip() # re.sub(r'.*>', '>', line)
		if len(truncated_line) <= 1:
			continue

		out_string += truncated_line + "\n"
		if verbose:
			print(truncated_line)
			# for word in truncated_line.split(" "):
			# 	word = word.strip("")
			# 	if len(word) > 0 and not dictionary.check(word):
			# 		print("{} -> {}".format(word, dictionary.suggest(word)))

	if verbose:
		cv2.imshow("image", np.hstack([image]))
		cv2.waitKey(0)

	return out_string


file_count = 0
file_write_lock = threading.Lock()
success_bar = None
fail_bar = None


def process_image_path(filename):
	global file_count
	global file_write_lock
	global success_bar
	global fail_bar

	try:

		image_path = os.path.join(images_dir, filename)

		if os.path.isfile(image_path):
			text = image_to_text(image_path, verbose=False)

			basename = os.path.basename(image_path).replace(" ", "_")
			
			return True, text

	except IOError as e:
		return False, ""
		# print("Could not open file '{}'".format(filename))


def main():
	global file_count
	global file_write_lock
	global success_bar
	global fail_bar
	if not os.path.isdir(text_dir):
		os.makedirs(text_dir)

	num_images = len([name for name in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, name))])
	success_bar = tqdm.tqdm(total=num_images, position=1)
	fail_bar = tqdm.tqdm(total=num_images, position=0)

	pool = pathos.multiprocessing.Pool(processes=number_of_threads)
	jobs = os.listdir(images_dir)

	# for job in jobs:
	# 	process_image_path(job)
	# 	bar += 1

	file_count = 0
	for success, text in pool.imap_unordered(process_image_path, jobs):
		if success:
			success_bar.update(1)
			text_path = os.path.join(text_dir, "{}.txt".format(file_count))
			with open(text_path, 'w') as outfile:
				outfile.write(text)
			file_count += 1
		else:
			fail_bar.update(1)


if __name__ == "__main__":
	main()
