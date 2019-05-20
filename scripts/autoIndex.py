#!/usr/bin/env python3
import ogr
import os
import subprocess
import click
import logging
import json

from satstac import Catalog, Collection, Item
from satsearch import Search

logger = logging.getLogger('odcindexer')

def stac_search(extent, start_date, end_date):
    """ Convert lat, lon to pathrows """
    logger.info("Querying STAC for area: {} and times: {} - {} (UTC)".format(extent, start_date, end_date))
    srch = Search(bbox=extent, time='{}T00:00:00Z/{}T23:59:59Z'.format(start_date,end_date), 
                    url="https://sat-api.developmentseed.org/stac/search")
    try:
        logger.info("Found {} items".format(srch.found()))
        return srch
    except KeyError:
        return None


def index_datasets(items):
    for item in items:
        if "MTL" in item.assets:
            logger.info("TODO: index {}".format(item.assets["MTL"]["href"]))
        else:
            logger.warn("WARN: Item {} does not have an MTL asset (Sentinel2?) - skipping".format(item))


# Probably should use Click like the other scripts? -agl
@click.command()
@click.option('--extents', '-e', default="146.30,146.83,-43.54,-43.20", help="Extent to index in the form lon_min,lon_max,lat_min,latmax")
# @click.option('--pathrow_file', '-p', default="/opt/odc/data/wrs2_descending.zip", help="Absolute path to the pathrow file, e.g., /tmp/example.zip")
@click.option('--start_date', default="2013-02-11", help="Start date of the acquisitions to index, in YYYY-MM-DD format (UTC)")
@click.option('--end_date', default="2099-12-31", help="End date of the acquisitions to index, in YYYY-MM-DD format (UTC)")
def index(extents, start_date, end_date, write_extents=True):
    lon_min, lon_max, lat_min, lat_max = map(float, extents.split(','))

    if write_extents:
        with open('/opt/odc/data/configIndex.txt', 'w') as outfile:
            json.dump({'extent': [lon_min, lon_max, lat_min, lat_max]}, outfile)

    srch = stac_search([lon_min, lat_min, lon_max, lat_max], start_date, end_date)
    if not srch:
        logging.error("STAC search failed, stopping.")
        return
    logging.info("Indexing datasets...")
    index_datasets(srch.items())
    logging.info("And we're done!")


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    logger.info("Starting the index process")
    index()


