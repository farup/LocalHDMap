import numpy as np 
import cv2 
import json
import os


from PIL import Image
# import geopandas as gpd
# import matplotlib.pyplot as plt
# import contextily as ctx
# from shapely.geometry import Point


root_path = "/cluster/home/terjenf/maptr_new/data/nuscenes"
save_path_nuscnes_metadata = "/cluster/home/terjenf/NAPLab_car/data_nuscnes"
version = 'v1.0-trainval'
saved_nusce_file = 'nuscene_metadata.json'

import utils

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
        

def read_NAP_Lab_camera_prarameters(calibrated_sesnsor_file, selected_cams): 
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

                cam_data[car_mask['name']] = {'roll_pitch_yaw': roll_pitch_yaw, 't':t, 'cx': cx, 'cy': cy, 'height': height, 'width': width, 'float_bw': float_bw}

            except KeyError as e:
                print("Error", e)
                print(car_mask)

    return cam_data


if __name__ == "__main__": 

    # cam_intrinsics, image_size = get_nuscenes_cam_intrinics()

    absoulute_files = utils.get_folder(folder_name="Trip077")

    calibrated_sensor_file = utils.get_files(absoulute_files, file_format="json")


    intrinsics_map = {
        'C1 front60Single',
        'C7_R2',
        'C7_L2',
        'C4_rearCam',
        'C5_L1',
        'C5_R1',
    }

    cam_data = read_NAP_Lab_camera_prarameters(calibrated_sensor_file[0])

 





