##Utils
import folium
import json
from rasterio.plot import show_hist
from datacube.storage import masking
from datacube import Datacube
from datetime import datetime
from skimage import exposure
import numpy as np


def threeBandImage(ds, bands, time = 0, figsize = [10,10], projection = 'projected'):
    '''
    threeBandImage takes three spectral bands and plots them on the RGB bands of an image. 
    
    Inputs: 
    ds -   Dataset containing the bands to be plotted
    bands - list of three bands to be plotted
    
    Optional:
    time - Index value of the time dimension of ds to be plotted
    figsize - dimensions for the output figure
    projection - options are 'projected' or 'geographic'. To determine if the image is in degrees or northings
    '''
    t, y, x = ds[bands[0]].shape
    rawimg = np.zeros((y,x,3), dtype = np.float32)
    for i, colour in enumerate(bands):
        rawimg[:,:,i] = ds[colour][time].values
    rawimg[rawimg == -9999] = np.nan
    img_toshow = exposure.equalize_hist(rawimg, mask = np.isfinite(rawimg))

    return img_toshow

def loadConfigExtent():
    config = json.load(open('/opt/odc/data/configIndex.txt'))
    lon_min, lon_max, lat_min, lat_max = map(float, config['extent'].split(','))
    #centre = [(lat_min+ lat_max)/2,(lon_min + lon_max)/2]
    rectangle =  [[lat_max,lon_min],[lat_max,lon_max], [lat_min,lon_max],[lat_min,lon_min],[lat_max,lon_min]]
    return [[lon_min, lon_max, lat_min, lat_max],rectangle]
    
