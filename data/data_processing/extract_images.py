import numpy as np 
import cv2 
import json
import os


import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point


#image_path_nor = "/cluster/home/terjenf/MapTR/NAP_data/nuscenes/samples/C1_front60Single/frame_0782.png"
trip_path = "/cluster/home/terjenf/MapTR/NAP_raw_data/Trip077/"
root_folder = "/cluster/home/terjenf/MapTR/NAP_raw_data/"


save_img_rooth = "/cluster/home/terjenf/NAPLab_car/data_images"
folder_name ="Trip077"
#camera_json = "/cluster/home/terjenf/MapTR/NAP_raw_data/Trip077/camerasandCanandGnssCalibratedAll_lidars00-virtual.json"

import utils


def create_folders(folder_name, cam_names):

    new_folders = []
    for cam_name in cam_names: 
        new_folder = os.path.join(save_img_rooth,folder_name, cam_name)
        if not os.path.exists(new_folder): 
            os.makedirs(new_folder)
            print("Created Folder", new_folder)
            new_folders.append(new_folder)

    return new_folders 




def extract_images(folder_name, camera_files, timestamp_files):
    """ 
    Extract images from files. Save image name with corresponding timestamp

    """

    cam_names = [cam.split("/")[-1].split(".")[0] for cam in camera_files]
    cam_folder_paths = create_folders(folder_name, cam_names)

    if len(cam_folder_paths) < 1:
        cam_folder_paths = [os.path.join(save_img_rooth,folder_name, cam_name) for cam_name in cam_names]


    for camera_file, timestamp_file, cam_folder_path in zip(cmaera_files, timestamp_files, cam_folder_paths): 

        count, time_stamps_cam = utils.get_timestamps(timestamp_file)

        save_images_from_camera(cam_folder_path,camera_file, time_stamps_cam )

        
def save_images_from_camera(cam_folder_path, camera_file, time_stamps_cam):

    """
    Extraxt and save images.

    Aargs:
        cam_folder_path: (str) folder to save extracted images
        camera_file: (str) path to camera file
        time_stamps_cam: corresponding timestamps for the camera_file
 
    """



    cam_cap = cv2.VideoCapture(camera_file)
    print("FPS: ", cap_2.get(cv2.CAP_PROP_FPS))


    if not cam_cap.isOpened():
        print("Error: Unable to open the .h264 file")
    else:
        frame_count = 0
        while True:
            # Read each frame
            ret, frame = cam_cap.read()
            if not ret:
                break
            # Save the frame as an image file
            frame_filename = os.path.join(cam_folder_path, f"frame_{frame_count:04d}_{time_stamps_cam[frame_count]}.png")
            cv2.imwrite(frame_filename, frame)
            print(f"Saved: {frame_filename}")

            frame_count += 1
        # Release resources
        cam_cap.release()
        print(f"Extracted {frame_count} frames to {cam_folder_path}")


if __name__ == "__main__": 

    

    absoulute_files = utils.get_folder(folder_name=folder_name)
    camera_files = utils.get_files(absoulute_files, file_format="h264")

    timestamps_files = utils.get_files(absoulute_files, file_format="timestamps")

    cam_names = [cam.split("/")[-1].split(".")[0] for cam in camera_files]




    create_folders(folder_name, cam_names)


    count, time_stamps_cam = utils.get_timestamps(timestamps_files[0])


    