#!/usr/bin/env python3

from sys import exit
from time import sleep
from os import environ, path
from pprint import pprint
from operator import attrgetter
from csv import reader as CSVReader
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from requests import Session

kImageBase = 'https://d1cuyjsrcm0gby.cloudfront.net/{key}/thumb-{resolution}.jpg'
kNearestService = 'https://a.mapillary.com/v2/search/im/close'
kImageResolution = 640 # in [320, 640, 1024, 2048]
kMaxDistanceInMeters = 35
kHttpTimeoutInSeconds = 0.2

def main():
    args = mkArguments()
    clientId = mkClientId()

    if not clientId:
        exit('export EXIT_SIGNS_CLIENT_ID=')

    with open(args.signFile, 'r') as handle, Session() as session:
        reader = CSVReader(handle)
        for line in reader:
            longitude = float(line[0])
            latitude = float(line[1])

            params = {'client_id': clientId, 'lon': longitude, 'lat': latitude, 'distance': kMaxDistanceInMeters}
            response = session.get(kNearestService, params=params)
            sleep(kHttpTimeoutInSeconds)

            if response.status_code != 200:
                print('Error: unable to find images for {:.5f}, {:.5f}'.format(longitude, latitude))
                continue

            json = response.json()

            if json['more']:
                pass  # Implement pagination

            images = json['ims']

            if not images:
                print('Error: no nearest images found for {:.5f}, {:.5f}'.format(longitude, latitude))
                continue

            # Take a bunch, instead of just a single nearest image
            # images.sort(key=lambda image: image['distance'])

            nearest = min(images, key=lambda image: image['distance'])

            imageAngle = nearest['ca']
            imageLongitude = nearest['lon']
            imageLatitude = nearest['lat']
            imageDistance = nearest['distance']
            imageKey = nearest['key']
            imageUrl = kImageBase.format(key=imageKey, resolution=kImageResolution)

            print('Found: at {:.5f},{:.5f} for {:.5f},{:.5f} with distance {:.0f} meters' \
                  .format(imageLongitude, imageLatitude, longitude, latitude, imageDistance))

            imageResponse = session.get(imageUrl)
            sleep(kHttpTimeoutInSeconds)

            if imageResponse.status_code != 200:
                print('Error: unable to fetch image for {:.5f}, {:.5f}'.format(longitude, latitude))
                continue

            saveTo = path.join(args.outDirectory, '{}.jpg'.format(imageKey))

            with open(saveTo, 'wb') as handle:
                _ = handle.write(imageResponse.content)


def mkClientId():
    return environ.get('EXIT_SIGNS_CLIENT_ID')

def mkArguments():
    parser = ArgumentParser(description='Image Scraper for Exit Sign / Destination Sign',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('signFile', type=str, help='path to lon,lat .csv file')
    parser.add_argument('outDirectory', type=str, help='directory to save images in')
    return parser.parse_args()



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit('\nBye')
