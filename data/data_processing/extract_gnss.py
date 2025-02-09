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
#camera_json = "/cluster/home/terjenf/MapTR/NAP_raw_data/Trip077/camerasandCanandGnssCalibratedAll_lidars00-virtual.json"


import utils


def read_gnss(path):
    """
    Read gnss file 

    Returns: 
    """
    with open(path, "rb") as f:
        GPGGA_lines = []
        position = dict()
        for line in f.readlines():
            if line.startswith(b"$GPGGA"):
                GPGGA_lines.append(line)
    return GPGGA_lines


def nmea_to_decimal(coord):
    """ Convert MNEA latidue and and longitude to decimal degrees
    Args
        Coords: 
            Latitude is represented as ddmm.mmmm
            longitude is represented as dddmm.mmmm
            - dd or ddd is degrees
            - mm.mmmm is minutes and decimal fractions of minutes
    Returns:
        float: degrees in decimal 
    """
    degrees = int(coord[:2])  # First 2 digits are degrees
    minutes = float(coord[2:])  # Rest is minutes
    decimal_degrees = degrees + (minutes / 60)
    return decimal_degrees

def get_gnss_data(gnss_file):
    """ Extract latitude, longitude (in decimal degrees), and gnss timestamps

    Args:
        gnss_file: file path to gnss data 

    Returns:
        list: list of tuples with lat and lon , 
        list: list of timestamps

    
    """
    with open(gnss_file, "rb") as f:
        count = 0

        timestamps_gnss = []

        lat_lon = []
  
        for line in f.readlines():
            if line.startswith(b"$GPGGA"):
            
                coord = (line.split(b",")[2:6])
                latitude = float(coord[:2][0].strip())  #  6324.8972646 
                longitude = float(coord[2:][0].strip()) # 1023.9477304 
                

                lat = nmea_to_decimal(str(latitude)) # 63.41495441
                lon = nmea_to_decimal(str(longitude))

                lat_lon.append((lat, lon))

                
                time_stamp = (int(line.split(b" ")[-1].strip()))

                #dict_obj[time_stamp] = {'x': x, 'y':y}
                timestamps_gnss.append(time_stamp)
                
                count += 1

    print(f"Read and extracted {count} lines of data")
    return lat_lon, timestamps_gnss


def find_best_sync_new(timestamp1, timestamp2):
    """  Loop through different start and end positions for timestamps for finding best average sync
        Assume one timestamp1 is 10hz (gnss) and timestamp3 30hz (camera)
    
    Args:
        timestamp1: list of timestamps 
        timestamp2: list of timestamps

    
    """

    dict_best = {'s': {'best_score': 1000000000}, 
                'r': {'best_score': 1000000000}}

    for i in range(200):
        if i == 0:
            print("Start")
            seconds = calculate_sync_dif(timestamp1, timestamp2[::3])
            if seconds < dict_best['s']['best_score']:
                dict_best['s']['best_score'] = seconds 
                dict_best['s']['timestamp1'] = 0
                dict_best['s']['timestamp2'] = 0

            timestamp2_start =  3*(i+1)
            timestamp1_end = -1

        else:
            timestamp2_start =  3*(i+1) + 1
            timestamp1_end = -i-2

        print(f"\nArgument1 end number: {timestamp1_end}, Argument2 start number: {timestamp2_start}")

        for direction in ['s', 'r']:
            if direction == 's':
                seconds = calculate_sync_dif(timestamp1[:timestamp1_end], timestamp2[timestamp2_start::3])
                if seconds < dict_best['s']['best_score']:
                    dict_best['s']['best_score'] = seconds 
                    dict_best['s']['timestamp2_start'] = timestamp2_start
                    dict_best['s']['timestamp1_end'] = timestamp1_end
                    
            else: 
                seconds = calculate_sync_dif(timestamp1[timestamp1_end*-1:], timestamp2[:-timestamp2_start:3])
                if seconds < dict_best['r']['best_score']:
                    dict_best['r']['best_score'] = seconds 
                    dict_best['r']['timestamp2_end'] = -timestamp2_start
                    dict_best['r']['timestamp1_start'] = timestamp1_end*-1

    return dict_best



def find_best_sync(gnss, cam):
    """ Loop through different start and end timestamps"""

    dict_best = {'best_score': 1000000000}


    for i in range(200):
        if i == 0:
            print("Start")
            seconds = calculate_sync_dif(gnss, cam[::3])
            if seconds < dict_best['best_score']:
                dict_best['best_score'] = seconds 
                dict_best['cam_start'] = 0
                dict_best['gnss_end'] = 0

            cam_split =  3*(i+1)
            gnss_split = -1

        else:
            cam_split =  3*(i+1) + 1
            gnss_split = -i-2

        print(f"\nGNSS end number: {gnss_split}, Cam start number: {cam_split}")
        seconds = calculate_sync_dif(gnss[:gnss_split], cam[cam_split::3])
        if seconds < dict_best['best_score']:
            dict_best['best_score'] = seconds 
            dict_best['cam_start'] = cam_split
            dict_best['gnns_end'] = gnss_split
    return dict_best


def average_frequency(timestamps): 
    """ Find average frequency in timestamps
    
    """

    freq = np.mean(np.abs(np.array(timestamps[:-1]).astype(int) - np.array(timestamps[1:]).astype(int)))
    print(f"Average time diff: {freq} ms, in seconds {freq / 1e6}")
    print(f"Average freq: {1 / (freq / 1e6)} Hz")


def calculate_sync_dif(timestamps1, timestamps2):

    assert len(timestamps1) == len(timestamps2), f" arg1 {len(timestamps1)} should be equal arg2 {len(timestamps2)}"
    
    np_timestamps1 = np.array(timestamps1).astype(int)
    np_timestamps2 = np.array(timestamps2).astype(int)

    seconds = (np.mean(np.abs(np_timestamps1 - np_timestamps2))) / 1e6
    print(f"Average time (in seconds) between timestamps: {seconds}")
    return seconds


def get_ego_position(lat_lon):
    """
    Extract coordinates in 3857 (in meters for latitude and longitude)
    
    """

    # Create a GeoDataFrame from latitude and longitude
    geometry = [Point(coord[1], coord[0]) for coord in lat_lon]

    gdf = gpd.GeoDataFrame(geometry=geometry)

    gdf.set_crs("EPSG:4326", inplace=True)
    # EPSG:4326 (WGS 84)  represents locations using latitude and longitude (degrees)
    # standard CRS for GPS, Google Earth, OpenStreetMap, and most global datasets.

    gdf = gdf.to_crs(epsg=3857)

    return gdf.get_coordinates()


def compute_yaw(lat1, lon1, lat2, lon2):
    """
    Compute yaw (bearing) from point (lat1, lon1) to (lat2, lon2).
    """
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    d_lon = lon2 - lon1
    x = np.sin(d_lon) * np.cos(lat2)
    y = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(d_lon)
    
    yaw = np.arctan2(x, y)  # Bearing in radians

    yaw_deg = (np.degrees(yaw) + 360) % 360  # Convert to degrees
    
    return yaw_deg


def compute_yaws(lat_lon):
    yaws  = [compute_yaw(point1[0], point1[1], point2[0], point2[1]) for point1, point2 in zip(lat_lon[:-1], lat_lon[1:])]
    return yaws


def plot_route(lat_lon):

    # Create a GeoDataFrame from latitude and longitude
    geometry = [Point(coord[1], coord[0]) for coord in lat_lon]

    gdf = gpd.GeoDataFrame(geometry=geometry)

    gdf.set_crs("EPSG:4326", inplace=True)
    # EPSG:4326 (WGS 84)  represents locations using latitude and longitude (degrees)
    # standard CRS for GPS, Google Earth, OpenStreetMap, and most global datasets.

    gdf = gdf.to_crs(epsg=3857)
    # projected coordinate system that represents locations in meters.
    # Convert the coordinates to a CRS that works with contextily basemaps (Web Mercator)
    fig, ax = plt.subplots(figsize=(10, 10))  # Adjust width and height here
    # Plot the map with reference basemap

    gdf.plot(marker="o", color="blue", markersize=1, ax=ax)
    #ax.set_xlim(-800, 800)

    # Add reference map (OpenStreetMap)
    ctx.add_basemap(ax, crs=gdf.crs.to_string())

    start = gdf.get_coordinates().iloc[0]
    end = gdf.get_coordinates().iloc[-1]

    plt.scatter(start.x, start.y, label="Start", color="red")
    plt.scatter(end.x, end.y, label="End", color="black")


    # Add labels, title, and other customizations
    plt.title("Latitude/Longitude on Map")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()

    plt.savefig('/cluster/home/terjenf/NAPLab_car/plots/route/route.png')



if __name__ == "__main__": 

    absoulute_files = utils.get_folder(folder_name="Trip077")
    camera_files = utils.get_files(absoulute_files, file_format="h264")  
    timestamps_files = utils.get_files(absoulute_files, file_format="timestamps")
    
    count, timestamps_cam = utils.get_timestamps(timestamps_files[0])

    gnss_file = utils.get_gnss_file(absoulute_files, gnss_type="gnss52")

    GPGGA_lines = read_gnss(gnss_file)

    lat_lon, timestamps_gnss = get_gnss_data(gnss_file)

    average_frequency(timestamps_gnss)
    average_frequency(timestamps_cam)

    best_new = find_best_sync_new(timestamps_gnss, timestamps_cam)

    # GNSS end number: -28, Cam start number: 82
    # Average time (in seconds) between timestamps: 0.015527154475982533

    #plot_route(lat_lon)


    ego_xy_coords = get_ego_position(lat_lon)

    ego_yaws = compute_yaws(lat_lon)

    print("Done")

    # calculate_sync_dif(timestamps_gnss, timestamps_cam[::3])
    # calculate_sync_dif(timestamps_gnss[:-1], timestamps_cam[3::3])

    # calculate_sync_dif(timestamps_gnss[:-10], timestamps_cam[30::3])
    # calculate_sync_dif(timestamps_gnss[:-100], timestamps_cam[300::3])

    # calculate_sync_dif(timestamps_gnss[:-11], timestamps_cam[33::3])

    # calculate_sync_dif(timestamps_gnss[:-21], timestamps_cam[61::3])


    # calculate_sync_dif(timestamps_gnss[1:], timestamps_cam[3::3])





