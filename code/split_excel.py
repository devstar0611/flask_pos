import pandas as pd
import sys
import os
from icecream import ic
from pathlib import Path
import argparse
module_path = os.path.dirname(os.path.realpath(__file__))
filepath = module_path+'/Output_Products.xlsx'

loc = ("C://senthil-code//freelancer//jay//mycode//List_details.xlsx")
parser = argparse.ArgumentParser()
parser.add_argument("file_path", type=Path)
p = parser.parse_args()
fil = p.file_path
module_path = os.path.dirname(os.path.realpath(__file__))
Path(module_path+"/input").mkdir(parents=True, exist_ok=True)
if not os.path.exists(module_path+'input'):
    os.makedirs(module_path+'input')
# create an excel file object
reader = pd.ExcelFile(fil)

# loop through all sheet names
for sheet in reader.sheet_names:
    #read in data
    df = pd.read_excel(reader, sheet_name=sheet)
    # save data to excel in this location
    # '~/desktop/new files/a.xlsx', etc.
    df.to_excel(module_path+'/input/'+sheet+'.xlsx', index=False)
    argg=module_path+'/input/'+sheet+'.xlsx'
    pat=module_path+'/input/'+sheet+'.bat'
    patt=module_path+'/input/async_working.py'
    with open(pat,'w+') as myBat:
        myBat.write(r'c:\Users\justs\Documents\target\python.exe '+patt+' "'+argg+'"')
        
    
