"""
This module contains DataHandler class to load and save a dataset without using its file path.
Requires to to initialize the path of data folder below.
To upload a new dataset, a file with the same name must be created in the data folder.
"""

import pandas as pd
import geopandas as gpd
import os
import json
import gzip
import pickle

import numpy as np
from pympler import asizeof
from shapely.geometry import mapping, base
from pandas import DataFrame
from typing import Any



      
class DataHandler:   
    """
    DataHandler is a data class that helps loading and saving data without using its path.
    The base_path must be initialized as the path of data folder in directory.  
       
    Supported file extensions: 
        '.csv', '.json', '.json.gz', '.geojson', '.geojson.gz', '.pkl', '.pkl.gz', '.parquet'
       
    Usage Example: 
        handler = DataHandler()
        chicago = handler.load_chicago()  
    """
    
    def __init__(self, base_path=None, base_path_2=None, base_path_3=None):
        
        if base_path == None:
            self.base_path = "/Users/kirtisoglu/Documents/GitHub/kirtisoglu-Spatial-Accessibility-Chicago/data"
        else:
            self.base_path = base_path
        
        if base_path_2 == None:
            self.base_path_2 = "/Users/kirtisoglu/Documents/GitHub/kirtisoglu-Spatial-Accessibility-Chicago/data"
        else:
            self.base_path_2 = base_path_2
            
        if base_path_3 == None:
            self.base_path_3 = "/Users/kirtisoglu/Documents/GitHub/kirtisoglu-Spatial-Accessibility-Chicago/data"
        else: 
            self.base_path_3 = base_path_3
            
            
            
        self.files = self.detect_existing_data()
        self._create_properties()
        
    
    
    def get_full_extension(self, filename):
        parts = filename.split('.')
        if len(parts) > 1:
            return '.' + '.'.join(parts[1:]), parts[0]
        return '', filename
    
    
    def detect_existing_data(self):
        """Detects files in the directory of base_path. 
        Splits and saves names of files in a dictionary."""
        files = {}
            
        for path in [self.base_path, self.base_path_2, self.base_path_3]: # iterates over files in the directories
            for filename in os.listdir(path):  # iterates over files in the directories
                full_path = os.path.join(path, filename)
                if os.path.isfile(full_path):  # checks if full_path is a file
                    extension, root = self.get_full_extension(filename)
                files[root]=(extension, filename, full_path)
        return files
    
     
    def _create_properties(self):
        """Dynamically creates properties for each file detected."""
        for name in self.files:
            setattr(self, f"load_{name}", self._create_loader(name))
            setattr(self, f"save_{name}", self._create_saver(name))

    def _create_loader(self, name):
        """Creates a loader function for a specific file."""
        def loader():
            return self.load(name)
        return loader
    
    def _create_saver(self, name):
        """Creates a saver function for a specific data."""
        def saver(data, new_path=None):
            extension, _ = self.files[name]
            file_path = new_path if new_path else self.files[name][2]
            self.save(data, file_path, extension)
        return saver

                
    def load(self, name, extension=None) -> any:
        """Load data based on the file name stored in `files` dictionary. """ 

        if extension == None:
            if name not in self.files:
                raise FileNotFoundError(f"There is no file with name {name} in the directory.")
            extension, filename, file_path = self.files[name]

        if extension == '.csv':
            return pd.read_csv(file_path)
        elif extension in {'.pkl', '.pickle'}:
            with open(file_path, 'rb') as file:
                return pickle.load(file)
        elif extension in {'.pkl.gz', '.pickle_gzip'}:
            with gzip.open(file_path, 'rb') as file:
                return pickle.load(file)
        elif extension == '.json' or extension == '.json.gz':
            open_func = gzip.open if 'gz' in extension else open
            with open_func(file_path, 'rt', encoding='utf-8') as file:
                return json.load(file)
        elif extension == '.parquet':
            return pd.read_parquet(file_path)
        elif extension == '.geojson' or extension == '.geojson_gzip':
            open_func = gzip.open if 'gz' in extension else open
            with open_func(file_path, 'rt', encoding='utf-8') as file:
                return gpd.read_file(file)
        else:
            raise ValueError(f"The file format {extension} is not supported.")



    
    def save(self, data, name, zip) -> None:
        """Save data to a file with a given name. If a file does not exists
        with that name in the directory, it first creates a file. 
        param: zip (boolean): If True, data is zipped. 
        """

        if isinstance(data, pd.DataFrame):
            extension = '.csv'
            file_path = os.path.join(self.base_path_2, f"{name}{extension}")
            data.to_csv(file_path, index=False)
            
        elif isinstance(data, dict):
            extension = '.json.gz' if zip == True else '.json'
            file_path = os.path.join(self.base_path_2, f"{name}{extension}")
            mode += 't' if zip==True else 'b'
            opener = gzip.open if zip==True else open
            with opener(file_path, mode, encoding=None if 'gzip' in name else 'utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        
        elif isinstance(data, gpd.GeoDataFrame):
            extension = '.geojson.gz' if zip==True else '.geojson'
            file_path = os.path.join(self.base_path_2, f"{name}{extension}")
            mode = 'wt' if zip==True else 'w'
            if zip==True:
                with gzip.open(file_path, mode, encoding='utf-8') as gz_file:
                    data.to_file(gz_file, driver='GeoJSON')
            else:
                data.to_file(file_path, driver='GeoJSON')
            
        elif isinstance(data, (bytes, bytearray)) or callable(getattr(data, "read", None)):
            extension = '.pkl.gz' if zip==True else '.pkl'
            file_path = os.path.join(self.base_path_2, f"{name}{extension}")
            mode = 'wb'
            opener = gzip.open if zip==True else open
            with opener(file_path, mode) as file:
                pickle.dump(data, file)

        if not file_path:
            raise ValueError("Unsupported data type for saving.")

    
        
