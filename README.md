## exit-signs

Playing with Exit Signs / Destination Signs.

## Usage

Build the sign location extractor:

    ./deps.sh
    make

Grab some OSM extracts:

    ./osm.sh

Run the Sign location extractor on the extract and save out a list of locations:

    ./build/Release/exit-signs osm/*.osm.pbf > signLocations.csv

Get clientId from Mapillary and use it to fetch images for locations:

    export EXIT_SIGNS_CLIENT_ID='YOUR-CLIENT-ID'
    mkdir -p signImages
    ./images.py signLocations.csv signImages


## License

Copyright © 2016 Daniel J. Hofmann

Distributed under the MIT License (MIT).
