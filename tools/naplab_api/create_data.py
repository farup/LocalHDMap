
import json 
import uuid
from dataclasses import dataclass, field
import sys
import pickle

#from nuscenes.nuscenes import NuScenes


sys.path.append("/cluster/home/terjenf/NAPLab_car")

from tools.data_processing import utils
from tools.data_processing import extract_gnss
from tools.data_processing import extract_camera_parameters
from tools.data_processing import extract_images
from tools.naplab_api.tables import Scene, Sample, SampleData, CalibratedSensor, EgoPose, Map

import os 
import numpy as np



nuscenes_cam_json = "/cluster/home/terjenf/NAPLab_car/data/metadata_nuscenes/nuscene_metadata.json"
dataroot = "/cluster/home/terjenf/NAPLab_car/data"

intrinsics_map = {
        'C1_front60Single': 'CAM_FRONT',
        'C8_R2': 'CAM_FRONT_RIGHT', 
        'C7_L2': 'CAM_FRONT_LEFT', 
        'C4_rearCam': 'CAM_BACK', 
        'C6_L1': 'CAM_BACK_LEFT', 
        'C5_R1':  'CAM_BACK_RIGHT'
    }

camera_types = [
            'CAM_FRONT',
            'CAM_FRONT_RIGHT',
            'CAM_FRONT_LEFT',
            'CAM_BACK',
            'CAM_BACK_LEFT',
            'CAM_BACK_RIGHT',
    ]


# def create_scenes(map_token, nbr_samples, timestamps_gnss, timestamps_cams, calibrated_sensors, ego_poses, cams, index_gnss_end, index_cam_start): 

#     # scene, timestamps_gnss, timestamps_cams, calibrated_sensors, ego_poses, cams, index_gnss_end, index_cam_start

#     for i, timestamp_gnss in enumerate(timestamps_gnss[:index_gnss_end:nbr_samples]):
#         if i % 20:
#             scene = Scene(scene_name=f"scene_{i}", nbr_samples=(i%20 + 1) )

   

def create_calibrated_sensors(cam_parameters, nuscnes_intrinsics, sensors=None): 
    """
    Create claibrated sensors
    
    """
    cd_sensors = []
    for i, (k, v) in enumerate(cam_parameters.items()):
        cd_sensor = CalibratedSensor(translation=v['t'], rotation=utils.euler_to_quaternion_yaw(v['roll_pitch_yaw']), camera_intrinsics=nuscnes_intrinsics[intrinsics_map[k]]['camera_intrinsic'], cx=v['cx'], cy=v['cy'], fw_coeff=v['fw_coeff'], bw_coeff=v['bw_coeff'])
        cd_sensors.append(cd_sensor.__dict__)
    
    return cd_sensors

def create_ego_pose(gnss_file, index_gnss_end, yaw_refrence_frame=False):
    """
    Function for creating ego poses, based on selected gnss timestamps. 
    
    """ 
    lat_lon, timestamps_gnss = extract_gnss.get_gnss_data(gnss_file)

    ego_xy_coords = extract_gnss.get_ego_position(lat_lon)
    ego_yaws = extract_gnss.compute_yaws(lat_lon)

    x_offsets = ego_xy_coords.x - ego_xy_coords.x[0]
    y_offsets = ego_xy_coords.y - ego_xy_coords.y[0]

    if yaw_refrence_frame:
        ego_yaws = ego_yaws - ego_yaws[yaw_refrence_frame]

    x_offsets = x_offsets[:index_gnss_end]
    y_offsets = y_offsets[:index_gnss_end]

    ego_poses = []
    for i, time_stamp_gnns in enumerate(timestamps_gnss[:index_gnss_end]):
        egopose = EgoPose(translation=[float(x_offsets[i]), float(y_offsets[i]), float(0)], rotation=utils.euler_to_quaternion_yaw([0,0, ego_yaws[i]]), timestamp=time_stamp_gnns)
        ego_poses.append(egopose.__dict__)

    return ego_poses


def generate_filenmae(scene, trip, cam, timestamp):
    return os.path.join(scene.dataroot, trip, "samples", cam, f"{cam}_{timestamp}.png")

def create_samples_new(trip, timestamps_gnss, timestamps_cams, calibrated_sensors, ego_poses, cams, index_gnss_end, index_cam_start):
    """
    
    """
    samples = []
    scenes = []
    samples_data = []
    scene_count = 0
    for i, timestamp_gnss in enumerate(timestamps_gnss[:index_gnss_end]): 
        
        if i % 40 == 0: 

            scene = Scene(scene_name=f"scene_{scene_count}", nbr_samples=(40 if i%40 == 0 else i%40), dataroot=dataroot)
            scenes.append(scene.__dict__)
            scene_count += 1


        sample = Sample(scene_token=scene.token, scene_name=scene.scene_name, timestamp=timestamp_gnss)
        data = {}

        for j, (cam, timestamps_cam) in enumerate(zip(cams, timestamps_cams)):

   
            sample_data = SampleData(sample_token=sample.token, calibrated_sensor_token=calibrated_sensors[j]['token'],  ego_pose_token=ego_poses[i]['token'], timestamp=int(timestamps_cam[i]), filename=generate_filenmae(scene, trip, cam, timestamps_cam[i]), next_idx=None, prev_idx=None)
            samples_data.append(sample_data.__dict__)

            data[cam] = sample_data.token

        sample.data = data
        
        samples.append(sample.__dict__)

    return samples, samples_data, scenes


def create_samples(scene, timestamps_gnss, timestamps_cams, calibrated_sensors, ego_poses, cams, index_gnss_end, index_cam_start):
    """
    
    """
    samples = []
    samples_data = []
    for i, timestamp_gnss in enumerate(timestamps_gnss[:index_gnss_end]): 
        sample = Sample(scene_token=scene.token, timestamp=timestamp_gnss)
        data = {}


        for j, (cam, timestamps_cam) in enumerate(zip(cams, timestamps_cams)):

   
            sample_data = SampleData(sample_token=sample.token, calibrated_sensor_token=calibrated_sensors[j]['token'],  ego_pose_token=ego_poses[i]['token'], timestamp=int(timestamps_cam[i]), filename=generate_filenmae(scene, cam, timestamps_cam[i]), next_idx=None, prev_idx=None)
            samples_data.append(sample_data.__dict__)

            data[cam] = sample_data.token

        sample.data = data
        
        samples.append(sample.__dict__)

    return samples, samples_data


def save_tables_json(dataroot, folder_name, table, filename):

    new_folder = os.path.join(dataroot, folder_name, "tables")

    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    new_file = os.path.join(new_folder, filename)
    with open(new_file, 'w') as f: 
        json.dump(table, f, indent=4)
        print("Saved to", new_file)




def process_timestamps(cam_info, index_cam_start, selected_cams):
    """ 
    Adjusts camera timestamps to fit with the best synched GNSS and Camera Captures
    
    """

    lowest_count = np.min([v['count'] for k,v in cam_info.items()])
    timestamps_list = []

    for k,v in cam_info.items():
        if k not in selected_cams:
            continue 
        if v['count'] > lowest_count:
            temp_index_cam_start = index_cam_start + (v['count'] - lowest_count)
            timestamp = v['timestamps_cam'][temp_index_cam_start::3]
            timestamps_list.append(timestamp)


        else:
            timestamp = v['timestamps_cam'][index_cam_start::3]
            timestamps_list.append(timestamp)

    return timestamps_list


def select_files(files, selected):
    new_files = []
    for file in files: 
        if file.split("/")[-1].split(".")[0] in selected:
            new_files.append(file)
    
    return new_files


if __name__ == "tools.data_processing.custom_data": 


    print("HEi")


if __name__ == "__main__": 

    print("hei")

    folder_name = "Trip077"
    root_folder = "/cluster/home/terjenf/MapTR/NAP_raw_data/"
    

    absoulute_files = utils.get_folder(root_folder=root_folder, folder_name=folder_name)
    camera_files = utils.get_files(absoulute_files, file_format="h264")  
    timestamps_files = utils.get_files(absoulute_files, file_format="timestamps")


    selected_cams = list(intrinsics_map.keys())

    timestamps_files = select_files(timestamps_files, selected_cams)
    camera_files = select_files(camera_files, selected_cams)


    cam_names= [cam.split("/")[-1].split(".")[0] for cam in camera_files]



    gnss_file = utils.get_gnss_file(absoulute_files, gnss_type="gnss52")

    cams_info = extract_images.camera_timestamps(timestamps_files, camera_files)

    lat_lon, timestamps_gnss = extract_gnss.get_gnss_data(gnss_file)
    #bests = extract_gnss.calculate_syncs_diffs(cams_info, timestamps_gnss)

    description="Handels -> Eglseterbru -> Nidarosdomen -> Samfundet -> Høyskoleringen"

    # cam_start 64, gnss end -18

    index_cam_start = 52
    index_gnss_end = -18

    ego_poses = create_ego_pose(gnss_file, index_gnss_end, yaw_refrence_frame=500)
    
    calibrated_sensor_files = utils.get_files(absoulute_files, file_format="json")

    timestamps_files = utils.get_files(absoulute_files, file_format="timestamps")

    cam_parameters = extract_camera_parameters.get_naplab_cams(calibrated_sensor_files[0],selected_cams)

    timestamps_cams = process_timestamps(cams_info, index_cam_start, selected_cams)

    nuscnes_intrinsics = utils.load_json_file(nuscenes_cam_json)

    cd_sensors = create_calibrated_sensors(cam_parameters, nuscnes_intrinsics)
    cam_names = [cam.split("/")[-1].split(".")[0] for cam in camera_files]

    samples, samples_data, scenes = create_samples_new(trip=folder_name, timestamps_gnss=timestamps_gnss, timestamps_cams=timestamps_cams,
     calibrated_sensors=cd_sensors, ego_poses=ego_poses, cams=cam_names, index_gnss_end=index_gnss_end, index_cam_start=index_cam_start)

    ego_xy_coords = extract_gnss.get_ego_position(lat_lon)
    ego_yaws = extract_gnss.compute_yaws(lat_lon)


    data_root = "/cluster/home/terjenf/NAPLab_car/data"
    
    save_tables_json(data_root,folder_name,  scenes, "scenes.json")
    save_tables_json(data_root,folder_name,  samples, "samples.json")
    save_tables_json(data_root,folder_name,  samples_data, "samples_data.json")
    save_tables_json(data_root,folder_name,  cd_sensors, "cd_sensors.json")
    save_tables_json(data_root,folder_name,  ego_poses, "ego_poses.json")
  
 
    # cd1 = utils.load_from_picle_file("/cluster/home/terjenf/NAPLab_car/data/Trip077/tables/cd_sensors.pkl")
    # eg1 = utils.load_from_picle_file("/cluster/home/terjenf/NAPLab_car/data/Trip077/tables/ego_poses.pkl")
    # sa1 = utils.load_from_picle_file("/cluster/home/terjenf/NAPLab_car/data/Trip077/tables/samples.pkl")
    # sad1 = utils.load_from_picle_file("/cluster/home/terjenf/NAPLab_car/data/Trip077/tables/samples_data.pkl")

  
    # utils.save_to_json_file(ego_poses, naplab_tables_path, "ego_poses.json")
    # utils.save_to_json_file(cd_sensors, naplab_tables_path, "calibarated_sensors.json")
    # utils.save_to_json_file(samples, naplab_tables_path, "samples.json")
    # utils.save_to_json_file(samples_data, naplab_tables_path, "samples_data.json")


