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

DOWNLOAD_BFS_EGID = True
DOWNLOAD_POST_PLZ_POP = False
LOAD_EINGANG = True
LOAD_GEBAEUDE = True
LOAD_WOHNUNG = True
LOAD_CODES = True
LOAD_PLZ_POP = False

bfs_data_link="https://public.madd.bfs.admin.ch/ch.zip" # all available BFS data for CH
post_plz_pop_data_link = 'https://swisspost.opendatasoft.com/api/explore/v2.1/catalog/datasets/bevoelkerung_proplz/exports/csv?lang=de&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B'
downloads_path = '~/Downloads'
# Dynamic path resolving, e.g. C:\Users\<user>\Downloads on Windows
# or /home/<user>/Downloads on Linux
downloads_path_str = str(Path(downloads_path).expanduser())

data_path = 'data'

base_path_str  = downloads_path_str

gwr_eingang_filepath =  base_path_str + '/ch/eingang_entree_entrata.csv'
gwr_eingang_table = "ENTRANCE" 

gwr_gebaeude_filepath = base_path_str + '/ch/gebaeude_batiment_edificio.csv'
gwr_gebaeude_table = "BUILDING" 

gwr_wohnung_filepath = base_path_str + '/ch/wohnung_logement_abitazione.csv'
gwr_wohnung_table = "DWELLING" 

gwr_codes_filepath =  base_path_str + '/ch/kodes_codes_codici.csv'
gwr_codes_table = "CODES" 

plz_pop_filepath = base_path_str +"/bevoelkerung_proplz.csv"
plz_pop_table = "PLZ_POP" 


DUCK_DB = 'gwr_ch_bfs_duck.db'
PATH_TO_DUCK_DB = data_path + "/" + DUCK_DB


load_mapping = [[gwr_eingang_filepath,gwr_eingang_table],
                [gwr_gebaeude_filepath,gwr_gebaeude_table],
                [gwr_wohnung_filepath,gwr_wohnung_table],
                [gwr_codes_filepath,gwr_codes_table],
                [plz_pop_filepath, plz_pop_table]
                ]

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
    download_extract_zip(bfs_data_link, extract_dir = downloads_path_str,
                        proxies = proxies, verify = verify) if DOWNLOAD_BFS_EGID else None    
    download_file(post_plz_pop_data_link, file=plz_pop_filepath, proxies = proxies, verify = None) if DOWNLOAD_POST_PLZ_POP else None    
    engine = duckdb.connect(database = PATH_TO_DUCK_DB)    
    load_save_csv(engine, load_mapping[0]) if LOAD_EINGANG else None
    load_save_csv(engine, load_mapping[1]) if LOAD_GEBAEUDE else None
    load_save_csv(engine, load_mapping[2]) if LOAD_WOHNUNG else None
    load_save_csv(engine, load_mapping[3]) if LOAD_CODES else None
    load_save_csv(engine, load_mapping[4]) if LOAD_PLZ_POP else None
    #df = engine.execute(gwr_building_community_v)
    #df = engine.execute(gwr_dwelling_community_v)
    engine.close()




