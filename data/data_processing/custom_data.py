
import json 
import uuid
from dataclasses import dataclass

from nuscenes.nuscenes import NuScenes

def generate_token():
    return str(uuid.uuid4())


class Scene: 
    def __init__(self, scene_name, description):
        self.token = generate_token() 
        self.scene_name = scene_name
        self.description = description
        

class Sample: 
    def __init__(self, scene_token, timestamp, next_idx=None, prev_idx=None): 
        self.token = generate_token()
        self.scene_token = scene_token
        self.timestamp = timestamp
        self.data = {}

        self.next = next_idx
        self.prev = prev_idx

    def set_next(self, next_idx): 
        self.next = next_idx

    def set_prev(self, prev_idx): 
        self.prev = prev_idx

class SampleData: 
    def __init__(self, sample_token, timestamp, next_idx=None, prev_idx=None): 
        self.token = generate_token()
        self.sample_token = sample_toke
        self.timestamp = timestamp

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
    def __init__(self, sensor_token):
        self.token = generate_token()
        self.sensor_token = sensor_token


class EgoPose: 

    """"
    Ego vehicle pose at a particular timestamp. Given with respect to global coordinate system of the log's map. 
    The localization is 2-dimensional in the x-y plane.
    """
    def __init__(self):
        self.token = generate_token()



class Log: 
    def __init__(self, vehicle_name, date_caputred, location):
        self.token = generate_token()
        self.vehicle_name = vechile_name
        self.date_captured = date_caputred
        self.location = location


if __name__ == "__main__": 

    print("hei")

    scene = Scene(scene_name="trip_077", description="Handels -> Eglseterbru -> Nidarosdomen -> Samfundet -> Høyskoleringen")
    sample = Sample(scene_token=scene.token, timestamp=23242535)

    print("TErje ")
