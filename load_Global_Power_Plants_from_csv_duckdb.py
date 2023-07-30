# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 16:39:31 2022

@author: u237679
"""

import urllib.request
import duckdb
from pathlib import Path
import shutil
import time
import zipfile

DOWNLOAD_GPP = True
LOAD_GPP = True


gpp_data_link="https://wri-dataportal-prod.s3.amazonaws.com/manual/global_power_plant_database_v_1_3.zip" # all available BFS data for CH
downloads_path = '~/Downloads'
# Dynamic path resolving, e.g. C:\Users\<user>\Downloads on Windows
# or /home/<user>/Downloads on Linux
downloads_path_str = str(Path(downloads_path).expanduser())

data_path = 'data'

base_path_str  = downloads_path_str

gpp_filepath =  base_path_str + '/global_power_plant_database_v_1_3/global_power_plant_database.csv'
gpp_table = "GPP" 

DUCK_DB = 'gpp_duck.db'
PATH_TO_DUCK_DB = data_path + "/" + DUCK_DB


load_mapping = [[gpp_filepath, gpp_table]]


def download_file(url, file = None, proxies = None, verify = None):
    time_start = time.time() 
    #create the object, assign it to a variable
    proxy = urllib.request.ProxyHandler(proxies)
    # construct a new opener using your proxy settings
    opener = urllib.request.build_opener(proxy)
    # install the openen on the module-level
    urllib.request.install_opener(opener)    
    file_path, _ = urllib.request.urlretrieve(url)
    if file:
        shutil.copy(file_path, file)
    print(file_path)
    time_end=time.time()
    print('=> Runtime of %s: %.2f second.' %("Download/Extract " + url, time_end-time_start)) 
    return file_path


def download_extract_zip(url, extract_dir, proxies = None, verify = None):
    time_start = time.time() 
    zip_path = download_file(url, file = None, proxies = proxies, verify = verify)
    with zipfile.ZipFile(zip_path, "r") as f:
        f.extractall(extract_dir + "/ch")
    time_end=time.time()
    print('=> Runtime of %s: %.2f second.' %("Download/Extract " + url, time_end-time_start)) 
    
 
      
def load_save_csv(engine, load_pair):
    time_start = time.time()    
    engine.execute("DROP TABLE IF EXISTS " + load_pair[1])    
    engine.from_csv_auto(load_pair[0]).create(load_pair[1])    
    df = engine.execute("SELECT COUNT(*) FROM " + load_pair[1]).df() 
    nbr_rows = df['count_star()'].iat[0]
    time_end=time.time() 
    print('=> Runtime of %s: %.2f second.' %("Dumping " + load_pair[0] + " to Table " + load_pair[1] 
                                             + " (" + str(nbr_rows) + " rows)", time_end-time_start))               
       
if __name__ == "__main__":
    proxies, verify =  {}, True # to be adapted when running on a corporate device/network
    download_extract_zip(gpp_data_link, extract_dir = downloads_path_str,
                        proxies = proxies, verify = verify) if DOWNLOAD_GPP else None    
    engine = duckdb.connect(database = PATH_TO_DUCK_DB)    
    load_save_csv(engine, load_mapping[0]) if LOAD_GPP else None
    engine.close()




