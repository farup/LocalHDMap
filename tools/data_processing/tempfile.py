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

    def 


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