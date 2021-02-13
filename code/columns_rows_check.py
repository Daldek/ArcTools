import arcpy
from functions import columns_rows_check
from classes import AscFile

# Input
input_folder = arcpy.GetParameterAsText(0)

# Variables
# Adam's approach - functions.py
model_domain_output_file = input_folder + str("/model_domain.asc")
land_use_output_file = input_folder + str("/land_use.asc")
roughness_output_file = input_folder + str("/roughness.asc")

columns_rows_check(land_use_output_file, model_domain_output_file, roughness_output_file)
arcpy.AddMessage('Success!')

# Piotr's approach - classes.py
model_domain = AscFile(input_folder + str("/model_domain.asc"))
land_use = AscFile(input_folder + str("/land_use.asc"))
roughness = AscFile(input_folder + str("/roughness.asc"))

if land_use.get_properties() == model_domain.get_properties() == roughness.get_properties():
    arcpy.AddMessage('Success!')
