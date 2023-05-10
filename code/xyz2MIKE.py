from xyz2MIKE_functions import *
import arcpy
arcpy.CheckOutExtension("Spatial")

# Input
dBase_Table = arcpy.GetParameterAsText(0)
workspace = arcpy.GetParameterAsText(1)

dBase2xyz(dBase_Table, workspace)
