import os
import time
import shutil
import tarfile
import argparse
from glob import iglob

parser = argparse.ArgumentParser(description='Create day tars after no activity of XXhrs')

parser.add_argument('--data_folder', required=True, type=str, help='Data folder location')
parser.add_argument('--time_since_dir_mod', required=True, type=float, help='Time since directory update in hours')

args = parser.parse_args()


def add_to_tarfile(tar_path, dir_path):
    for filepath in iglob(os.path.join(dir_path, '*')):
        with tarfile.open(tar_path, 'a') as tar:
            filename = os.path.basename(filepath)
            if filename not in tar.getnames():
                tar.add(filepath, arcname=os.path.basename(filepath))
            else:
                if os.path.getsize(filepath) > tar.getmember(filename).size:
                    tar.add(filepath, arcname=os.path.basename(filepath))


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, 'w') as tar:
        tar.add(source_dir, arcname='')


def remove_files(tar_path, dir_path, time_since_dir_mod):
    last_mod = os.path.getmtime(dir_path)
    dir_time_since_mod_hrs = (time.time() - last_mod) / 3600.0
    if dir_time_since_mod_hrs > time_since_dir_mod:
        tar = tarfile.open(tar_path)
        tar.close()
        shutil.rmtree(dir_path)


def check_folder_last_write(data_folder, time_since_dir_mod):

    for fullpath in iglob(os.path.join(data_folder, '*/*/*/*/'), recursive=True):
        print(fullpath)
        last_mod = os.path.getmtime(fullpath)
        dir_time_since_mod_hrs = (time.time() - last_mod) / 3600.0
        tar_path = fullpath.rstrip('/') + '.tar'
        if dir_time_since_mod_hrs > time_since_dir_mod and os.path.isdir(fullpath) and not os.path.isfile(tar_path):
            make_tarfile(tar_path, fullpath)
            remove_files(tar_path, fullpath, time_since_dir_mod)
        elif os.path.isfile(tar_path) and os.path.isdir(fullpath):
            add_to_tarfile(tar_path, fullpath)
            remove_files(tar_path, fullpath, time_since_dir_mod)


if __name__ == '__main__':
    check_folder_last_write(args.data_folder, args.time_since_dir_mod)
