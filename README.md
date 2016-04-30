## exit-signs

Playing with Exit Signs / Destination Signs.

High-level idea:
Extract location for `destination=*` and `exit_to=*` tags from OSM ways and nodes and query Mapillary to retrieve dashcam images.
Use these labeled images to train a model that is able to predict signs from unlabeled images.

![Signs](https://raw.github.com/daniel-j-h/exit-signs/master/.image.jpg)

[Mapillary](http://mapillary.com) images licensed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).

## Preparation

Build the sign location extractor:

    ./deps.sh
    make

Grab some OSM extracts:

    ./osm.sh

Get a clientId from Mapillary and export it for image fetching:

    export EXIT_SIGNS_CLIENT_ID='YOUR-CLIENT-ID'

## Usage

Run the Sign location extractor on the extract and save out a list of locations:

    ./build/Release/extract-locations osm/*.osm.pbf > signLocations.csv

Fetch images for locations:

    mkdir -p signImages
    ./fetch-images.py signLocations.csv signImages

Clean up images and label them with rectangles to generate a training set:

    for image in signImages; do ./label-image.py signImages/$image signImages/labels.csv; done

Train the R-CNN model on labeled images:

    ./region-cnn.py --train signImages/labels.csv

Predict signs on a new image:

    ./region-cnn.py --predict image.jpg


## License

Copyright © 2016 Daniel J. Hofmann

Distributed under the MIT License (MIT).
