#!/usr/bin/env python3

from sys import exit
from random import randint
from csv import reader as CSVReader
from collections import defaultdict, namedtuple
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import numpy as np

from skimage import io, draw, transform
from skimage.segmentation import felzenszwalb

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.utils import np_utils


# The following is guided by the R-CNN paper [0] and selective search as proposed in [1].
# This is work in progress and we're taking a lot of shortcuts here to get a MVP going.
#
# [0] "Rich feature hierarchies for accurate object detection and semantic segmentation"
#     doi: 10.1109/TPAMI.2015.2437384
#     http://arxiv.org/abs/1311.2524
#
# [1] "Selective Search for Object Recognition"
#     doi: 10.1007/s11263-013-0620-5
#     https://ivi.fnwi.uva.nl/isis/publications/2013/UijlingsIJCV2013


kFelzenszwalbScale = 500
kNetImageShape = (3, 100, 100)
kNetNumClasses = 2
kNetBatchSize = 10000
kNetNumEpochs = 1
kNetValidationSplit = 0.1


def main():
    args = mkArguments()

    if args.positive and args.negative:
        trainFromLabeledRegions(args.positive, args.negative, args.modelFile)
    elif args.predict:
        predictRegionFromFile(args.predict, args.modelFile)


class Rectangle(namedtuple('Rectangle', 'x0 y0 x1 y1')):
    def pixels(_, shape):
        return draw.polygon([_.x0, _.x0, _.x1, _.x1], [_.y0, _.y1, _.y1, _.y0], shape)


def trainFromLabeledRegions(positiveLabelFile, negativeLabelFile, modelFile):
    def readImagePathsLabels(labelFile):
        pathsWithLabeledRegions = defaultdict(list)

        with open(labelFile) as handle:
            for line in CSVReader(handle):
                imagePath = line[0]
                rectangle = Rectangle(int(line[1]), int(line[2]), int(line[3]), int(line[4]))
                pathsWithLabeledRegions[imagePath].append(rectangle)

        return pathsWithLabeledRegions

    positiveSamples = readImagePathsLabels(positiveLabelFile)
    negativeSamples = readImagePathsLabels(negativeLabelFile)

    numPositiveSamples = sum(len(rectangles) for rectangles in positiveSamples.values())
    numNegativeSamples = sum(len(rectangles) for rectangles in negativeSamples.values())
    numSamples = numPositiveSamples + numNegativeSamples

    x = np.zeros((numSamples, kNetImageShape[0], kNetImageShape[1], kNetImageShape[2]), dtype='uint8')
    y = np.zeros((numSamples, kNetNumClasses), dtype='uint8')

    idx = 0

    def batchReadImageDataAndLabel(pathsWithLabeledRegions, idx, label):
        for imagePath, rectangles in pathsWithLabeledRegions.items():
            image = io.imread(imagePath)

            for rectangle in rectangles:
                sign = image[rectangle.y0 : rectangle.y1, rectangle.x0 : rectangle.x1 , :]

                fixedSize = transform.resize(sign, (kNetImageShape[1], kNetImageShape[2]))
                sample = np.reshape(fixedSize, kNetImageShape)
                x[idx] = sample
                y[idx] = [label]

                idx += 1

        return idx

    idx = batchReadImageDataAndLabel(positiveSamples, idx, 1)
    idx = batchReadImageDataAndLabel(negativeSamples, idx, 0)

    model = getCNN()
    history = model.fit(x, y, batch_size=kNetBatchSize, nb_epoch=kNetNumEpochs, validation_split=kNetValidationSplit)

    model.save_weights(modelFile)


def getCNN():
    model = Sequential()

    model.add(Convolution2D(32, 3, 3, activation='relu', input_shape=kNetImageShape))
    model.add(Convolution2D(32, 3, 3, activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Convolution2D(64, 3, 3, activation='relu'))
    model.add(Convolution2D(64, 3, 3, activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))

    model.add(Dense(kNetNumClasses, activation='softmax'))

    model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])

    return model


def predictRegionFromFile(predictionImage, modelFile):
    # regionProposals = selectiveSearch(image)
    # bestRegions = []
    # for region in regionProposals:
    #     warped = warpRegion(region)
    #     features = cnn.predict(warped)
    #     bestRegions.append(svm.predict(features))
    # best = nonMaximumSuppression(bestRegions)
    # return best
    exit('No')


def aabb(region):
    (x0, y0) = np.min(region, axis=0)
    (x1, y1) = np.max(region, axis=0)
    return Rectangle(x0, y0, x1, y1)


def selectiveSearch(image):
    segments = felzenszwalb(image, scale=kFelzenszwalbScale)
    numRegions = segments.max()

    rectangles = []

    for regionTag in range(numRegions):
        selectedRegion = segments == regionTag
        regionPixelIndices = np.transpose(np.nonzero(selectedRegion))
        rectangle = aabb(regionPixelIndices)
        rectangles.append(rectangle)

    # Implement similarities, neighbourhood merging.
    # Felzenszwalb's segmentation is ridiculously good already.

    def debug():
        marked = np.zeros(image.shape, dtype=np.uint8)

        for rectangle in rectangles:
            rr, cc = rectangle.pixels(marked.shape)
            randcolor = randint(0, 255), randint(0, 255), randint(0, 255)
            marked[rr, cc] = randcolor

        print(image.shape, segments.shape, marked.shape)

        io.imshow_collection([image, segments, marked])
        io.show()

    # debug()

    return rectangles


def mkArguments():
    parser = ArgumentParser(description='Train and evaluate a region convolutional neural net model',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--positive', type=str, help='.csv label file with positive samples to train model on')
    parser.add_argument('--negative', type=str, help='.csv label file with negative samples to train model on')
    parser.add_argument('--predict', type=str, help='image to run prediction on')
    parser.add_argument('--modelFile', type=str, default='model.hdf5' help='.hdf5 model file to load model from or save model to')
    return parser.parse_args()



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit('\nBye')
