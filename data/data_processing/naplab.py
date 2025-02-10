import json
import math
import os
import os.path as osp
import sys
import time
from datetime import datetime
from typing import Tuple, List, Iterable








class NapLab:
    """
    Database class for nuScenes to help query and retrieve information from the database.
    """

    def __init__(self, dataroot: str)

        self.dataroot = dataroot


        self.table_names = ['sensor', 'calibrated_sensor',
                            'ego_pose', 'log', 'scene', 'sample', 'sample_data']



    def __load_table__(self, table_name) -> dict:
        """ Loads a table. """
        with open(osp.join(self.table_root, '{}.json'.format(table_name))) as f:
            table = json.load(f)
        return table








