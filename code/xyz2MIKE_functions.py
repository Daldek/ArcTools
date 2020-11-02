import os
import re
# import pandas
# import arcpy
# from arcpy.sa import *  # spatial analyst module
# from arcpy.da import *  # data access module
# arcpy.CheckOutExtension("Spatial")

dBase_path = r"C:\Work\python\_programy\automatyzacja\feature2raster_from_point\pointZdBase.dbf"
save_path = r"C:\Work\python\_programy\automatyzacja\feature2raster_from_point"


#----------------------change_dBase_to_TXT_format-------------------------------
def change_to_TXT(dBase_path, save_path):

    # links
    save_path = save_path + r"/raster2xyz.txt"

    new_txt_file = open(save_path, "w")
    for line in open(dBase_path):
        new_txt_file.writelines("{}\n".format(line))
    new_txt_file.close()


#-----------------------------table_organizer-----------------------------------
def tab_to_new_line(save_path):
#--------------------------replacing_part---------------------------------------

    # links
    save_path = save_path + r"/raster2xyz.txt"

    input_xyz = open(save_path, "r+")
    working_data = input_xyz.read()
    working_data = working_data.replace(" ", "\n")

#----------------------------saving_part----------------------------------------
    save_data = open(save_path, "w+")
    save_data.write(working_data)

#----------------------------below_zero_to_new_line-----------------------------
    input_xyz = open(save_path, "r+")
    working_data = input_xyz.read()
    working_data = working_data.replace("-", "\n-")

#----------------------------saving_part----------------------------------------
    save_data = open(save_path, "w+")
    save_data.write(working_data)

# ----------------------------last_char-----------------------------------------
    input_xyz = open(save_path, "r+")
    working_data = input_xyz.read()
    working_data = working_data.replace("", "")

# ----------------------------saving_part---------------------------------------
    save_data = open(save_path, "w+")
    save_data.write(working_data)


#--------------------------delete_empty_lines-----------------------------------
def del_empty_lines(input_table_from_table_organizer):

    # links
    output_file_with_no_empty_lines = input_table_from_table_organizer + \
                                      r"/raster2xyz_no_empty_lines.txt"
    input_table_from_table_organizer = input_table_from_table_organizer + \
                                       r"/raster2xyz.txt"

    with open(input_table_from_table_organizer) as infile,\
            open(output_file_with_no_empty_lines, "w") as outfile:
        for line in infile:
            if not line.strip():
                continue  # skip the empty line
            outfile.write(line)


#---------------------------delete_headlines------------------------------------
def remove_headlines(del_empty_lines_output):

    # links
    del_empty_lines_output = del_empty_lines_output \
                             + r"/raster2xyz_no_empty_lines.txt"

    remove_headlines = open(del_empty_lines_output, "r")
    remove_lines = remove_headlines.readlines()
    remove_headlines.close()

    del remove_lines[0:3]
    # del remove_lines[-1]

    removed_headlines = open(del_empty_lines_output, "w+")

    for headline in remove_lines:
        removed_headlines.write(headline)

    removed_headlines.close()


#---------------------------delete_unnecessary_rows-----------------------------
def table_creation(infilelocation):

    # Links
    infilename = infilelocation + r"/raster2xyz_no_empty_lines.txt"
    outfilename = infilelocation + r"/raster2xyz.txt"

    with open(infilename, "r") as infile:
        lines = infile.readlines()

    grouping_pattern = re.compile("^(\d{1,3})$")

    with open(outfilename, "w") as outfile:
        for line in lines:
            match = re.match(grouping_pattern, line)
            if match:
                newline = re.sub(grouping_pattern, r" ", line)
                outfile.write(newline)
            else:
                outfile.write(line)


#----------------------------------xyz2mike-------------------------------------
def xyz2mike(infilelocation):
#------------------------------list_preparation---------------------------------

# Links
    infilename = infilelocation + r"/raster2xyz_no_empty_lines.txt"
    outfilename = infilelocation + r"/raster2xyz.txt"

# couple of list for data holding
    xyz_list = []
    multiple_list = []
    xyz_list_no_new_lines = []
    multiple_list_no_new_lines = []
    xyz_correct_values = []

    with open(infilename, "r") as infile:
        lines = infile.readlines()

#patterns for regex to identify neccessary parts of list
    pattern_multiple = re.compile("\d{1,3}$")
    pattern_delete = re.compile("\D{1,2}\d{1,3}$")
    pattern_xyz = re.compile("(\d{1,}\.\d{1,})")
    pattern_delete_xyz = re.compile("(\d{1,}\.\d{1,}\D{1,2})")

#geting rid of unneccessary parts of txt file
    with open(outfilename, "w") as outfile:
        for line in lines:
            match = re.match(pattern_xyz, line)
            if match:
                newline = re.sub(pattern_delete_xyz, r"", line)
            #     outfile.write(newline)
            # else:
            #     outfile.write(line)
            multiple_list.append(newline)

    with open(outfilename, "w") as outfile:
        for line in lines:
            match = re.match(pattern_xyz, line)
            if match:
                newline = re.sub(pattern_delete, r"", line)
                outfile.write(newline)
            else:
                outfile.write(line)
            xyz_list.append(newline)
    os.remove(outfilename)
    os.remove(infilename)

#creating list that contains x, y and z cooridnates
    for element in xyz_list:
        xyz_list_no_new_lines.append(element.strip())
    for element in multiple_list:
        multiple_list_no_new_lines.append(element.strip())

    for num_xyz, num_mulitplie in zip(xyz_list_no_new_lines,
                                      multiple_list_no_new_lines):
        xyz_correct_values.append(
            round(float(num_xyz)*(10**float(num_mulitplie)), 2))

    x_list = xyz_correct_values[0::3]
    y_list = xyz_correct_values[1::3]
    z_list = xyz_correct_values[2::3]

    list_count = 0
    while list_count <= (len(y_list) - 1):
        if int(y_list[list_count]) == int(z_list[list_count]):
            del x_list[list_count]
            del y_list[list_count]
            del z_list[list_count]
            list_count = 0
        list_count = list_count + 1

#saveing to txt part
    import csv

    save_file = infilelocation + r"/xyz2Mike.xyz"
    zip(x_list, y_list, z_list)
    with open(save_file, 'w') as output:
        writer = csv.writer(output, delimiter = " ")
        writer.writerows(zip(x_list, y_list, z_list))
    quit()


def dBase2xyz(dBase_Table, workspace):

    # Input files
    dBase_path = dBase_Table
    save_path = workspace

    # functions in order to run
    change_to_TXT(dBase_path, save_path)
    tab_to_new_line(save_path)
    del_empty_lines(save_path)
    remove_headlines(save_path)
    table_creation(save_path)
    del_empty_lines(save_path)
    xyz2mike(save_path)
    # arcpy.AddMessage('Success!')


dBase2xyz(dBase_path, save_path)

# change_to_TXT(dBase_path, save_path)
