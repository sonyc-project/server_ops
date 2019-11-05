import os
import argparse
from glob import iglob
import time
import shutil


parser = argparse.ArgumentParser(description='Move ingested data from cache to NFS storage')

parser.add_argument('--cache_folder', required=True, type=str, help='Cache folder to watch (absolute path)')
parser.add_argument('--out_folder', required=True, type=str, help='Out folder on NFS (absolute path)')

args = parser.parse_args()


def move_file(src_full_path, dst_dir_path, dst_full_path):
    os.makedirs(dst_dir_path, exist_ok=True)
    if not os.path.isfile(dst_full_path):
        shutil.move(src_full_path, dst_full_path)
    else:
        if os.path.getsize(src_full_path) > os.path.getsize(dst_full_path):
            shutil.move(src_full_path, dst_full_path)
        else:
            os.remove(src_full_path)


def file_move_loop(cache_folder, out_folder):
    for fullpath in iglob(os.path.join(cache_folder, '**'), recursive=True):
        if os.path.isfile(fullpath):
            filename = os.path.basename(fullpath)
            pathparts = os.path.normpath(fullpath).split(os.path.sep)

            if 'test' in pathparts[-5]:
                outdir = os.path.join(out_folder, *pathparts[-5:-1])
                outpath = os.path.join(outdir, filename)

                move_file(fullpath, outdir, outpath)

            else:
                outdir = os.path.join(out_folder, *pathparts[-4:-1])
                outpath = os.path.join(outdir, filename)

                move_file(fullpath, outdir, outpath)


if __name__ == "__main__":
    while True:
        file_move_loop(args.cache_folder, args.out_folder)
        time.sleep(1)
