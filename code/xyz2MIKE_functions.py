import os
import re

dBase_path = r"C:\Users\PLPD00293\Documents\!Temp\fin_script_dBase.dbf"
save_path = r"C:\Users\PLPD00293\Documents\!Temp"


def dbf_to_txt(dbf_path, txt_location):
    # Czy nie lepiej byloby zrobic po prostu kopie pliku i po prostu zmienic rozszerzenie?
    txt_path = txt_location + r"\dbf2xyz.txt"
    new_txt_file = open(txt_path, "w")
    dbf_file = open(dbf_path)

    for line in dbf_file:
        new_txt_file.writelines("{}\n".format(line))

    dbf_file.close()
    new_txt_file.close()
    print("1")
    return txt_path


def tab_to_new_line(txt_path):
    input_txt = open(txt_path, "w+")
    working_data = input_txt.read()
    working_data.replace(" ", "n")
    # working_data.replace("-", "\n-")
    # working_data = working_data.replace(" ", "\n")
    # working_data = working_data.replace("-", "\n-")
    # working_data = working_data.replace("", "")

    # input_txt.write(working_data)
    # input_txt.close()
    print(working_data)
    return txt_path


def del_empty_lines(input_table_from_table_organizer):
    output_file_with_no_empty_lines = input_table_from_table_organizer + \
                                      r"\dbf2xyz_no_empty_lines.txt"
    input_table_from_table_organizer = input_table_from_table_organizer + \
                                       r"\dbf2xyz.txt"

    with open(input_table_from_table_organizer) as infile,\
            open(output_file_with_no_empty_lines, "w") as outfile:
        for line in infile:
            if not line.strip():
                continue  # skip the empty line
            outfile.write(line)


def remove_headlines(output_folder):
    output_file = output_folder + r"/raster2xyz_no_empty_lines.txt"

    f = open(output_file, "w+")
    lines = f.readlines()
    del lines[0:3]
    for line in lines:
        f.write(line)
    f.close()


def table_creation(infilelocation):
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
    dBase_p = dBase_Table
    save_p = workspace

    dbf_to_txt(dBase_p, save_p)
    tab_to_new_line(save_p)
    del_empty_lines(save_p)
    remove_headlines(save_p)
    table_creation(save_p)
    del_empty_lines(save_p)
    xyz2mike(save_p)
    # arcpy.AddMessage('Success!')


# dBase2xyz(dBase_path, save_path)
out1 = dbf_to_txt(dBase_path, save_path)
tab_to_new_line(out1)
# del_empty_lines(save_path)
