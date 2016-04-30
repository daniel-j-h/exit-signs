#!/usr/bin/env python3

from os.path import abspath
from sys import exit
from csv import writer as CSVWriter
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import numpy as np

from skimage import io

# from skimage.viewer.plugins import LabelPainter
# Unfortunately LabelPainter is currently broken, let's implement a basic matplotlib solution

import matplotlib.pyplot as plt
import matplotlib.patches as mpatch


def main():
    args = mkArguments()

    image = io.imread(args.image)

    plt.imshow(image)

    points = []

    def onButton(event):
        x, y = int(event.xdata), int(event.ydata)
        points.append((x, y))
        print('Rectangle[{}]: at {},{}'.format('start' if len(points) % 2 != 0 else 'end', x, y))

    def onKey(event):
        if event.key == 'q' and points:
            points.pop()
        elif event.key == 'w':
            exit('Error: discarding rectangles, label again')
        elif event.key == 'e':
            plt.close()

    plt.connect('button_press_event', onButton)
    plt.connect('key_press_event', onKey)

    plt.title('mouse press: add point, q: pop point, w: discard, e: next')
    plt.axis('off')
    plt.show()

    if not points or len(points) % 2 != 0:
        exit('Error: unable to make up rectangles from no or odd number of points')

    with open(args.labelFile, 'a') as handle:
        writer = CSVWriter(handle)
        for i in range(0, len(points) - 1, 2):
            p0, p1 = points[i], points[i+1]
            (x0, y0) = np.min([p0, p1], axis=0)
            (x1, y1) = np.max([p0, p1], axis=0)

            # Region is made up of: path, x0, y0, x1, y1 (bottom left, top right)
            writer.writerow([abspath(args.image), x0, y0, x1, y1])


def mkArguments():
    parser = ArgumentParser(description='Label images with rectangle regions of interest',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('image', type=str, help='image to label with rectangles')
    parser.add_argument('labelFile', type=str, help='.csv file to append labeled regions for image to')
    return parser.parse_args()



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit('\nBye')
