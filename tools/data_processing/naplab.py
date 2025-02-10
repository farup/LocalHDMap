import json
import math
import os
import os.path as osp
import sys
import time
from datetime import datetime
from typing import Tuple, List, Iterable
import pickle



class NapLab:
    """
    Database class for nuScenes to help query and retrieve information from the database.
    """

    def __init__(self, dataroot: str, trip: str)

        self.dataroot = dataroot
        self.trip = trip

        self.table_names = ['calibrated_sensor',
                            'ego_pose', 'log', 'scene', 'sample', 'sample_data']


        self.calibrated_sensor = self.__load_table__('calibrated_sensor')
        self.ego_pose = self.__load_table__('ego_pose')
        self.log = self.__load_table__('log')
        self.scene = self.__load_table__('scene')
        self.sample = self.__load_table__('sample')
        self.sample_data = self.__load_table__('sample_data')


        if verbose:
            for table in self.table_names:
                print("{} {},".format(len(getattr(self, table)), table))
            print("Done loading in {:.3f} seconds.\n======".format(time.time() - start_time))

    @property
    def table_root(self) -> str:
        """ Returns the folder where the tables are stored for the relevant trip. """
        return osp.join(self.dataroot, self.trip)


    def __load_table__(self, table_name) -> dict:
        """ Loads a table. """
        with open(os.join(self.table_root, f"{table_name}.pkl"), 'wb') as f:
            table = pickle.load(f)
        return table


    def __make_reverse_index__(self, verbose: bool) -> None:
        """
        De-normalizes database to create reverse indices for common cases.
        :param verbose: Whether to print outputs.
        """
        start_time = time.time()
        if verbose:
            print("Reverse indexing ...")

        # Store the mapping from token to table index for each table.
        self._token2ind = dict()
        for table in self.table_names:
            self._token2ind[table] = dict()

            for ind, member in enumerate(getattr(self, table)):
                self._token2ind[table][member['token']] = ind

        # for record in self.sample_data:
        #     if record['is_key_frame']:
        #         sample_record = self.get('sample', record['sample_token'])
        #         sample_record['data'][record['channel']] = record['token']

        if verbose:
            print("Done reverse indexing in {:.1f} seconds.\n======".format(time.time() - start_time))


    def get(self, table_name: str, token: str) -> dict:
        """
        Returns a record from table in constant runtime.
        :param table_name: Table name.
        :param token: Token of the record.
        :return: Table record. See README.md for record details for each table.
        """
        assert table_name in self.table_names, "Table {} not found".format(table_name)

        return getattr(self, table_name)[self.getind(table_name, token)]
    

    def getind(self, table_name: str, token: str) -> int:
        """
        This returns the index of the record in a table in constant runtime.
        :param table_name: Table name.
        :param token: Token of the record.
        :return: The index of the record in table, table is an array.
        """
        return self._token2ind[table_name][token]


    def getind(self, table_name: str, token: str) -> int:
        """
        This returns the index of the record in a table in constant runtime.
        :param table_name: Table name.
        :param token: Token of the record.
        :return: The index of the record in table, table is an array.
        """
        return self._token2ind[table_name][token]




if __name__ == "__main__": 


    dataroot ="/cluster/home/terjenf/NAPLab_car/data"
    trip="Trip077"

    naplab = NapLab(dataroot=dataroot, trip=trip)


    print("heis")










