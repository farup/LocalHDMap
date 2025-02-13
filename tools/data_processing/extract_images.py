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


save_img_rooth = "/cluster/home/terjenf/NAPLab_car/data"


import sys
sys.path.append("/cluster/home/terjenf/")

image__frame_span = (11672, 15972)
# image__frame_span = (12672, 13972)
#camera_json = "/cluster/home/terjenf/MapTR/NAP_raw_data/Trip077/camerasandCanandGnssCalibratedAll_lidars00-virtual.json"

from NAPLab_car.tools.data_processing import utils


def create_folders(extracted_root_folder, trip_name, cam_names, image_folder_name="samples"):

    new_folders = []
    for cam_name in cam_names: 
        new_folder = os.path.join(extracted_root_folder, trip_name, image_folder_name, cam_name)
        if not os.path.exists(new_folder): 
            os.makedirs(new_folder)
            print("Created Folder", new_folder)
            new_folders.append(new_folder)
        else:
            new_folders.append(new_folder)
        
    return new_folders 


def extract_images(save_img_rooth, folder_name, camera_files, timestamp_files):
    """ 
    Extract images from files. Save image name with corresponding timestamp

    """

    cam_names = [cam.split("/")[-1].split(".")[0] for cam in camera_files]
    cam_folder_paths = create_folders(save_img_rooth, folder_name,cam_names)

    # if len(cam_folder_paths) < 1:
    #     cam_folder_paths = [os.path.join(save_img_rooth,folder_name, cam_name) for cam_name in cam_names]

    for camera_file, timestamp_file, cam_folder_path, cam in zip(camera_files, timestamp_files, cam_folder_paths, cam_names): 

        count, time_stamps_cam = utils.get_timestamps(timestamp_file)

        save_images_from_camera(cam, cam_folder_path, camera_file, time_stamps_cam )

def camera_timestamps(timestamps_files, camera_files):
    cam_names = [cam.split("/")[-1].split(".")[0] for cam in camera_files]
    cams = {}
    for timestamps_file, cam_name in zip(timestamps_files, cam_names):
        count, timestamps_cam = utils.get_timestamps(timestamps_file)
        cams[cam_name] = {'count': count, 'timestamps_cam': timestamps_cam}
    
    return cams
     
def save_images_from_camera(cam, cam_folder_path, camera_file, time_stamps_cam):

    """
    Extraxt and save images.

    Aargs:
        cam_folder_path: (str) folder to save extracted images
        camera_file: (str) path to camera file
        time_stamps_cam: corresponding timestamps for the camera_file
 
    """

    cam_cap = cv2.VideoCapture(camera_file)
    print("FPS: ", cam_cap.get(cv2.CAP_PROP_FPS))


    if not cam_cap.isOpened():
        print("Error: Unable to open the .h264 file")
    else:
        frame_count = 0
        while True:

            ret, frame = cam_cap.read()
            if not ret:
                break
            
            if not (image__frame_span[0] < frame_count):
                frame_count += 1
                continue

            if frame_count > image__frame_span[1]:
                break

            # Save the frame as an image file
            frame_filename = os.path.join(cam_folder_path, f"{cam}_{time_stamps_cam[frame_count]}.png")
            frame_count += 1

            if os.path.exists(frame_filename): 
                continue

            cv2.imwrite(frame_filename, frame)
            print(f"Saved: {frame_filename}")

            

            # if frame_count >= 550:
            #     break
        # Release resources
        cam_cap.release()

        print(f"Extracted {frame_count} frames to {cam_folder_path}")


if __name__ == "__main__": 

    folder_name ="Trip077"

    absoulute_files = utils.get_folder(folder_name=folder_name)
    camera_files = utils.get_files(absoulute_files, file_format="h264")

    timestamps_files = utils.get_files(absoulute_files, file_format="timestamps")

    count, time_stamps_cam = utils.get_timestamps(timestamps_files[0])


    extract_images(save_img_rooth, folder_name, camera_files, timestamps_files)


    