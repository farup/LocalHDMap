


import sys

sys.path.append("/cluster/home/terjenf/")
sys.path.append("/cluster/home/terjenf/NAPLab_car")


from NAPLab_car.tools.data_processing import utils
import numpy as np



def get_cam_props(cam_name, cam_param):
    w = cam_parm[cam_name]['width']
    h = cam_parm[cam_name]['height']
    cx = cam_parm[cam_name]['cx']
    cy = cam_parm[cam_name]['cy']
    float_bw = cam_parm[cam_name]['float_bw']
   
    return w, h, round(cx), round(cy), float_bw


def poly(r, float_bw):
    res = np.sum([j*r**i for i, j in enumerate(float_bw)])
    return res



def calculate_fw_coef(w, h, cx, cy, float_bw, steps=10):

    rx = np.arange(-cx,w-cx)[::steps]
    ry = np.arange(-cy,h-cy)[::steps]

    r_distances = []
    for y in ry:
        for x in rx:
            r_distances.append(np.sqrt(x**2 + y**2))

    print(f"Number of distances (points) used to calculate: {len(r_distances)}")

    thetas = [poly(r, float_bw) for r in  r_distances]

    forward_degree = len(float_bw) - 1

    f_coeffs = np.polyfit(thetas,r_distances , forward_degree)


    f_coeffs[0] = 0
    
    f_coeffs_list = [float(f_cof) for f_cof in f_coeffs]

    print(f"BW: {float_bw}, FW: {f_coeffs}")

    return f_coeffs_list





if __name__ == "__main__": 
    root_folder = "/cluster/home/terjenf/MapTR/NAP_raw_data/"
    
    absoulute_files = utils.get_folder(root_folder=root_folder, folder_name="Trip077")

    calibrated_sensor_file = utils.get_files(absoulute_files, file_format="json")

    cams = [
        'C1_front60Single',
        'C8_R2',
        'C7_L2',
        'C4_rearCam',
        'C6_L1',
        'C5_R1',]

    cam_parm = extract_camera_parameters.get_naplab_cams(json_files[0], cams)


    cam_intrin = create_cam_intrin(cam_parm)


