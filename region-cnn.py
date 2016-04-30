#!/usr/bin/env python3

from sys import exit
from csv import reader as CSVReader
from collections import defaultdict, namedtuple
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import numpy as np

from skimage import io
from skimage.segmentation import felzenszwalb

# The following is guided by the R-CNN paper [0] and selective search as proposed in [1].
#
# [0] "Rich feature hierarchies for accurate object detection and semantic segmentation"
#     doi: 10.1109/TPAMI.2015.2437384
#     http://arxiv.org/abs/1311.2524
#
# [1] "Selective Search for Object Recognition"
#     doi: 10.1007/s11263-013-0620-5
#     https://ivi.fnwi.uva.nl/isis/publications/2013/UijlingsIJCV2013


kFelzenszwalbScale = 500

Rectangle = namedtuple('Rectangle', 'x0 y0 x1 y1')


def selectiveSearch(image):
    mask = felzenszwalb(image, scale=kFelzenszwalbScale)
    numRegions = mask.max()

    def aabb(region):
        (x0, y0) = np.min(region, axis=0)
        (x1, y1) = np.max(region, axis=0)
        return Rectangle(x0, y0, x1, y1)

    for regionTag in range(numRegions):
        selectedRegion = mask == regionTag
        regionPixelIndices = np.transpose(np.nonzero(selectedRegion))
        rectangle = aabb(regionPixelIndices)
        print(rectangle)

    # Implement merging, similarities, ..

    io.imshow_collection([image, mask])
    io.show()


def trainFromLabeledRegions(labelFile):
    pathsWithLabeledRegions = defaultdict(list)

    with open(labelFile) as handle:
        for line in CSVReader(handle):
            # Region is made up of: path, x0, y0, x1, y1
            pathsWithLabeledRegions[line[0]].append([(line[1], line[2]), (line[3], line[4])])

    for imagePath in pathsWithLabeledRegions.keys():
        image = io.imread(imagePath)
        proposedRegions = selectiveSearch(image);

        break  ### Testing with a single image first


def predictRegionFromFile(predictionImage):
    # regionProposals = selectiveSearch(image)
    # bestRegions = []
    # for region in regionProposals:
    #     warped = warpRegion(region)
    #     features = cnn.predict(warped)
    #     bestRegions.append(svm.predict(features))
    # best = nonMaximumSuppression(bestRegions)
    # return best
    exit('No')


def main():
    args = mkArguments()

    if args.train:
        trainFromLabeledRegions(args.train)
    elif args.predict:
        predictRegionFromFile(args.predict)


def mkArguments():
    parser = ArgumentParser(description='Train and evaluate a region convolutional neural net model',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    trainOrPredict = parser.add_mutually_exclusive_group(required=True)
    trainOrPredict.add_argument('--train', type=str, help='.csv label file to train model on')
    trainOrPredict.add_argument('--predict', type=str, help='image to run prediction on')
    return parser.parse_args()



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit('\nBye')
