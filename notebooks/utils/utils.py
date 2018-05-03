##Utils
import folium
import json
from rasterio.plot import show_hist
from datacube.storage import masking
from datacube import Datacube
from datetime import datetime
from skimage import exposure
import utils.landsat_qa_lookup as lookup_dict
import numpy as np
import osr
import ogr
bit_flags = lookup_dict.bit_flags

def LatLongtoEPSG(lat_max,lon_min):

    return str(int(32700-round((45+lat_max)/90,0)*100+round((183+lon_min)/6,0)))

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
    config = json.load(open('/opt/odc/data/extents.txt'))
    lon_min, lon_max, lat_min, lat_max = config['extent']
    #centre = [(lat_min+ lat_max)/2,(lon_min + lon_max)/2]
    rectangle =  [[lat_max,lon_min],[lat_max,lon_max], [lat_min,lon_max],[lat_min,lon_min],[lat_max,lon_min]]
    return [[lon_min, lon_max, lat_min, lat_max], rectangle]


def transformToWGS(getLong, getLat, EPSGa):
    source = osr.SpatialReference()
    source.ImportFromEPSG(EPSGa)

    target = osr.SpatialReference()
    target.ImportFromEPSG(4326)

    transform = osr.CoordinateTransformation(source, target)

    point = ogr.CreateGeometryFromWkt("POINT (" + str(getLong[0]) + " " + str(getLat[0]) + ")")
    point.Transform(transform)
    return [point.GetX(), point.GetY()]

def decodeQABand(toCheck, sensor = 'L8', band = 'BQA', rm_low = False):

    ###Code has been copied and modified from https://github.com/USGS-EROS/landsat-qa-arcgis-toolbox/blob/master/Scripts/qa_decode.py
    bit_values = sorted(bit_flags[band][sensor].values())
    bit_bool = []
    for bv in bit_values:
        if len(bv) == 1:  # single bit
            bit_bool.append(toCheck & 1 << bv[0] > 0)

        elif len(bv) > 1:  # 2+ bits
            bits = []
            for b in bv:
                bits.append(toCheck & 1 << b > 0)
            if all(item == True for item in bits):
                bit_bool.append(True)
            else:
                bit_bool.append(False)

        else:
            sys.exit("No valid bits found for target band.")

    # create description of each value based upon all possible bits
    true_bits = [i for (i, bb) in zip(bit_values, bit_bool) if bb]

    # if double bits exist, eliminate single bit descriptions,
    #   otherwise, the descriptions will duplicate themselves.
    bb_double = [len(i) > 1 for i in true_bits]
    if any(bb_double):
        # get only the double bits
        dbit_nest = [i for (i, db) in zip(true_bits, bb_double) if db]

        # collapse the bits into a single list
        dbits = [item for sublist in dbit_nest for item in sublist]

        # remove matching single bits out of true_bits list
        tbo = []
        for t in true_bits:
            tb_out = []
            for d in dbits:
                if t[0] != d or len(t) > 1:
                    tb_out.append(True)
                else:
                    tb_out.append(False)
            if all(tb_out):
                tbo.append(t)

        # replace true_bits with filtered list
        true_bits = tbo

    def get_label(bits):
        """
        Generate label for value in attribute table.
        :param bits: <list> List of True or False for bit position
        :return: <str> Attribute label
        """
        if len(bits) == 0:
            if band == 'radsat_qa':
                return 'No Saturation'

            elif band == 'sr_cloud_qa' or band == 'sr_aerosol':
                return 'None'

            elif band == 'BQA':
                return 'Not Determined'

        # build description from all bits represented in value
        desc = []
        for tb in bits:
            k = next(key for key, value in
                     bit_flags[band][sensor].items() if value == tb)

            # if 'low' labels are disabled, do not add them here
            if rm_low and band != 'BQA' and 'low' in k.lower():
                continue

            # if last check, and not radiometric sat, set to 'clear'
            elif rm_low and band == 'BQA' and 'low' in k.lower() and \
                            tb == bits[-1] and \
                            'radiometric' not in k.lower() and \
                    not desc:
                k = 'Clear'

            # if BQA and bit is low radiometric sat, keep it
            elif rm_low and band == 'BQA' and 'low' in k.lower():
                if 'radiometric' not in k.lower():
                    continue

	        # if radsat_qa, handle differently to make display cleaner
            if band == 'radsat_qa':
    	        if not desc:
    	            desc.append("Band {0} Data Saturation".format(tb[0]))

    	        else:
    	            desc.append("{0},{1} Data Saturation".format(
    	                desc[:desc.find('Data') - 1], tb[0]))

	    # string creation for all other bands
            else:
    	        desc.append("{0}".format(k))

        # final check to make sure something was set
        if not desc:
            desc = 'ERROR: bit set incorrectly'

        return desc


    return get_label(true_bits)
