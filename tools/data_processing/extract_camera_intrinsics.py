

from NAPLab_car.tools.data_processing import utils
from NAPLab_car.tools.data_processing import extract_camera_parameters


def make_image_coords(image_shape):
    """ 
    Generate mesh grid for plotting image plane
    """
 
    X, Y = np.meshgrid(np.arange(image_shape[0],), np.arange(image_shape[1]))

    x_coords = X.flatten()
    y_coords = Y.flatten()

    image_coords = np.stack((y_coords, x_coords))
    return image_coords, X, Y 

def get_cam_props(cam_v):
    w = cam_v['width']
    h = cam_v['height']
    cx = cam_v['cx']
    cy = cam_v['cy']
    float_bw = cam_v['float_bw']
   
    return w, h, round(cx), round(cy), float_bw


def shift_image(x_values, y_values, cx, cy):
    return (x_values - cx), (y_values - cy)



def calculate_rays(w, h, cx, cy, float_bw): 
    r_d = []
    rays = []
    for v in range(h):
        for u in range(w):
            ry = v - cy
            rx = u - cx

            r = np.sqrt(rx**2 + ry**2)
            theta = np.sum([j*r**i for i, j in enumerate(float_bw)])

            phi = np.arctan2(ry, rx)
            ray = [np.sin(theta)*np.cos(phi),
                    np.sin(theta)*np.sin(phi),
                      np.cos(theta)]
            
            r_d.append(r)
            rays.append(ray)

    return np.array(r_d), np.array(rays)


def normalize_rays(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)

    # Avoid division by zero (set zero norms to 1 to prevent NaNs)
    norms[norms == 0] = 1

    # Normalize each vector
    normalized_vectors = vectors / norms

    return normalized_vectors


def create_cam_intrin(cam_param):

    cam_intrin = {}

    for cam_name, v in cam_param.items()
        w, h, cx, cy, float_bw = get_cam_props(cam_v)
        image_coords, X, Y  = make_image_coords(w,h)

        shifted_x, shifted_y = shift_image(cx, cy)

        r_d, rays = calculate_rays(w, h, cx, cy, float_bw)

        norm_rays = normalize_rays(rays)

        cam_intrin[cam_name] = norm_rays

    
    return cam_intrin


if __name__ "__main__": 

    
    absoulute_files = utils.get_folder(folder_name="Trip077")

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


