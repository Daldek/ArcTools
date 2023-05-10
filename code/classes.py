import os.path
import arcpy

class AscFile:

    """
    This class analyzes an ASCII file header. This analysis can be used to compare 2 (or more) ASCII files
    used in Mike21 models
    """

    def __init__(self, path):

        """
        Class initialization
        :param path: path to an ASCII (ESRI grid) file
        """

        self.path = path
        self.asc_file = ''
        self.ncols = ''
        self.nrows = ''
        self.xllconer = ''
        self.yllcorner = ''
        self.cellsize = ''
        self.nodata_value = ''

    def get_properties(self):
        self.asc_file = open(self.path, "r")
        self.ncols = " ".join(self.asc_file.readline().split())
        self.nrows = " ".join(self.asc_file.readline().split())
        self.xllconer = " ".join(self.asc_file.readline().split())
        self.yllcorner = " ".join(self.asc_file.readline().split())
        self.cellsize = " ".join(self.asc_file.readline().split())
        self.nodata_value = " ".join(self.asc_file.readline().split())
        self.asc_file.close()  # is this necessary?
        return self.ncols, self.nrows, self.xllconer, self.yllcorner, self.cellsize, self.nodata_value


class AutomationWorkspace:

    """
    This class checks whether a dedicated geodatabase exists and, if not, creates one at the location of the main geodatabase.
    """

    def __init__(self, main_gdb_path):
        self.main_gdb_path = main_gdb_path
        self.gdb_name = 'Automation.gdb'
        self.inputdataset_name = 'Input'
        self.outputdataset_name = 'Output'
        self.folder_path = ''

    def verification(self):
        self.folder_path = os.path.dirname(self.main_gdb_path)
        self.path = self.folder_path + r'/' + self.gdb_name

        if arcpy.Exists(self.path):
            print("I'm already there!")
            if arcpy.Exists(self.path + r'/' + self.inputdataset_name) and arcpy.Exists(self.path + r'/' + self.outputdataset_name):
                print('All good!')
            elif arcpy.Exists(self.path + r'/' + self.inputdataset_name) and not arcpy.Exists(self.path + r'/' + self.outputdataset_name):
                print('But a feature dataset is missing!')
                arcpy.CreateFeatureDataset_management(self.path, self.outputdataset_name)
            elif not arcpy.Exists(self.path + r'/' + self.inputdataset_name) and arcpy.Exists(self.path + r'/' + self.outputdataset_name):
                print('But a feature dataset is missing!')
                arcpy.CreateFeatureDataset_management(self.path, self.inputdataset_name)
            else:
                print('But datasets are missing!')
                arcpy.CreateFeatureDataset_management(self.path, self.inputdataset_name)
                arcpy.CreateFeatureDataset_management(self.path, self.outputdataset_name)

        else:
            print('Creation of a new geodatabase')
            arcpy.CreateFileGDB_management(self.folder_path, self.gdb_name)
            arcpy.CreateFeatureDataset_management(self.path, self.inputdataset_name)
            arcpy.CreateFeatureDataset_management(self.path, self.outputdataset_name)
