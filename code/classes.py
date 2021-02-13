class AscFile:

    def __init__(self, path):
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
