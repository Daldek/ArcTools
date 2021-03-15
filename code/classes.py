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
