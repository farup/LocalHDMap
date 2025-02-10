
import json 
import uuid
from dataclasses import dataclass

#from nuscenes.nuscenes import NuScenes

import utils
import extract_gnss
import extract_camera_parameters
import extract_images
import os 
import numpy as np

nuscenes_cam_json = "/cluster/home/terjenf/NAPLab_car/data_nuscnes/nuscene_metadata.json"

intrinsics_map = {
        'C1_front60Single': 'CAM_FRONT',
        'C8_R2': 'CAM_FRONT_RIGHT', 
        'C7_L2': 'CAM_FRONT_LEFT', 
        'C4_rearCam': 'CAM_BACK', 
        'C6_L1': 'CAM_BACK_LEFT', 
        'C5_R1':  'CAM_BACK_RIGHT'
    }


def generate_token():
    return str(uuid.uuid4())


class Scene: 
    def __init__(self, scene_name, description, data_root):
        self.token = generate_token() 
        self.scene_name = scene_name
        self.description = description
        self.data_root = data_root
      
class Sample: 
    def __init__(self, scene_token, timestamp, next_idx=None, prev_idx=None): 
        self.token = generate_token()
        self.scene_token = scene_token
        self.timestamp = timestamp
  
        self.next = next_idx
        self.prev = prev_idx

    def set_next(self, next_idx): 
        self.next = next_idx

    def set_prev(self, prev_idx): 
        self.prev = prev_idx

    def set_data(self, data): 
        self.data = data

class SampleData: 
    def __init__(self, sample_token, timestamp, calibrated_sensor_token, ego_pose_token=None, filename=None, next_idx=None, prev_idx=None): 
        self.token = generate_token()
        self.sample_token = sample_token
        self.timestamp = timestamp
        self.calibrated_sensor_token = calibrated_sensor_token

        self.filename = filename

        self.next = next_idx
        self.prev = prev_idx

    def set_next(self, next_idx): 
        self.next = next_idx

    def set_prev(self, prev_idx): 
        self.prev = prev_idx


class CalibratedSensor:
    """
    [copy from nuscenes]
    Definition of a particular sensor (lidar/radar/camera) as calibrated on a particular vehicle. 
    All extrinsic parameters are given with respect to the ego vehicle body frame.
    All camera images come undistorted and rectified.
    
    """
    def __init__(self, translation, rotation, camera_intrinsics, sensor_token=None):
        self.token = generate_token()
        self.sensor_token = sensor_token
        self.translation = translation 
        self.rotation = rotation 
        self.camera_intrinsics = camera_intrinsics


class EgoPose: 

    """"
    Ego vehicle pose at a particular timestamp. Given with respect to global coordinate system of the log's map. 
    The localization is 2-dimensional in the x-y plane.
    """
    def __init__(self, translation, rotation, timestamp):
        self.token = generate_token()
        self.translation = translation 
        self.rotation = rotation 
        self.timestamp = timestamp


class Log: 
    def __init__(self, vehicle_name, date_caputred, location):
        self.token = generate_token()
        self.vehicle_name = vechile_name
        self.date_captured = date_caputred
        self.location = location


class Sensor: 
    def __init__(self, channel, modility):
        self.token = generate_token()
        self.channel = channel
        self.modality = channel




# def process_timestamps(cam_timestamps):
#     for k,v in cam_timestamps.items():
    
 
def create_calibrated_sensors(cam_parameters, nuscnes_intrinsics, sensors=None): 
    """
    Create claibrated sensors
    
    """
    cd_sensors = []
    for i, (k, v) in enumerate(cam_parameters.items()):
        cd_sensor = CalibratedSensor(translation=v['t'], rotation=utils.euler_to_quaternion_yaw(v['roll_pitch_yaw']), camera_intrinsics=nuscnes_intrinsics[intrinsics_map[k]]['camera_intrinsic'])
        cd_sensors.append(cd_sensor)
    
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
        egopose = EgoPose(translation=[x_offsets[i], y_offsets[i], 0], rotation=utils.euler_to_quaternion_yaw([0,0, ego_yaws[i]]), timestamp=time_stamp_gnns)
        ego_poses.append(egopose)

    return ego_poses


def generate_filenmae(scene, cam, timestamp):
    return os.path.join(scene.data_root, scene.scene_name, cam, f"_{cam}_{timestamp}")


def create_samples(scene, timestamps_gnss, timestamps_cams, calibrated_sensors, ego_poses, cams, index_gnss_end, index_cam_start):
    """
    
    """
    samples = []
    samples_data = []
    for i, timestamp_gnss in enumerate(timestamps_gnss[:index_gnss_end]): 
        sample = Sample(scene_token=scene.token, timestamp=timestamp_gnss)
        data = {}
        for i, (cam, timestamps_cam) in enumerate(zip(cams, timestamps_cams)):
            sample_data = SampleData(sample_token=sample.token, calibrated_sensor_token=calibrated_sensors[i].token,  ego_pose_token=ego_poses[i].token, timestamp=int(timestamps_cam[i]), filename=generate_filenmae(scene, cam, timestamps_cam[i]), next_idx=None, prev_idx=None)
            samples_data.append(sample_data)

            data[cam] = sample_data.token

        sample.set_data(data)
        
        samples.append(sample)

    return samples, samples_data


def process_timestamps(cam_info, index_cam_start, selected_cams):
    """ Adjusts camera timestamps to fit with the best synched GNSS and Camera Captures
    

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


if __name__ == "__main__": 

    print("hei")

    absoulute_files = utils.get_folder(folder_name="Trip077")
    camera_files = utils.get_files(absoulute_files, file_format="h264")  
    timestamps_files = utils.get_files(absoulute_files, file_format="timestamps")

    cam_names= [cam.split("/")[-1].split(".")[0] for cam in camera_files]

    camera_types = [
            'CAM_FRONT',
            'CAM_FRONT_RIGHT',
            'CAM_FRONT_LEFT',
            'CAM_BACK',
            'CAM_BACK_LEFT',
            'CAM_BACK_RIGHT',
    ]

    gnss_file = utils.get_gnss_file(absoulute_files, gnss_type="gnss52")

    cams_info = extract_images.camera_timestamps(timestamps_files, camera_files)

    lat_lon, timestamps_gnss = extract_gnss.get_gnss_data(gnss_file)


    # bests = extract_gnss.calculate_syncs_diffs(cams_info, timestamps_gnss)

    data_root = "/cluster/home/terjenf/NAPLab_car/data_images"
    description="Handels -> Eglseterbru -> Nidarosdomen -> Samfundet -> Høyskoleringen"

    scene = Scene(scene_name="trip_077", description=description, data_root=data_root)

    # cam_start 64, gnss end -18

    index_cam_start = 64
    index_gnss_end = -18

    ego_poses = create_ego_pose(gnss_file, index_gnss_end, yaw_refrence_frame=500)

    selected_cams = list(intrinsics_map.keys())

    calibrated_sensor_files = utils.get_files(absoulute_files, file_format="json")

    timestamps_files = utils.get_files(absoulute_files, file_format="timestamps")

    cam_parameters = extract_camera_parameters.read_NAP_Lab_camera_prarameters(calibrated_sensor_files[0],selected_cams)

    timestamps_cams = process_timestamps(cams_info, index_cam_start, selected_cams)

    nuscnes_intrinsics = utils.load_json_file(nuscenes_cam_json)

    cd_sensors = create_calibrated_sensors(cam_parameters, nuscnes_intrinsics)
    cam_names = [cam.split("/")[-1].split(".")[0] for cam in camera_files]


    samples = create_samples(scene=scene, timestamps_gnss=timestamps_gnss, timestamps_cams=timestamps_cams,
     calibrated_sensors=cd_sensors, ego_poses=ego_poses, cams=cam_names, index_gnss_end=index_gnss_end, index_cam_start=index_cam_start)

    ego_xy_coords = extract_gnss.get_ego_position(lat_lon)
    ego_yaws = extract_gnss.compute_yaws(lat_lon)


    print("Terje")
