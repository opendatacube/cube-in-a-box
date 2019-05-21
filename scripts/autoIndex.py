#!/usr/bin/env python3
import ogr
import os
import subprocess
import click
import logging
import json
import boto3
import datacube
from urllib.parse import urlparse

from  multiprocessing import Process, current_process, Queue, Manager, cpu_count
from queue import Empty

from ls_public_bucket import _parse_group, make_metadata_doc, get_s3_url, add_dataset


from satstac import Catalog, Collection, Item
from satsearch import Search

STOP_SIGN = "ALL_COMPLETE_END_WORKER"

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


def index_dataset(index, s3, url, parse_only):
    logger.info("Downloading {}".format(url))
    bucket_name, key = parse_s3_url(url)
    obj = s3.Object(bucket_name, key).get(ResponseCacheControl='no-cache')
    raw = obj['Body'].read()
    raw_string = raw.decode('utf8')
    logger.info("Parsing {}".format(key))
    try:
        txt_doc = _parse_group(iter(raw_string.split("\n")))['L1_METADATA_FILE']
        data = make_metadata_doc(txt_doc, bucket_name, key)
    except Exception as e:
        logger.error("Metadata parsing error: {}; {}".format(e.__class__.__name__, e))
        return
    uri = get_s3_url(bucket_name, key)
    cdt = data['creation_dt']
    if parse_only:
        logger.info("Skipping indexing step")
    else:
        logger.info("Indexing {}".format(key))
        add_dataset(data, uri, index, "verify")


def index_datasets(items, parse_only=False):
    s3 = boto3.resource("s3")
    dc = datacube.Datacube()
    idx = dc.index
    for item in items:
        if "MTL" in item.assets:
            index_dataset(idx, s3, item.assets["MTL"]["href"], parse_only)
        else:
            logger.info("Item {} does not have an MTL asset (Sentinel2?) - skipping".format(item))


def worker(parse_only, queue):
    s3 = boto3.resource("s3")
    dc = datacube.Datacube()
    idx = dc.index

    while True:
        try:
            url = queue.get(timeout=60)
            if url == STOP_SIGN:
                break
            logging.info("Processing {} {}".format(url, current_process()))
            index_dataset(idx, s3, url, parse_only)
            queue.task_done()
        except Empty:
            break
        except EOFError:
            break


def index_datasets_multi(items, parse_only=False):
    manager = Manager()
    queue = manager.Queue()
    worker_count = cpu_count() * 2
    
    processes = []
    for i in range(worker_count):
        proc = Process(target=worker, args=[parse_only, queue])
        processes.append(proc)
        proc.start()

    for item in items:
        if "MTL" in item.assets:
            queue.put(item.assets["MTL"]["href"])
        else:
            logger.info("Item {} does not have an MTL asset (Sentinel2?) - skipping".format(item))

    for i in range(worker_count):
        queue.put(STOP_SIGN)

    for proc in processes:
        proc.join()
    

def parse_s3_url(url):
    o = urlparse(url)
    if o.netloc.startswith("s3"):
        # https://s3-{region}.amazonaws.com/{bucket-name}/{key}
        bucket_name, key = o.path.split("/", 2)[1:]
    else:
        # https://{bucket-name}.s3.amazonaws.com/{key}
        bucket_name = o.netloc.split(".")[0]
        key = o.path.split("/",1)[1]
    return bucket_name, key


# Probably should use Click like the other scripts? -agl
@click.command()
@click.option('--extents', '-e', default="146.30,146.83,-43.54,-43.20", help="Extent to index in the form lon_min,lon_max,lat_min,latmax")
# @click.option('--pathrow_file', '-p', default="/opt/odc/data/wrs2_descending.zip", help="Absolute path to the pathrow file, e.g., /tmp/example.zip")
@click.option('--start_date', default="2013-02-11", help="Start date of the acquisitions to index, in YYYY-MM-DD format (UTC)")
@click.option('--end_date', default="2099-12-31", help="End date of the acquisitions to index, in YYYY-MM-DD format (UTC)")
@click.option('--single_process_only', is_flag=True, help="If true, multi-processing is disabled")
@click.option('--parse_only', '-p', is_flag=True, help="If true, scan STAC and parse MTL files, but do not index into datacube")
def index(extents, start_date, end_date, single_process_only, parse_only, write_extents=True):
    lon_min, lon_max, lat_min, lat_max = map(float, extents.split(','))

    if write_extents and not parse_only:
        with open('/opt/odc/data/configIndex.txt', 'w') as outfile:
            json.dump({'extent': [lon_min, lon_max, lat_min, lat_max]}, outfile)

    srch = stac_search([lon_min, lat_min, lon_max, lat_max], start_date, end_date)
    if not srch:
        logging.error("STAC search failed, stopping.")
        return
    logging.info("Indexing datasets...")
    if single_process_only:
        index_datasets(srch.items(), parse_only)
    else:
        index_datasets_multi(srch.items(), parse_only)
    logging.info("And we're done!")


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    logger.info("Starting the index process")
    index()


