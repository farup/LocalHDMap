



from nuscenes.nuscenes import NuScenes



root_path = "/cluster/home/terjenf/maptr_new/data/nuscenes"
save_path_nuscnes_metadata = "/cluster/home/terjenf/NAPLab_car/data_nuscnes"
version = 'v1.0-trainval'
saved_nusce_file = 'nuscene_metadata.json'





if __name__ == "__main__":

    
    nusc = NuScenes(version=version, dataroot=root_path, verbose=True)
    samples = nusc.sample
    sample = samples[0]

    lidar_token = sample['data']['LIDAR_TOP'] 
    sd_rec = nusc.get('sample_data', sample['data']['LIDAR_TOP']) # sample data  # 'filename' = 'samples/LIDAR_TOP/n015-2018-07-18-11-07-57+0800__LIDAR_TOP__1531883530449377.pcd.bin'
    cs_record = nusc.get('calibrated_sensor', sd_rec['calibrated_sensor_token']) # callibrated sensor data 
    img_fpath=str(nusc.get_sample_data_path(sd_rec['token']))





#   def get_sample_data_path(self, sample_data_token: str) -> str:
#         """ Returns the path to a sample_data. """

#         sd_record = self.get('sample_data', sample_data_token)
#         return osp.join(self.dataroot, sd_record['filename'])








