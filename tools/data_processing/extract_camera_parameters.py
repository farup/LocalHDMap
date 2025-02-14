import numpy as np 
import cv2 
import json
import os
import sys


from PIL import Image
# import geopandas as gpd
# import matplotlib.pyplot as plt
# import contextily as ctx
# from shapely.geometry import Point



save_path_nuscnes_metadata = "/cluster/home/terjenf/NAPLab_car/data_nuscnes"
version = 'v1.0-trainval'
saved_nusce_file = 'nuscene_metadata.json'

sys.path.append("/cluster/home/terjenf/")

from NAPLab_car.tools.data_processing import utils
from NAPLab_car.tools.data_processing import extract_camera_intrinsics

def get_nuscenes_cam_intrinics(): 
    from nuscenes.nuscenes import NuScenes
    nusc = NuScenes(version=version, dataroot=root_path, verbose=True)

    cam_intrinsics = []
    image_size = []

    nuscene_info = {}
    sample = nusc.sample[0]
    lidar_token = sample['data']['LIDAR_TOP']
    sd_rec = nusc.get('sample_data', sample['data']['LIDAR_TOP'])

    camera_types = [
            'CAM_FRONT',
            'CAM_FRONT_RIGHT',
            'CAM_FRONT_LEFT',
            'CAM_BACK',
            'CAM_BACK_LEFT',
            'CAM_BACK_RIGHT',
    ]

    for cam in camera_types:
            cam_token = sample['data'][cam]
            sd_rec = nusc.get('sample_data', cam_token)
            cs_record = nusc.get('calibrated_sensor', sd_rec['calibrated_sensor_token']) 
            cam_intrin = cs_record['camera_intrinsic']
            img_fpath=str(nusc.get_sample_data_path(sd_rec['token']))
            shape = np.asarray(Image.open(img_fpath)).shape


            nuscene_info[cam] = {'camera_intrinsic': cam_intrin, 'img_size': shape}

    with open(os.path.join(save_path_nuscnes_metadata,saved_nusce_file), 'w') as f: 
        json.dump(nuscene_info, f, indent=4)
           
    return nuscene_info
        

def get_naplab_cams(calibrated_sesnsor_file, selected_cams=False): 
    with open(calibrated_sesnsor_file, 'r') as file:
        json_obj = json.load(file)

        cam_data = {}
        roll_pitch_yaw = []
        t = []
        properties = []

        for car_mask in json_obj['rig']['sensors']: 
            try: 
                if 'car-mask' not in car_mask.keys():
                    continue
                
                if selected_cams:
                    if car_mask['name'] not in selected_cams:
                        continue

                nominalSensor2Rig_FLU = car_mask['nominalSensor2Rig_FLU']
            
                roll_pitch_yaw = nominalSensor2Rig_FLU['roll-pitch-yaw']
                t = nominalSensor2Rig_FLU['t']
                properties = car_mask['properties']

                cx = float(properties['cx'])
                cy = float(properties['cy'])

                height = int(properties['height'])
                width = int(properties['width'])

                bw_poly = (properties['bw-poly']).split(" ")
                float_bw = [float(num) for num in bw_poly if len(num) > 2]


                fw_coeff = extract_camera_intrinsics.calculate_fw_coef(width, height, cx, cy, float_bw)

                cam_data[car_mask['name']] = {'roll_pitch_yaw': roll_pitch_yaw, 't':t, 'cx': cx, 'cy': cy, 'height': height, 'width': width, 'bw_coeff': float_bw, 'fw_coeff': fw_coeff}

            except KeyError as e:
                print("Error", e)
                print(car_mask)

    return cam_data


if __name__ == "__main__": 

    # cam_intrinsics, image_size = get_nuscenes_cam_intrinics()
    root_folder = "/cluster/home/terjenf/MapTR/NAP_raw_data/"

    absoulute_files = utils.get_folder(root_folder=root_folder, folder_name="Trip077")

    calibrated_sensor_file = utils.get_files(absoulute_files, file_format="json")
    

    cam_data = get_naplab_cams(calibrated_sensor_file[0])

 





