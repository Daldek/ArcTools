# ArcTools

Python tools for manipulating a Digital Elevation Model, removing obstacles (polyline based) 
and creating an ASCII GRID files (elevation model, land use and roughness).

**Features**
- Remove culverts, bridges, etc. to allow water to flow under/through constructions
- Fill sinks to create a hydrologically correct (drainless) surface
- Catchment delineation [More](https://desktop.arcgis.com/en/arcmap/10.3/tools/spatial-analyst-toolbox/how-watershed-works.htm)
- Create an endorheic catchments (optional) [Wikipedia](https://en.wikipedia.org/wiki/Endorheic_basin)
- Export DEM to Esri GRID (ASCII) [Wikipedia](https://en.wikipedia.org/wiki/Esri_grid)

## Install
**Requirements**
- ArcMap 10.7 or later
- Git (not required, but will make things easier). [Wikipedia](https://en.wikipedia.org/wiki/Git)

**Installation**

> From GitHub to your machine:
- You can simply download this repository and put anywhere you like, but make sure
ArcGIS has access to it.
- You can also clone this repository using Git. Git makes life easier, when you work on
the code that is "under construction" (but not only!), because you will be able to update
your code more efficiently.

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

If you have made changes to the code yourself and want to discard them (permanently):
```shell
$ git reset --hard
```

> In ArcMap:
- Make sure the repository on your computer is connected to your ArcMap 
(Catalog -> Connect To Folder)
- Create a Geodatabase where you want to keep your results
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
    and save as a new feature class)
    - Buildings (feature class)
    - buffer distance (selected catchment will be enlarged by this width) [m]
    - Output folder

- **MIKE2xyz**
    - Workspace -> place where user wants to save .xyz file
    - dTable -> dbf table made basing on a sampled raster

- **Equidistant_rain**
    - input_excel -> none equidistant rain data file
    - output_excel

## FAQ
- **What data is needed to use this tool?**
    - Digital Elevation Model and polylines with river network (at least line must
    be a culvert centerline or channel axis under a bridge that you want to open up)
- **Code does not work and I do not understand why. What should I do?**
    - Let me know about this!
- **How can I help you develop your code?**
    - Clone this repo and play with your data. Or make a pull request :)
- **Can I use shapefiles instead of geodatabses and feature classes?**
    - No.
- **Can I specify the buffer and depth for each polyline?**
    - No. It is a fixed value which is specified before you start the script.
- **Buffer? What buffer? What are you talking about?**
    - In the "DEM_manipulation" script is a parameter called "maximum_distance". This
    parameter specifies the top width of the channel which will be created in the elevation
    model.
- **What is the "smooth_drop" parameter?**
    - Here you should insert the channel depth.
- **Then, what is the "sharp_drop?" parameter**
    - To be sure that the culver (or anything else) is open, the middle part should be
    much deeper. This will prevent overfilling the sink areas.

## Documentation

ಠ_ಠ
