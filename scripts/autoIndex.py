#!/usr/bin/env python3
import ogr
import os
import click
import logging

logger = logging.getLogger('odcindexer')

def convert_ll_to_pr(extent, ascending, path):
    """ Convert lat, lon to pathrows """
    logger.info("Starting the conversion from ll to pathrow for area: {}".format(extent))
    driver = ogr.GetDriverByName('ESRI Shapefile')
    file_path = '/vsizip/' + path + '/wrs1_asc_desc'
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
    logging.info("Found {} features.".format(layer.GetFeatureCount()))
    if not ascending:
        layer.SetAttributeFilter("MODE_ = 'A'")
    else:
        layer.SetAttributeFilter("MODE_ = 'D'")

    pathRows = []
    for pInfo in layer:
        pathRows.append([pInfo.GetField('PATH'), pInfo.GetField('ROW_')])

    return pathRows

# Probably should use Click like the other scripts? -agl
@click.command()
@click.option('--extents', '-e', default="152.1,153.11,-42.51,-41.5", help="Extent to index in the form lon_min,lon_max,lat_min,latmax")
@click.option('--pathrow_file', '-p', default="/opt/odc/data/wrs1_asc_desc.zip", help="Absolute path to the pathrow file, e.g., /tmp/example.zip")
def index(extents, pathrow_file):
   lon_min, lon_max, lat_min, lat_max = map(float, extents.split(','))

   pathRows = convert_ll_to_pr([lon_min, lon_max, lat_min, lat_max], True, pathrow_file)
   if not pathRows:
       logging.error("Couldn't find pathrows, stopping.")
       return
   logging.info("Found {} pathrows to handle".format((len(pathRows))))
   for pathRow in pathRows:
        os.system('python3 ./ls_public_bucket.py landsat-pds -p c1/L8/' + str(pathRow[0]) + '//' + str(pathRow[0]) + '//')

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    logger.info("Starting the index process")
    index()
