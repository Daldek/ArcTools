from feature2xyz_functions import *
import os
import re
# import pandas
import arcpy
from arcpy.sa import *  # spatial analyst module
from arcpy.da import *  # data access module
arcpy.CheckOutExtension("Spatial")

# Input
# dBase_Table = r"C:\Work\python\_programy\automatyzacja\test\raster2xyz.dbf"
# workspace = r"C:\Work\python\_programy\automatyzacja\test"
dBase_Table = arcpy.GetParameterAsText(0)
workspace = arcpy.GetParameterAsText(1)

dBase2xyz(dBase_Table, workspace)

