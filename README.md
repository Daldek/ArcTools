# ArcTools

Python tools for manipulating a Digital Elevation Model, removing obstacles (polyline based), creating an ASCII GRID file (elevation model) and more!

**Features**
- Remove culverts, bridges, etc. to allow water to flow under/through constructions
- Fill sinks to create a hydrologically correct (drainless) surface
- Catchment delineation [More](https://desktop.arcgis.com/en/arcmap/10.3/tools/spatial-analyst-toolbox/how-watershed-works.htm)
- Create an endorheic catchments (optional) [Wikipedia](https://en.wikipedia.org/wiki/Endorheic_basin)
- Export DEM to Esri GRID (ASCII) [Wikipedia](https://en.wikipedia.org/wiki/Esri_grid)
- Analyse land use vetor file (Sweden, Fastighetskartan), simplify and convert to GRID
- Delineate the longest flowpath
- Detect infrastruture at (flood) risk

## Install
**Requirements**
- ArcMap 10.8 or ArcGIS Pro 2.9 (or newer)
- Git (not required, but will make things easier). [Wikipedia](https://en.wikipedia.org/wiki/Git)

**Installation**

> From GitHub to your machine:
- You can simply download this repository and put anywhere you like, but make sure ArcGIS has access to it.
- You can also clone this repository using Git. Git makes life easier, when you work on the code that is "under construction" (but not only!), because you will be able to update your code more efficiently.

To clone this repository, open the location where you want to save it and type "cmd" in the
top bar (where is the path to the folder). Then copy paste this code:

```shell
$ git clone https://github.com/Daldek/ArcTools.git
```

To update the ArcTools repository, go to the folder which has been created and copy paste
this code:

```shell
$ git pull https://github.com/Daldek/ArcTools.git
```

To pull from e.g. the develop branch, use the following code:
```shell
$ git pull https://github.com/Daldek/ArcTools.git develop
```

If you have made changes to the code yourself and want to discard them (permanently):
```shell
$ git reset --hard
```

> In ArcMap/ArcGIS:
- Make sure the project folder on your computer is connected to ArcMap/ArcGIS (Catalog -> Connect To Folder)
- Create a Geodatabase where you want to keep your results. Remember to avoid special characters and non-latin letters in the path.
- Create a Toolbox in a folder or in the Geodatabase (you can use existing ones if you have)
- Right click on the Toolbox -> "Add" -> "Script..."
- Choose "Store relative search path names (instead of absolute paths)"
- Find the script which you want to add
- Add parameters to the list and define the data types

## Parameters list
> Main scripts
- **Raster Manipulation**
    - Workspace
    - Culverts or river network (feature class)
    - Endroheic water bodies (optional, feature class)
    - DEM
    - Channel width (default recommended value for raster with 2 m pixel resolution ≥ 4) [m]
    - Channel depth [m]
    - Sharp drop (recommended value ≥ 10) [m]
    - Confirmation of raster execution "AgreeDEM"

- **Catchment delineation**
    - Workspace
    - Raster ("AgreeDEM" from "Raster Manipulation" script)
    - Catchment Area (default = 0,25) [sq. km]

- **Domain Creation**
    - Workspace
    - DEM ("filled_sinks" from "Raster Manipulation" script)
    - Rise (building heights, recommended value = 2) [m]
    - Selected catchments (Select catchment from "Catchment_delineation" script (feature class)
    and save as a new feature class. You can also add a feature class from another source)
    - Buildings (feature class)
    - buffer distance (selected catchment will be enlarged by this width. For the value 0, simplification of the catchment polygon will be automatically ommited) [m]
    - Output folder
    - Catchment simlification (Parameter indicates whether the output polygon will be simplifield)

- **Fastighetskartan**
    - Workspace
    - Input feature class which is Fastighetskartan that could be obtained from Lantmateriet

- **Infrastructure at risk**
    - Workspace
    - List of water depths
    - Vector file representing the infrastructure we would like to investigate (polylines and polygons only)
    - Water depth raster (from HEC-RAS, MIKE by DHI or any other hydraulic software)


## FAQ
- **What data is needed to use this tool?**
    - Digital Elevation Model and polylines with river network (at least line must be a culvert centerline or channel axis under a bridge that you want to open up)
- **Code does not work and I do not understand why. What should I do?**
    - Let me know about this!
- **How can I help you develop your code?**
    - Clone this repo and play with your data. Or make a pull request :)
- **Can I use shapefiles instead of geodatabses and feature classes?**
    - No.
- **Can I specify the buffer and depth for each polyline?**
    - No. It is a fixed value which is specified before you start the script.
- **Buffer? What buffer? What are you talking about?**
    - In the "DEM_manipulation" script is a parameter called "maximum_distance". This parameter specifies the top width of the channel which will be created in the elevation
    model.
- **What is the "smooth_drop" parameter?**
    - Here you should insert the channel depth.
- **Then, what is the "sharp_drop?" parameter**
    - To be sure that the culver (or anything else) is open, the middle part should be
    much deeper. This will prevent overfilling the sink areas.
- **What kind of infrastructure can I analyse?**
    - It can be anything you want, as long as it is represented as polylines or polygons. Hece you can find flooded roads, buildings, your own land or see whether you could go to your favouire grocery store to buy more chocolate bars if your village is flooded and you happen to live on a hilltop.


## TODO list
- Create tools to generate a dedicated geodatabase for ArcTools to create copies of the original input files and store the results in it
- 'Jordartskartan' is to be rewritten from ModelBuilder to Python
- Integration with MikeTools to support conversion of GIS files directly to Dfs2 and vice versa
- Integration with SCALGO to get data faster
- Integrate with Vattenwebb and SMHI webpage (alternatively this can be done in QGIS as I have already created a project to get data from these sites)
- Development first hydrological tools
- Documentation


## Documentation

ಠ_ಠ
