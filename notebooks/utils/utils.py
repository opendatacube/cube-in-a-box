# Utils
import json
from skimage import exposure
import numpy as np
import osr
import ogr


def lat_lon_to_epsg(lat_max, lon_min):
    return str(int(32700 - round((45 + lat_max) / 90, 0) * 100 + round((183 + lon_min) / 6, 0)))


def three_band_image(ds, bands, time=0, figsize=[10, 10], projection='projected'):
    '''
    three_band_image takes three spectral bands and plots them on the RGB bands of an image.

    Inputs:
    ds -   Dataset containing the bands to be plotted
    bands - list of three bands to be plotted

    Optional:
    time - Index value of the time dimension of ds to be plotted
    figsize - dimensions for the output figure
    projection - options are 'projected' or 'geographic'. To determine if the image is in degrees or northings
    '''
    t, y, x = ds[bands[0]].shape
    rawimg = np.zeros((y, x, 3), dtype=np.float32)
    for i, colour in enumerate(bands):
        rawimg[:, :, i] = ds[colour][time].values
    rawimg[rawimg == -9999] = np.nan
    img_toshow = exposure.equalize_hist(rawimg, mask=np.isfinite(rawimg))

    return img_toshow


def load_config_extents(file):
    config = json.load(open(file))
    lon_min, lon_max, lat_min, lat_max = config['extent']
    rectangle = [
        [lat_max, lon_min],
        [lat_max, lon_max],
        [lat_min, lon_max],
        [lat_min, lon_min],
        [lat_max, lon_min]]
    return [[lon_min, lon_max, lat_min, lat_max], rectangle]


def transform_to_wgs(getLong, getLat, EPSGa):
    source = osr.SpatialReference()
    source.ImportFromEPSG(EPSGa)

    target = osr.SpatialReference()
    target.ImportFromEPSG(4326)

    transform = osr.CoordinateTransformation(source, target)

    point = ogr.CreateGeometryFromWkt("POINT (" + str(getLong[0]) + " " + str(getLat[0]) + ")")
    point.Transform(transform)
    return [point.GetX(), point.GetY()]
