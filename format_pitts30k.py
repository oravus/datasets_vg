
"""
In datasets/pitts30k/raw_data there should be the following files/folders:
000, 001, 002, 003, 004, 005, 006, queries_real, datasets
(datasets is a folder that contains files such as pitts250k_train.mat)
"""

import os
from os.path import realpath
import re
import utm
import shutil
from tqdm import tqdm
from os.path import join
from scipy.io import loadmat

import util
import map_builder

datasets_folder = join(os.curdir, "datasets")
dataset_name = "pitts30k"
dataset_folder = join(datasets_folder, dataset_name)
raw_data_folder = join(datasets_folder, dataset_name, "raw_data")
os.makedirs(dataset_folder, exist_ok=True)
os.makedirs(raw_data_folder, exist_ok=True)

def copy_images(dst_folder, src_images_paths, utms):
    os.makedirs(dst_folder, exist_ok=True)
    for src_image_path, (utm_east, utm_north) in zip(tqdm(src_images_paths, desc=f"Copy to {dst_folder}", ncols=100),
                                                     utms):
        src_image_name = os.path.basename(src_image_path)
        latitude, longitude = utm.to_latlon(utm_east, utm_north, 17, "T")
        pitch = int(re.findall('pitch(\d+)_', src_image_name)[0])-1
        yaw =   int(re.findall('yaw(\d+)\.', src_image_name)[0])-1
        note = re.findall('_(.+)\.jpg', src_image_name)[0]
        tile_num = pitch*24 + yaw
        dst_image_name = util.get_dst_image_name(latitude, longitude, pano_id=src_image_name.split("_")[0],
                                             tile_num=tile_num, note=note)
        src_path = os.path.join(dataset_folder, 'raw_data', src_image_path)
        dst_path = os.path.join(dst_folder, dst_image_name)
        os.symlink(realpath(src_path),realpath(dst_path))
        # shutil.move(src_path, dst_path)


for dataset in ["train", "val", "test"]:
    matlab_struct_file_path = os.path.join(dataset_folder, "raw_data", "datasets", f"pitts30k_{dataset}.mat")
    mat_struct = loadmat(matlab_struct_file_path)["dbStruct"].item()
    # Database
    g_images = [f[0].item() for f in mat_struct[1]]
    g_utms = mat_struct[2].T
    copy_images(os.path.join(dataset_folder, 'images', dataset, 'database'), g_images, g_utms)
    # Queries
    q_images = [os.path.join("queries_real", f"{f[0].item()}") for f in mat_struct[3]]
    q_utms = mat_struct[4].T
    copy_images(os.path.join(dataset_folder, 'images', dataset, 'queries'), q_images, q_utms)

map_builder.build_map_from_dataset(dataset_folder)
# shutil.rmtree(raw_data_folder)
