#!/usr/bin/env python3

# coding: utf-8
from xml.etree import ElementTree
from pathlib import Path
import os
from osgeo import osr
import dateutil
from dateutil import parser
from datetime import timedelta
import uuid
import yaml
import logging
import click
import re
import boto3
import datacube
from datacube.index.hl import Doc2Dataset
from datacube.utils import changes
from ruamel.yaml import YAML
import json

from multiprocessing import Process, current_process, Queue, Manager, cpu_count
from time import sleep, time
from queue import Empty

GUARDIAN = "GUARDIAN_QUEUE_EMPTY"
AWS_PDS_TXT_SUFFIX = "MTL.txt"
LANDSAT_XML_SUFFIX = 'T1.xml'
GENERAL_LANDSAT_XML_SUFFIX = '.xml'

MTL_PAIRS_RE = re.compile(r'(\w+)\s=\s(.*)')

bands_ls8 = [
    ('1', 'coastal_aerosol'),
    ('2', 'blue'),
    ('3', 'green'),
    ('4', 'red'),
    ('5', 'nir'),
    ('6', 'swir1'),
    ('7', 'swir2'),
    ('8', 'panchromatic'),
    ('9', 'cirrus'),
    ('10', 'lwir1'),
    ('11', 'lwir2'),
    ('QUALITY', 'quality')
]

bands_ls7 = [
    ('1', 'blue'),
    ('2', 'green'),
    ('3', 'red'),
    ('4', 'nir'),
    ('5', 'swir1'),
    ('7', 'swir2'),
    ('QUALITY', 'quality')
]

bands_ls57_usard = [
    ('1', 'blue'),
    ('2', 'green'),
    ('3', 'red'),
    ('4', 'nir'),
    ('5', 'swir1'),
    ('6', 'swir2'),
    ('7', 'sr_atmos_opacity'),
    ('8', 'pixel_qa'),
    ('9', 'radsat_qa'),
    ('10', 'sr_cloud_qa')
]

bands_ls8_usard = [
    ('1', 'coastal_aerosol'),
    ('2', 'blue'),
    ('3', 'green'),
    ('4', 'red'),
    ('5', 'nir'),
    ('6', 'swir1'),
    ('7', 'swir2'),
    ('8', 'pixel_qa'),
    ('9', 'sr_aerosol'),
    ('10', 'radsat_qa')
]

band_file_map_l57 = {
    'blue': 'sr_band1',
    'green': 'sr_band2',
    'red': 'sr_band3',
    'nir': 'sr_band4',
    'swir1': 'sr_band5',
    'swir2': 'sr_band7',
    'pixel_qa': 'pixel_qa',
    'radsat_qa': 'radsat_qa',
    'sr_cloud_qa': 'sr_cloud_qa',
    'sr_atmos_opacity': 'sr_atmos_opacity'
}

band_file_map_l8 = {
    'coastal_aerosol': 'sr_band1',
    'blue': 'sr_band2',
    'green': 'sr_band3',
    'red': 'sr_band4',
    'nir': 'sr_band5',
    'swir1': 'sr_band6',
    'swir2': 'sr_band7',
    'pixel_qa': 'pixel_qa',
    'radsat_qa': 'radsat_qa',
    'sr_aerosol': 'sr_aerosol'
}


def _parse_value(s):
    s = s.strip('"')
    for parser in [int, float]:
        try:
            return parser(s)
        except ValueError:
            pass
    return s


def _parse_group(lines):
    tree = {}
    for line in lines:
        match = MTL_PAIRS_RE.findall(line)
        if match:
            key, value = match[0]
            if key == 'GROUP':
                tree[value] = _parse_group(lines)
            elif key == 'END_GROUP':
                break
            else:
                tree[key] = _parse_value(value)
    return tree


def get_band_filenames(xmldoc):
    """ parse the xml metadata and return the band names in a dict """
    band_dict = {}
    bands = xmldoc.find('.//bands')
    for bandxml in bands:
        band_name = (bandxml.get('name'))
        file = bandxml.find('.//file_name')
        band_file_name = file.text
        band_dict[band_name] = band_file_name
    return (band_dict)


def get_geo_ref_points(info):
    return {
        'ul': {'x': info['CORNER_UL_PROJECTION_X_PRODUCT'], 'y': info['CORNER_UL_PROJECTION_Y_PRODUCT']},
        'ur': {'x': info['CORNER_UR_PROJECTION_X_PRODUCT'], 'y': info['CORNER_UR_PROJECTION_Y_PRODUCT']},
        'll': {'x': info['CORNER_LL_PROJECTION_X_PRODUCT'], 'y': info['CORNER_LL_PROJECTION_Y_PRODUCT']},
        'lr': {'x': info['CORNER_LR_PROJECTION_X_PRODUCT'], 'y': info['CORNER_LR_PROJECTION_Y_PRODUCT']},
    }


def get_coords(geo_ref_points, spatial_ref):
    t = osr.CoordinateTransformation(spatial_ref, spatial_ref.CloneGeogCS())

    def transform(p):
        lon, lat, z = t.TransformPoint(p['x'], p['y'])
        return {'lon': lon, 'lat': lat}

    return {key: transform(p) for key, p in geo_ref_points.items()}


def satellite_ref(sat):
    """
    To load the band_names for referencing either LANDSAT8 or LANDSAT7 bands
    """
    if sat == 'LANDSAT_8':
        sat_img = bands_ls8
    elif sat in ('LANDSAT_7', 'LANDSAT_5'):
        sat_img = bands_ls7
    elif sat in ('USGS/EROS/LANDSAT_7', 'USGS/EROS/LANDSAT_5'):
        # logging.info("We're working with the USGS supplied landsat 5 or 7.")
        sat_img = bands_ls57_usard
    elif sat == 'USGS/EROS/LANDSAT_8':
        # logging.info("We're working with the USGS supplied landsat 8.")
        sat_img = bands_ls8_usard
    else:
        raise ValueError('Satellite data Not Supported')
    return sat_img


def absolutify_paths(doc, bucket_name, obj_key):
    objt_key = format_obj_key(obj_key)
    for band in doc['image']['bands'].values():
        band['path'] = get_s3_url(bucket_name, objt_key + '/'+band['path'])
    return doc


def make_xml_doc(xmlstring, bucket_name, object_key):
    """ principle function to convert xml metadata into a JSON doc 
        need to document each section here...
    """

    xmlstring = re.sub(r'\sxmlns="[^"]+"', '', xmlstring, count=1)
    doc = ElementTree.fromstring(xmlstring)

    satellite = doc.find('.//satellite').text
    data_provider = doc.find('.//data_provider').text
    instrument = doc.find('.//instrument').text
    path = doc.find('.//wrs').attrib['path']
    row = doc.find('.//wrs').attrib['row']
    region_code = f"{int(path):03d}{int(row):03d}"

    # other params like cloud_shadow, snow_ice, tile_grid, orientation_angle are also available

    acquisition_date = doc.find('.//acquisition_date').text
    scene_center_time = doc.find('.//scene_center_time').text
    center_dt = acquisition_date + " " + scene_center_time
    level = doc.find('.//product_id').text.split('_')[1]
    start_time = center_dt
    end_time = center_dt

    satellite_string = "{}/{}".format(data_provider, satellite)
    images = satellite_ref(satellite_string)
    if satellite_string == 'USGS/EROS/LANDSAT_8':
        band_file_map = band_file_map_l8
    else:
        band_file_map = band_file_map_l57
    
    logging.info("Working on data for satellite: {}".format(satellite_string))

    # cs_code = '5072'
    utm_zone = doc.find('.//projection_information/utm_proj_params/zone_code').text
    spatial_ref = 'epsg:326' + utm_zone
    west = doc.find('.//bounding_coordinates/west').text
    east = doc.find('.//bounding_coordinates/east').text
    north = doc.find('.//bounding_coordinates/north').text
    south = doc.find('.//bounding_coordinates/south').text

    if float(west) < -179:
        west = str(float(west) + 360)

    if float(east) < -179:
        east = str(float(east) + 360)

    coord = {
          'ul':
             {'lon': west,
              'lat': north},
          'ur':
             {'lon': east,
              'lat': north},
          'lr':
             {'lon': east,
              'lat': south},
          'll':
             {'lon': west,
              'lat': south}}

    projection_parameters = doc.find('.//projection_information')
    for corner_point in projection_parameters.findall('corner_point'):
        if corner_point.attrib['location'] in 'UL':
           westx = corner_point.attrib['x']
           northy = corner_point.attrib['y']
        if corner_point.attrib['location'] in 'LR':
           eastx = corner_point.attrib['x']
           southy = corner_point.attrib['y']

    westxf = float(westx) * 1.0
    eastxf = float(eastx) * 1.0
    northyf = float(northy) * 1.0
    southyf = float(southy) * 1.0

    geo_ref_points = {
          'ul':
             {'x': westxf,
              'y': northyf},
          'ur':
             {'x': eastxf,
              'y': northyf},
          'lr':
             {'x': eastxf,
              'y': southyf},
          'll':
             {'x': westxf,
              'y': southyf}}

    band_dict =  get_band_filenames(doc)
    try:
        docdict = {
            'id': str(uuid.uuid5(uuid.NAMESPACE_URL, get_s3_url(bucket_name, object_key))),
            # 'cloud_cover': cloud_cover,
            # 'fill': fill,
            'processing_level': str(level),
            # This is hardcoded now... needs to be not hardcoded!
            'product_type': 'LEVEL2_USGS',
            'creation_dt': acquisition_date,
            'region_code': region_code,
            'platform': {'code': satellite},
            'instrument': {'name': instrument},
            'extent': {
                'from_dt': str(start_time),
                'to_dt': str(end_time),
                'center_dt': str(center_dt),
                'coord': coord,
            },
            'format': {'name': 'GeoTiff'},
            'grid_spatial': {
                'projection': {
                    'geo_ref_points': geo_ref_points,
                    'spatial_reference': spatial_ref,
                }
            },
            'image': {
                'bands': {
                    image[1]: {
                        'path': band_dict[band_file_map[image[1]]],
                        'layer': 1,
                    } for image in images
                }
            },

            'lineage': {'source_datasets': {}}
        }
    except KeyError as e:
        logging.error("Failed to handle metadata file: {} with error: {}".format(object_key, e))
        return None
    docdict = absolutify_paths(docdict, bucket_name, object_key)

    logging.info("Prepared docdict for metadata file: {}".format(object_key))
    # print(json.dumps(docdict, indent=2))

    return docdict



def make_metadata_doc(mtl_data, bucket_name, object_key):
    mtl_product_info = mtl_data['PRODUCT_METADATA']
    mtl_metadata_info = mtl_data['METADATA_FILE_INFO']
    satellite = mtl_product_info['SPACECRAFT_ID']
    instrument = mtl_product_info['SENSOR_ID']
    acquisition_date = mtl_product_info['DATE_ACQUIRED']
    scene_center_time = mtl_product_info['SCENE_CENTER_TIME']
    level = mtl_product_info['DATA_TYPE']
    product_type = 'L1TP'
    sensing_time = acquisition_date + ' ' + scene_center_time
    cs_code = 32600 + mtl_data['PROJECTION_PARAMETERS']['UTM_ZONE']
    label = mtl_metadata_info['LANDSAT_SCENE_ID']
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(cs_code)
    geo_ref_points = get_geo_ref_points(mtl_product_info)
    coordinates = get_coords(geo_ref_points, spatial_ref)
    bands = satellite_ref(satellite)
    doc = {
        'id': str(uuid.uuid5(uuid.NAMESPACE_URL, get_s3_url(bucket_name, object_key))),
        'processing_level': level,
        'product_type': product_type,
        'creation_dt': str(acquisition_date),
        'label': label,
        'platform': {'code': satellite},
        'instrument': {'name': instrument},
        'extent': {
            'from_dt': sensing_time,
            'to_dt': sensing_time,
            'center_dt': sensing_time,
            'coord': coordinates,
                  },
        'format': {'name': 'GeoTiff'},
        'grid_spatial': {
            'projection': {
                'geo_ref_points': geo_ref_points,
                'spatial_reference': 'EPSG:%s' % cs_code,
                            }
                        },
        'image': {
            'bands': {
                band[1]: {
                    'path': mtl_product_info['FILE_NAME_BAND_' + band[0]],
                    'layer': 1,
                } for band in bands
            }
        },
        'lineage': {'source_datasets': {}},
    }
    doc = absolutify_paths(doc, bucket_name, object_key)
    return doc


def format_obj_key(obj_key):
    obj_key ='/'.join(obj_key.split("/")[:-1])
    return obj_key


def get_s3_url(bucket_name, obj_key):
    return 's3://{bucket_name}/{obj_key}'.format(
        bucket_name=bucket_name, obj_key=obj_key)


def archive_document(doc, uri, index, sources_policy):
    def get_ids(dataset):
        ds = index.datasets.get(dataset.id, include_sources=True)
        for source in ds.sources.values():
            yield source.id
        yield dataset.id

    resolver = Doc2Dataset(index)
    dataset, err = resolver(doc, uri)
    index.datasets.archive(get_ids(dataset))
    logging.info("Archiving %s and all sources of %s", dataset.id, dataset.id)


def add_dataset(doc, uri, index, sources_policy):
    logging.info("Indexing dataset: {} with URI:  {}".format(doc['id'], uri))

    resolver = Doc2Dataset(index)
    dataset, err  = resolver(doc, uri)
    existing_dataset = index.datasets.get(doc['id'])

    if not existing_dataset:
        logging.info("Trying to index")
        if err is not None:
            logging.error("%s", err)
        else:
            try:
                index.datasets.add(dataset, with_lineage=False) # Source policy to be checked in sentinel 2 dataset types
            except Exception as e:
                logging.error("Unhandled exception %s", e)
    else:
        logging.info("Updating dataset instead.")
        try:
            index.datasets.update(dataset, {tuple(): changes.allow_any})
        except Exception as e:
            logging.error("Unhandled exception %s", e)

    return dataset, err

def worker(config, bucket_name, prefix, suffix, start_date, end_date, func, unsafe, sources_policy, queue):
    dc=datacube.Datacube(config=config)
    index = dc.index
    s3 = boto3.resource("s3")
    safety = 'safe' if not unsafe else 'unsafe'

    while True:
        try:
            key = queue.get(timeout=60)
            if key == GUARDIAN:
                break
            logging.info("Processing %s %s", key, current_process())
            obj = s3.Object(bucket_name, key).get(ResponseCacheControl='no-cache')
            raw = obj['Body'].read()
            raw_string = raw.decode('utf8')

            if suffix == AWS_PDS_TXT_SUFFIX:
                # Attempt to process text document
                txt_doc = _parse_group(iter(raw_string.split("\n")))['L1_METADATA_FILE']
                data = make_metadata_doc(txt_doc, bucket_name, key)
            elif suffix == LANDSAT_XML_SUFFIX or suffix == GENERAL_LANDSAT_XML_SUFFIX:
                data = make_xml_doc(raw_string, bucket_name, key)
            else:
                yaml = YAML(typ=safety, pure=False)
                yaml.default_flow_style = False
                data = yaml.load(raw)
            if data:
                uri = get_s3_url(bucket_name, key)
                cdt = data['creation_dt']

                # Only do the date check if we have dates set
                if cdt and start_date and cdt:
                    # Use the fact lexicographical ordering matches the chronological ordering
                    if cdt >= start_date and cdt < end_date:
                        # logging.info("calling %s", func)
                        func(data, uri, index, sources_policy)
                else:
                    func(data, uri, index, sources_policy)
            else:
                logging.error("Failed to get data returned... skipping file.")
        except Empty:
            logging.error("Empty exception hit.")
            break
        except EOFError:
            logging.error("EOF Error hit.")
            break
        except ValueError as e:
            logging.error("Found data for a satellite that we can't handle: {}".format(e))
        finally:
            queue.task_done()


def iterate_datasets(bucket_name, config, prefix, suffix, start_date, end_date, func, unsafe, sources_policy):
    logging.info("Starting iterate datasets.")
    manager = Manager()
    queue = manager.Queue()

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    logging.info("Bucket : %s prefix: %s ", bucket_name, str(prefix))
    # safety = 'safe' if not unsafe else 'unsafe'
    worker_count = cpu_count() * 2

    processess = []
    for i in range(worker_count):
        proc = Process(target=worker, args=(config, bucket_name, prefix, suffix, start_date, end_date, func, unsafe, sources_policy, queue,))
        processess.append(proc)
        proc.start()

    count = 0
    for obj in bucket.objects.filter(Prefix = str(prefix)):
        if (obj.key.endswith(suffix)):
            count += 1
            queue.put(obj.key)
    
    logging.info("Found {} items to investigate".format(count))

    for i in range(worker_count):
        queue.put(GUARDIAN)

    for proc in processess:
        proc.join()


@click.command(help= "Enter Bucket name. Optional to enter configuration file to access a different database")
@click.argument('bucket_name')
@click.option('--config','-c',help="Pass the configuration file to access the database",
        type=click.Path(exists=True))
@click.option('--prefix', '-p', help="Pass the prefix of the object to the bucket")
@click.option('--suffix', '-s', default=".yaml", help="Defines the suffix of the metadata_docs that will be used to load datasets. For AWS PDS bucket use MTL.txt")
@click.option('--start_date', help="Pass the start acquisition date, in YYYY-MM-DD format")
@click.option('--end_date', help="Pass the end acquisition date, in YYYY-MM-DD format")
@click.option('--archive', is_flag=True, help="If true, datasets found in the specified bucket and prefix will be archived")
@click.option('--unsafe', is_flag=True, help="If true, YAML will be parsed unsafely. Only use on trusted datasets. Only valid if suffix is yaml")
@click.option('--sources_policy', default="verify", help="verify, ensure, skip")
def main(bucket_name, config, prefix, suffix, start_date, end_date, archive, unsafe, sources_policy):
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    action = archive_document if archive else add_dataset
    iterate_datasets(bucket_name, config, prefix, suffix, start_date, end_date, action, unsafe, sources_policy)
   
if __name__ == "__main__":
    main()
