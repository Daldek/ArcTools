# ArcTools

Python tools for manipulating a Digital Elevation Model, removing obstacles (polyline based) 
and creating an ASCII GRID file.

**Features**
- Remove culverts, bridges, etc. to allow water to flow under/through constructions
- Fill sinks to create a hydrologically correct surface
- Catchment delineation
- Create an endorheic catchments (optional)
- Create an outer boundary to keep the water inside model domain to avoid calculation errors
- Export DEM to ESRI GRID

## Install
**Requirements**
- ArcMap 10.7.1
- Git (not required, but will make things easier)

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
> In ArcMap:
- Make sure the repository on your computer is connected to your ArcMap 
(Catalog -> Connect To Folder)
- Create a Geodatabase where you will keep your results
- Create a Toolbox in a folder or in the Geodatabase (you can use existing ones if you have)
- Right click on the Toolbox -> "Add" -> "Script..."
- Choose "Store relative search path names (instead of absolute paths)"
- Find the script which you want to add
- Add parameters the the list and define the data types (can be "Any value")

## Parameters list
> Main scripts
- **Raster Manipulation**
    - Workspace
    - Culverts or river network
    - Endroheic water bodies (optional)
    - DEM
    - Channel width (default recommended value for raster with 2 m pixel resolution = 4)
    - Channel depth (recommended value = 2)
    - Sharp drop (recommended value = 10)

- **Catchment delineation**
    - Workspace
    - Raster ("AgreeDEM" from "Raster Manipulation" script)
    - Catchment Area (default = 0,25 sq.km)
    - Output file name

- **Domain Creation**
    - Workspace
    - DEM ("filled_sinks" from "Raster Manipulation" script)
    - Rise (building heights)
    - Selected catchments (Select catchment from "Catchment delineation" script 
    and save as a new feature class)
    - Buildings
    - Landuse raster
    - Inclination
    - Output folder

- **MIKE2xyz**
    - Workspace -> place where user wants to save .xyz file
    - dTable -> dbf table made basing on a sampled raster
    
## FAQ
- **What data is needed to use this tool?**
    - Digital Elevation Model and polylines with river network (at least line must
    be a culvert centerline or channel axis under a bridge that you want to open up)
- **Code does not work and I do not understand why. What should I do?**
    - Let me know about this!
- **How can I help you develop your code?**
    - Clone this repo and play with your data. Or make a pull request :)
- **Can I use shapefiles instead of geodatabses and feature classes?**
    - Not recommended. With a probability of 99,99% it will not work. Unless there is
    a "OBJECTID" column in the table of contents. One day I will try to fix it.
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

Soon ;)
