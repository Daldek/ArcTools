# ArcTools

Python tools for playing with a Digital Elevation Model, removing obstacles (on the basis of
polylines) and creating an ASCII GRID file.

**Features**
- Remove culverts, bridges, etc. to allow water to flow under/through constructions
- Fill sinks to create a hydrologically correct surface
- Catchment delineation
- Create an endorheic catchments
- Create an outer boundary to keep the water inside model domain to avoid calculation errors
- Export DEM to ESRI GRID

## Install
**Requirements**
- ArcMap 10.7.1
- Git (not required, but will make things easier)

**Install**

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
- Create a Geodatabase where you will keep your Toolbox
- Create a Toolbox in the Geodatabase (you can use existing ones if you have)
- Right click on the Toolbox -> "Add" -> "Script..."
- Choose "Store relative search path names (instead of absolute paths)"
- Find the script which you want to add
- Add parameters the the list and define the data types (can be "Any value")
- The list of parameters can be found in each script file, here is an example:
```python
parameter_name = arcpy.GetParameterAsText(0)
```
## FAQ
- **What data is needed to use this tool?**
    - Digital Elevation Model and polylines with river network (at least line must
    be a culvert centerline or channel axis under a bridge that you want to open up)
- **Code does not work and I do not understand why. What should I do?**
    - Let me know about this!
- **How can I help you develop your code?**
    - Clone this repo and play with your data. Or make a pull request :)
- **Can I use shapefiles instead of geodatabses and feature classes?**
    - Not recommended. With a probability of 99,99% it will not work. UUnless there is
    a "OBJECTID" column in the table of contents. One day I will try to fix it.
- **Can I specify the buffer and depth for each polyline?**
    - No. It is a fixed value which you specify before you start the script. This
    feature has top priority.
- **Buffer? What buffer? What are you talking about?**
    - In the "DEM_manipulation" script is a parameter called "maximum_distance". This
    parameter specifies the top width of the channel which will be created in the elevation
    model.
- **What is the "smooth_drop" parameter?**
    - Here you should insert the channel depth.
- **Then, what is the "sharp_drop?"**
    - To be sure that the culver (or anything else) is open, the middle part should be
    much deeper. This will prevent overfilling the sink areas. IMPORTANT:
    the "DEM_manipulation" tool should be use dtwice: first run to delineate catchments
    (in this case "sharp_drop value can be higher than 10m), second run: to remove culverts
    from modeling. After second run you should pick the "AgreeDEM" raster, because sinks are
    not filled. "AgreeDEM" is an input file to the third tool "Model_area". It might sounds
    complicated, but I will fix this issue!

## Documentation

Soon ;)