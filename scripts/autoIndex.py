#!/usr/bin/env python3
import ogr
import os
import subprocess
import click
import logging
import json

logger = logging.getLogger('odcindexer')

def convert_ll_to_pr(extent, ascending, path):
    """ Convert lat, lon to pathrows """
    logger.info("Starting the conversion from ll to pathrow for area: {}".format(extent))
    driver = ogr.GetDriverByName('ESRI Shapefile')
    file_path = '/vsizip/' + path 
    dataSource = driver.Open(file_path, 0) # 0 means read-only. 1 means writeable.
    if not dataSource:
        logger.error("Failed to open the file: {}".format(file_path))
        return
    layer = dataSource.GetLayer()

    ring = ogr.Geometry(ogr.wkbLinearRing)
    # Stupid geometry is lat, lon instead of lon, lat...
    ring.AddPoint(extent[0], extent[2])
    ring.AddPoint(extent[0], extent[3])
    ring.AddPoint(extent[1], extent[3])
    ring.AddPoint(extent[1], extent[2])
    ring.AddPoint(extent[0], extent[2])
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)

    logging.info("Usion bbox filter: {}".format(poly.ExportToJson()))
    layer.SetSpatialFilter(poly)

    if not ascending:
        layer.SetAttributeFilter("MODE = 'A'")
    else:
        layer.SetAttributeFilter("MODE = 'D'")


    logging.info("Found {} features.".format(layer.GetFeatureCount()))
    pathRows = []
    for pInfo in layer:
        pathRows.append([pInfo.GetField('PATH'), pInfo.GetField('ROW')])

    return pathRows

# Probably should use Click like the other scripts? -agl
@click.command()
@click.option('--extents', '-e', default="146.30,146.83,-43.54,-43.20", help="Extent to index in the form lon_min,lon_max,lat_min,latmax")
@click.option('--pathrow_file', '-p', default="/opt/odc/data/wrs2_descending.zip", help="Absolute path to the pathrow file, e.g., /tmp/example.zip")
@click.option('--start_date', default="2013-02-11", help="Start date of the acquisitions to index, in YYYY-MM-DD format")
@click.option('--end_date', default="2099-12-31", help="End date of the acquisitions to index, in YYYY-MM-DD format")
def index(extents, pathrow_file, start_date, end_date, write_extents=True):
    lon_min, lon_max, lat_min, lat_max = map(float, extents.split(','))

    if write_extents:
        with open('/opt/odc/data/configIndex.txt', 'w') as outfile:
            json.dump({'extent': [lon_min, lon_max, lat_min, lat_max]}, outfile)

    pathRows = convert_ll_to_pr([lon_min, lon_max, lat_min, lat_max], True, pathrow_file)
    if not pathRows:
        logging.error("Couldn't find pathrows, stopping.")
        return
    logging.info("Found {} pathrows to handle".format((len(pathRows))))
    for pathRow in pathRows:
        logging.info("Loading pathrows")
        print(pathRow)
        os.system('python3 ./ls_public_bucket.py landsat-pds -p c1/L8/' + "%03d" % (pathRow[0],) + '/' + "%03d" % (pathRow[1],) + '/ --suffix="MTL.txt"' + ' --start_date %s' % start_date + ' --end_date %s' % end_date)

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    logger.info("Starting the index process")
    index()
