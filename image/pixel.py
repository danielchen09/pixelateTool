from PIL import Image
import numpy as np
import math
from collections import Counter
import random
import pickle

class Pixelate:
	def __init__(self, filename, unitSize = 5, n_colors = 10, lookupTable = None):
		self.image = np.array(Image.open(filename))
		self.unitSize = unitSize
		self.height, self.width = self.image.shape[0:2]
		self.canvas = Image.new('RGB', (self.width, self.height))


		if lookupTable:
			self.lookupTable = lookupTable
		else:
			self.lookupTable = getDominantColors(self.image, n_colors, 5)

		self.pixelate()
		

	def pixelate(self):
		print("pixelating...")

		for i in range(0, self.height, self.unitSize):
			for j in range(0, self.width, self.unitSize):
				sr = sg = sb = 0
				for h in range(i, min(i+self.unitSize, self.height)):
					for w in range(j, min(j+self.unitSize, self.width)):
						sr += self.image[h][w][0]
						sg += self.image[h][w][1]
						sb += self.image[h][w][2]
				for h in range(i, min(i+self.unitSize, self.height)):
					for w in range(j, min(j+self.unitSize, self.width)):
						a = self.unitSize**2
						c = (sr//a, sg//a, sb//a)
						minD = np.linalg.norm(np.array(c)-np.array(self.lookupTable[0]))
						minC = self.lookupTable[0]
						for t in self.lookupTable:
							d = np.linalg.norm(np.array(c) - np.array(t))
							if d < minD:
								minD = d
								minC = t

						self.canvas.putpixel((w, h), minC)

		self.canvas.show()

	@staticmethod
	def getDominantColors(image, n_colors = 5, epochs = 3):
		clusters = {}


		#find random point
		for i in range(n_colors):
			randC = tuple(image[random.randrange(0, image.shape[0])][random.randrange(0, image.shape[1])])

			while randC in clusters:
				randC = tuple(image[random.randrange(0, image.shape[0])][random.randrange(0, image.shape[1])])
			clusters[randC] = []

		print("getting dominant colors...")
		for e in range(epochs):
			#group into clusters
			for i in range(image.shape[0]):
				for j in range(image.shape[1]):
					c = image[i][j]

					minimum = (list(clusters.keys())[0], np.linalg.norm(np.array(c) - np.array(list(clusters.keys())[0])))
					for key, value in clusters.items():
						distance = np.linalg.norm(np.array(c) - np.array(key))
						if distance < minimum[1]:
							minimum = (key, distance)

					clusters[minimum[0]].append(c)

			#update center
			newclusters = {}
			for key, value in clusters.items():
				r = sum([i[0] for i in value])//len(value)
				g = sum([i[1] for i in value])//len(value)
				b = sum([i[2] for i in value])//len(value)

				if (r,g,b) not in newclusters:
					newclusters[(r,g,b)] = []

			percentChange = 0
			if e != 0:
				percentChange = max([np.linalg.norm(np.array(ci[0]) - np.array(cf[0])) for ci, cf in zip(clusters.items(), newclusters.items())]) - diff
				percentChange *= 100/diff

			diff = max([np.linalg.norm(np.array(ci[0]) - np.array(cf[0])) for ci, cf in zip(clusters.items(), newclusters.items())])

			clusters = newclusters
			print("epoch %s/%s complete, max difference: %s(%s%%)"%(e+1, epochs, diff, percentChange))

		table = []
		for key, value in clusters.items():
			table.append(key)

		Pixelate.showLookupTable(table, "epoch%s.BMP"%(e+1))

		return table

	@staticmethod
	def showLookupTable(table, title, width = 10):
		s = 10
		n = min(width, len(table))
		w = s*n
		h = math.ceil(len(table)/n)*s
		im = Image.new('RGB', (w, h))

		index = 0
		for i in range(0, h, s):
			for j in range(0, w, s):
				for y in range(i, i+s):
					for x in range(j, j+s):
						if index < len(table):
							im.putpixel((x, y), (table[index]))
				index += 1

		im.show(title = title)

n_colors = 5
filename = "sample2.jpeg"
# Image.open(filename).show()
# t = Pixelate.getDominantColors(np.array(Image.open(filename)), n_colors = n_colors, epochs = 5)
# print("saving lookup table...")
# with open(filename.split(".")[0] + "_%s"%n_colors, 'wb') as f:
# 	pickle.dump(t, f)
with open("sample7_5", 'rb') as f:
	t = pickle.load(f)
p = Pixelate("sample6.jpg", unitSize = 1, n_colors = n_colors, lookupTable = t)
p = Pixelate("sample6.jpg", unitSize = 3, n_colors = n_colors, lookupTable = t)
# p = Pixelate(filename, unitSize = 5, n_colors = n_colors, lookupTable = t)
# p = Pixelate(filename, unitSize = 10, n_colors = n_colors, lookupTable = t)
# p = Pixelate(filename, unitSize = 15, n_colors = n_colors, lookupTable = t)

