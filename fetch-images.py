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
kHttpTimeoutInSeconds = 0.1
kMaxImagesPerLocation = 3


def main():
    args = mkArguments()
    clientId = mkClientId()

    if not clientId:
        exit('export EXIT_SIGNS_CLIENT_ID=')

    with open(args.signFile, 'r') as handle, Session() as session:
        mkImagesFor = lambda idx, lon, lat: mkImages(args.outDirectory, clientId, session, idx, lon, lat)

        for idx, line in enumerate(CSVReader(handle)):
            longitude = float(line[0])
            latitude = float(line[1])
            try:
                mkImagesFor(idx, longitude, latitude)
            except Exception as e:
                print('Error[{}]: unexpected exception'.format(idx))



def mkImages(outDirectory, clientId, session, idx, longitude, latitude):
    params = {'client_id': clientId, 'lon': longitude, 'lat': latitude, 'distance': kMaxDistanceInMeters}
    response = session.get(kNearestService, params=params)
    sleep(kHttpTimeoutInSeconds)

    if response.status_code != 200:
        print('Error[{}]: nearest request failed'.format(idx))
        return

    json = response.json()

    if json['more']:
        pass  # Implement pagination? Seems like kMaxImagesPerLocation is good enough for now.

    images = json['ims']

    if not images:
        print('Error[{}]: no images found'.format(idx))
        return

    # Take a bunch instead of just a single nearest image
    images.sort(key=lambda image: image['distance'])

    for nearest in images[:kMaxImagesPerLocation]:
        imageAngle = nearest['ca']
        imageLongitude = nearest['lon']
        imageLatitude = nearest['lat']
        imageDistance = nearest['distance']
        imageKey = nearest['key']
        imageUrl = kImageBase.format(key=imageKey, resolution=kImageResolution)

        print('Found[{}]: image with distance {:.0f} meters'.format(idx, imageDistance))

        imageResponse = session.get(imageUrl)
        sleep(kHttpTimeoutInSeconds)

        if imageResponse.status_code != 200:
            print('Error[{}]: image request failed'.format(idx))
            continue

        saveTo = path.join(outDirectory, '{}.jpg'.format(imageKey))

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
