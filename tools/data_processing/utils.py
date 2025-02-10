import numpy as np 
import cv2 
import json
import os
import pickle
from pyquaternion import Quaternion

#image_path_nor = "/cluster/home/terjenf/MapTR/NAP_data/nuscenes/samples/C1_front60Single/frame_0782.png"
trip_path = "/cluster/home/terjenf/MapTR/NAP_raw_data/Trip077/"
root_folder = "/cluster/home/terjenf/MapTR/NAP_raw_data/"
#camera_json = "/cluster/home/terjenf/MapTR/NAP_raw_data/Trip077/camerasandCanandGnssCalibratedAll_lidars00-virtual.json"



def euler_to_quaternion_yaw(r):
    roll, pitch, yaw = r
    qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
    qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)
    qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    return [float(qw), float(qx), float(qy), float(qz)] 


def euler_to_quaternion_pyquaternion(roll, pitch, yaw):
  
    # Create quaternion from Euler angles
    q = Quaternion(axis=[1, 0, 0], angle=roll) * \
        Quaternion(axis=[0, 1, 0], angle=pitch) * \
        Quaternion(axis=[0, 0, 1], angle=yaw) 

    return q


def save_to_picle_file(obj, path, pkl_name):
    if not os.path.exists(path):
        os.makedirs(path)

    new_file = str(os.path.join(path, pkl_name))
    with open(new_file, 'wb') as f: 
        pickle.dump(obj, f)
        print("Saved pkl to", new_file)


def load_from_picle_file(path):
    with open(path, "rb") as f:
        obj_pkl = pickle.load(f)
    return obj_pkl


def save_to_json_file(obj, path, json_name): 
    if not os.path.exists(path):
        os.makedirs(path)

    new_file = str(os.path.join(path, json_name))
    with open(new_file, 'w') as f: 
        json.dump(obj, f)
        print("Saved json to", new_file)

def load_json_file(file_path ):
    with open(file_path, 'r') as f: 
        json_obj = json.load(f)
        return json_obj


def sort_func(e): 
    return e.split("/")[-1]

def get_folders(path=root_folder):
    folder = [os.path.join(path,f) for f in os.listdir(path)]
    return folder


def get_folder(folder_name="Trip077"): 
    if not os.path.exists(folder := os.path.join(root_folder, folder_name)): 
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), fodler)
    
    absoulute_files = [os.path.join(root_folder,folder_name,  sub_folder) for sub_folder in os.listdir(folder)]
    print(absoulute_files)
    absoulute_files.sort(key=sort_func)

    return absoulute_files

def get_files(absoulute_files, file_format):

    files = []
    for file in absoulute_files:
        if file.split('.')[-1] == file_format: 
            files.append(file)

    return files


def get_gnss_file(absoulute_files, gnss_type="gnss52"):
    bin_files = get_files(absoulute_files, file_format="bin")

    for bin_file in bin_files: 
        if gnss_type in bin_file: 
            return bin_file

def get_timestamps(file_with_stamps): 
    count = 0
    time_stamps_cam = []
    with open(file_with_stamps, 'r') as file: 
        for timestamp in file: 
            # print(timestamp)
            # break
            time_stamps_cam.append(timestamp.split("\t")[-1].strip())
            count += 1
        print(f"Counted {count} timestamps in file {file_with_stamps}")
    return count, time_stamps_cam


def read_gnss52(path):
    with open(path, "rb") as f:
        list_lines = []
        position = dict()
        for line in f.readlines():
            if line.startswith(b"$GPGGA"):
                list_lines.append(line)
    return list_lines



if __name__ == "__main__": 

    absoulute_files = get_folder(folder_name="Trip077")

    camera_files = get_files(absoulute_files, file_format="h264")
    
    timestamps_files = get_files(absoulute_files, file_format="timestamps")

    count, time_stamps_cam = get_timestamps(timestamps_files[0])

    gnss52_file = get_gnss_file(absoulute_files, gnss_type="gnss52")


    print(absoulute_files)



