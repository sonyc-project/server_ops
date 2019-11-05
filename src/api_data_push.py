import asyncore
import pyinotify
import argparse
import tarfile
import pandas as pd
import numpy as np
import redis
import time
import settings
import json
import urllib.request

parser = argparse.ArgumentParser(description='SONYC API push script')
parser.add_argument('--folder', type=str, help='Folder to watch (absolute path)')

args = parser.parse_args()

MONITOR_DIR = args.folder

wm = pyinotify.WatchManager()
mask = pyinotify.IN_CLOSE_WRITE

sensor_meta_url = 'https://overview-dashboard.sonycproject.com/status'
meta_ts = 0
node_data = {}

redis_host = 'localhost'
port = 6379
db = 0

r = redis.Redis(host=redis_host, port=port, db=db, password=settings.redis_password)


def calc_leq(data):
    return 10.0 * np.log10(np.mean(10.0 ** (data / 10.0)))


def calc_min(data):
    return np.min(data)


def calc_max(data):
    return np.max(data)


def calc_pcntl(data, pcntl):
    stat_percentile = 100 - pcntl
    return np.nanpercentile(data, stat_percentile)


def get_sensor_meta():
    global meta_ts
    meta_ts = time.time()
    with urllib.request.urlopen(sensor_meta_url) as url:
        node_list = json.loads(url.read().decode())
        for node in node_list:
            if node['life_stage'] == 'Active':
                node_id = node['fqdn'].split('.')[0].split('-')[1]
                node_data[node_id] = {'lat': node['latitude'], 'lon': node['longitude'], 'dateup': node['date_up']}


def insert_data_db(id_str, timefloat, lat, lon, dateup, laeq, maxspl, minspl, l5, l10, l50, l90):
    db_payload = {'time': timefloat, 'lat': lat, 'lon': lon, 'dateup': dateup, 'laeq': round(laeq, 1), 'maxspl': round(maxspl, 1), 'minspl': round(minspl, 1),
                  'l5': round(l5, 1), 'l10': round(l10, 1), 'l50': round(l50, 1), 'l90': round(l90, 1)}

    print(json.dumps(db_payload))
    r.zadd(id_str, {json.dumps(db_payload): int(timefloat)})
    r.zremrangebyrank(id_str, 0, -1440)
    return 0


def tar_worker(tar_path):
    with tarfile.open(tar_path) as tf:
        for member in tf.getmembers():
            if 'slow' in member.name:
                sensor_id = member.name.split('_')[0]
                csv_f = tf.extractfile(member)
                df = pd.read_csv(csv_f)
                dbas_vals = df.dBAS.values
                ts = pd.Timestamp(df.time.values[0], unit='s').tz_localize('UTC').tz_convert('US/Eastern').timestamp()
                # timestr = ts.strftime(format='%Y-%m-%dT%H:%M:%S')
                # timestr = df.time.values[0]
                laeq = calc_leq(dbas_vals)
                maxspl = calc_max(dbas_vals)
                minspl = calc_min(dbas_vals)
                l5 = calc_pcntl(dbas_vals, 5)
                l10 = calc_pcntl(dbas_vals, 10)
                l50 = calc_pcntl(dbas_vals, 50)
                l90 = calc_pcntl(dbas_vals, 90)
                if time.time() - meta_ts > 60 * 5:
                    get_sensor_meta()

                lat = node_data[sensor_id]['lat']
                lng = node_data[sensor_id]['lon']
                dateup = node_data[sensor_id]['dateup']
                insert_data_db(sensor_id, ts, lat, lng, dateup, laeq, maxspl, minspl, l5, l10, l50, l90)


class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        if event.pathname.endswith(".tar"):
            try:
                start = time.time()

                filename = event.pathname
                tar_worker(filename)

                end = time.time()
                print('Execution time: %.2fms' % ((end - start) * 1000))
            except Exception as ex:
                print('---ERROR:', str(ex))
            finally:
                r = redis.Redis(host=redis_host, port=port, db=db)


if __name__ == "__main__":
    notifier = pyinotify.AsyncNotifier(wm, EventHandler())
    wdd = wm.add_watch(MONITOR_DIR, mask, rec=True, auto_add=True)
    print("Monitoring: ", MONITOR_DIR)
    asyncore.loop()