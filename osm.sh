#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

readonly OSMURLS=(
  "https://s3.amazonaws.com/metro-extracts.mapzen.com/berlin_germany.osm.pbf"
  "https://s3.amazonaws.com/metro-extracts.mapzen.com/san-francisco-bay_california.osm.pbf"
)

readonly OSMDIR="osm"

mkdir -p ${OSMDIR}
pushd ${OSMDIR}
for URL in ${OSMURLS[@]}; do wget --quiet ${URL}; done
popd
