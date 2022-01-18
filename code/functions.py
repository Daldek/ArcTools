# -*- coding: utf-8 -*-

import os
import arcpy
from arcpy.sa import *  # spatial analyst module
# from arcpy.da import *  # data access module
import arcpy.cartography as ca
from classes import *
arcpy.CheckOutExtension("Spatial")


def square_km_to_cells(area, cell_size):

    """
    Converting square kilometers to number of cells in a raster
    :param area: area to be recalculated [sq. km]
    :param cell_size: raster cell size [sq. m]
    :return: number of cells with total area corresponding to the input area [-]
    """

    area = float(area)
    area = (area * 1000000) / (cell_size * cell_size)
    area = int(area)
    arcpy.AddMessage('Area unit conversion completed.')
    return area


def raster_cell_size(input_raster):

    """
    Determining of average raster cell size
    :param input_raster: a raster whose cell size will be returned
    :return: average cell size in X and Y axis [m]. Example: if the width of the cell in the X axis is 1 and the length
    in the Y axis is 3, then a value of 2 will be returned
    """

    x_direction = arcpy.GetRasterProperties_management(input_raster, "CELLSIZEX")
    y_direction = arcpy.GetRasterProperties_management(input_raster, "CELLSIZEY")
    x_direction = float(x_direction.getOutput(0))
    y_direction = float(y_direction.getOutput(0))
    cell_size = (x_direction + y_direction) / 2
    if x_direction != y_direction:
        arcpy.AddMessage('Cell size in the x-direction is different from cell size in the y-direction!')
    arcpy.AddMessage('Cell size has been calculated.')
    return cell_size


def raster_extent(input_raster):

    """
    Determining the maximum range of a raster
    :param input_raster: a raster whose range will be returned
    :return: a single string containing the extent of the raster. The order of the boundaries is
    x_min, y_min, x_max, y_max, separated by spaces
    """

    x_min = arcpy.GetRasterProperties_management(input_raster, "LEFT")
    y_min = arcpy.GetRasterProperties_management(input_raster, "BOTTOM")
    x_max = arcpy.GetRasterProperties_management(input_raster, "RIGHT")
    y_max = arcpy.GetRasterProperties_management(input_raster, "TOP")
    extent = str(x_min) + " " + str(y_min) + " " + str(x_max) + " " + str(y_max)
    return extent


def feature_extent(input_feature):

    """
    Determining the maximum range of a feature class
    :param input_feature: a feature class whose range will be returned
    :return: a single string containing the extent of the feature class. The order of the boundaries is
    x_min, y_min, x_max, y_max, separated by spaces
    """

    desc = arcpy.Describe(input_feature)
    x_max = desc.extent.XMax
    y_max = desc.extent.YMax
    x_min = desc.extent.XMin
    y_min = desc.extent.YMin
    extent = str(x_min) + " " + str(y_min) + " " + str(x_max) + " " + str(y_max)
    return extent


def fill_channel_sinks(workspace, input_raster, channel_width, channel_axis):

    """
    Fill artificially deepened channels in such a way that they do not increase channel retention. The newly dredged bed
    must not be deeper than the nearest adjacent cell
    :param workspace: a geodatabase in which results will be stored
    :param input_raster: a input raster on which the filling operation will be performed
    :param channel_width: channel width. This is the buffer that will be created around a polyline representing
    the axis of a channel, culvert, or other object
    :param channel_axis: a feature class representing a channel, culvert or other object
    :return: raster on which the filling operations were performed. The fill was constrained with a buffer around
    the polyline so that the artificially deepened channels were filled to the height of the lowest adjacent cell
    """

    # Variables
    ditch_buffer = "in_memory" + r"/ditch_buffer"
    ditch_raster = "in_memory" + r"/ditch_raster"
    ditch_fill = "in_memory" + r"/ditch_fill"

    arcpy.AddMessage('Initialization of the "raster_cell_size" function.')
    cell_size = raster_cell_size(input_raster)

    ditch_buffer_size = int(channel_width) + (2 * cell_size)
    arcpy.AddMessage('Buffer size has been recalculated.')

    # Buffer
    arcpy.Buffer_analysis(in_features=channel_axis,
                          out_feature_class=ditch_buffer,
                          buffer_distance_or_field=ditch_buffer_size)
    arcpy.AddMessage('Buffers have been created.')

    # Clip
    arcpy.Clip_management(in_raster=input_raster,
                          rectangle=raster_extent(input_raster),
                          out_raster=ditch_raster,
                          in_template_dataset=ditch_buffer,
                          clipping_geometry="ClippingGeometry",
                          maintain_clipping_extent="NO_MAINTAIN_EXTENT")
    arcpy.AddMessage('Raster has been clipped.')

    # Fill sinks
    out_fill = Fill(in_surface_raster=ditch_raster)
    out_fill.save(ditch_fill)
    arcpy.AddMessage('Sinks have been filled.')

    # Mosaic to new raster
    input_str = str(ditch_fill) + "; " + str(input_raster)  # maybe a list instead of string?
    arcpy.MosaicToNewRaster_management(input_rasters=input_str,
                                       output_location=workspace,
                                       raster_dataset_name_with_extension="Script_filled_channels",
                                       pixel_type="32_BIT_FLOAT",
                                       cellsize=cell_size,
                                       number_of_bands=1,
                                       mosaic_method="FIRST",
                                       mosaic_colormap_mode="FIRST")
    arcpy.AddMessage('New raster has been created.')

    layers_to_remove = [ditch_buffer, ditch_raster, ditch_fill]
    for layer in layers_to_remove:
        arcpy.Delete_management(layer)
    output_raster = workspace + r"/Script_filled_channels"
    arcpy.AddMessage('Sinks have been filled.')
    return output_raster


def raster_endorheic_modification(workspace, input_raster, cell_size, water_bodies):

    """
    Function whose purpose is to rasterize polygons and then use them to create NoData areas. The NoData areas
    created inside the raster, will allow water to flow not only to the outer edges, but also into these areas.
    :param workspace: a geodatabase in which results will be stored
    :param input_raster: a raster (digital elevation model) to be modified
    :param cell_size: input raster cell size
    :param water_bodies: a feature class (polygons) representing NoData areas that will be created
    :return: a modified raster
    """

    # Variables
    new_field_name = "LakeElev"
    lakes = workspace + r"/lakes"
    dem_manip = "in_memory" + r"/dem_manip"
    dem_lakes = "in_memory" + r"/dem_lakes"

    if cell_size == '#':
        cell_size = raster_cell_size(input_raster)

    # New field
    arcpy.AddField_management(in_table=water_bodies,
                              field_name=new_field_name,
                              field_type="SHORT",
                              field_alias=new_field_name,
                              field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED")
    arcpy.AddMessage("New field has been created.")

    # Assigning values to the new filed
    arcpy.CalculateField_management(in_table=water_bodies,
                                    field=new_field_name,
                                    expression=9999,
                                    expression_type="PYTHON_9.3")
    arcpy.AddMessage("Values have been assigned.")

    # Rasterization
    arcpy.PolygonToRaster_conversion(in_features=water_bodies,
                                     value_field=new_field_name,
                                     out_rasterdataset=lakes,
                                     cell_assignment="CELL_CENTER",
                                     cellsize=cell_size)
    arcpy.AddMessage("Polygons have been rasterized.")

    # Mosaic to new raster
    input_str = str(lakes) + "; " + str(input_raster)
    arcpy.MosaicToNewRaster_management(input_rasters=input_str,
                                       output_location="in_memory",
                                       raster_dataset_name_with_extension="dem_manip",
                                       pixel_type="32_BIT_FLOAT",
                                       cellsize=cell_size,
                                       number_of_bands=1,
                                       mosaic_method="FIRST",
                                       mosaic_colormap_mode="FIRST")
    arcpy.AddMessage('New raster has been created.')

    # Set null
    out_set_null = SetNull(in_conditional_raster="in_memory" + r"/dem_manip",
                           in_false_raster_or_constant="in_memory" + r"/dem_manip",
                           where_clause="Value = 9999")
    out_set_null.save(dem_lakes)
    arcpy.AddMessage('Null values have been assigned. New raster is ready.')
    layers_to_remove = [lakes, dem_manip]
    for layer in layers_to_remove:
        arcpy.Delete_management(layer)
    return dem_lakes


def raster_manipulation(workspace,
                        input_raster,
                        culverts,
                        channel_width,
                        smooth_drop,
                        sharp_drop,
                        endorheic_water_bodies,
                        creating_agreedem):

    """
    The first of the main functions. Its purpose is to remove user-selected obstacles or deepen channels.
    Removal consists of creating a feature class (polyline) representing the axis in relation to which the dredging
    operation will be performed.
    :param workspace: a geodatabase in which results will be stored
    :param input_raster: a raster (digital elevation model) to be modified
    :param culverts: a feature class (polyline) representing culverts or other objects
    :param channel_width: width of the channel (not a bottom, but a "top edge") [m]
    :param smooth_drop: expected depth of channels [m]
    :param sharp_drop: additional dredging depth to make sure the obstruction is removed [m]
    :param endorheic_water_bodies: drainless areas that we want to take into account
    :param creating_agreedem: variable that determines whether an "AgreeDEM" raster is created.
    "Script_agreeDEM" is an input raster to the "catchment_delineation" function
    :return: confirmation of successful function execution. In addition, two rasters "Script_agreeDEM"
    and "Script_filled_channels" are created
    """

    # Variables
    smooth_drop *= 1000
    sharp_drop *= 1000
    # ras = workspace + r"/ras"
    agree_str_geo = workspace + r"/agreeStrGeo"
    vec_euc_dist_geo = workspace + r"/vecEucDistGeo"
    buffer_elev_geo = workspace + r"/bufferElevGeo"
    vec_euc_allo_geo = workspace + r"/vecEucAlloGeo"
    buf_euc_allo_geo = workspace + r"/bufEucAlloGeo"
    buf_euc_dist_geo = workspace + r"/bufEucDistGeo"
    smooth_mod_geo = workspace + r"/smoothModGeo"
    sharp_mod_geo = workspace + r"/sharpModGeo"
    agree_dem_times = workspace + r"/agreeDEM_times"
    # agree_dem = workspace + r"/agreeDEM"
    layers_to_remove = [agree_str_geo, vec_euc_dist_geo, buffer_elev_geo, vec_euc_allo_geo,
                        buf_euc_allo_geo, buf_euc_dist_geo, smooth_mod_geo, sharp_mod_geo,
                        agree_dem_times]

    cell_size = raster_cell_size(input_raster)
    # ditch_buffer_size = channel_width + (2 * cell_size)

    ras = Raster(input_raster) * 1000

    # Polyline to raster
    arcpy.PolylineToRaster_conversion(in_features=culverts,
                                      value_field="OBJECTID",
                                      out_rasterdataset=agree_str_geo,
                                      cell_assignment="MAXIMUM_LENGTH",
                                      cellsize=cell_size)
    arcpy.AddMessage('Polylines have been rasterized')

    # Con
    agree_str_dem = Con(in_conditional_raster=agree_str_geo,
                        in_true_raster_or_constant=ras)
    arcpy.AddMessage('AgreeStrDem. Done.')

    # Minus
    smooth_geo = Minus(in_raster_or_constant1=agree_str_dem,
                       in_raster_or_constant2=smooth_drop)
    arcpy.AddMessage('SmoothGeo. Done.')

    # Int
    smooth_geo_int = Int(smooth_geo)
    arcpy.AddMessage('SmoothGeoInt. Done.')

    # New extent
    # arcpy.env.extent = arcpy.Extent(raster_extent(input_raster))
    left = arcpy.GetRasterProperties_management(ras, "LEFT")
    left = str(left)
    left = left.replace(',', '.')
    bottom = arcpy.GetRasterProperties_management(ras, "BOTTOM")
    bottom = str(bottom)
    bottom = bottom.replace(',', '.')
    right = arcpy.GetRasterProperties_management(ras, "RIGHT")
    right = str(right)
    right = right.replace(',', '.')
    top = arcpy.GetRasterProperties_management(ras, "TOP")
    top = str(top)
    top = top.replace(',', '.')
    arcpy.env.extent = arcpy.Extent(left, bottom, right, top)
    arcpy.AddMessage('New environment settings set.')

    # Euclidean Allocation
    arcpy.gp.EucAllocation_sa(smooth_geo_int,
                              vec_euc_allo_geo,
                              channel_width,
                              "",
                              ras,
                              "VALUE",
                              vec_euc_dist_geo,
                              "",
                              "PLANAR",
                              "",
                              "")
    arcpy.AddMessage('VecEucAlloGeo and vecEucDistGeo. Done.')

    # Is Null
    null_buff_geo = IsNull(in_raster=vec_euc_dist_geo)
    arcpy.AddMessage('NullBuffGeo. Done.')

    # Con #2
    arcpy.gp.Con_sa(null_buff_geo,
                    ras,
                    buffer_elev_geo,
                    "",
                    "")
    arcpy.AddMessage('BufferElevGeo. Done.')

    # Int #2
    buffer_elev_int = Int(in_raster_or_constant=buffer_elev_geo)
    arcpy.AddMessage('BufferElevInt. Done.')

    # Euclidean Allocation #2
    arcpy.gp.EucAllocation_sa(buffer_elev_int,
                              buf_euc_allo_geo,
                              "",
                              "",
                              ras,
                              "VALUE",
                              buf_euc_dist_geo,
                              "",
                              "PLANAR",
                              "",
                              "")
    arcpy.AddMessage('Euclidean allocation. Done.')

    # Minus #2
    buf_min_vec_allo = Minus(in_raster_or_constant1=buf_euc_allo_geo,
                             in_raster_or_constant2=vec_euc_allo_geo)
    arcpy.AddMessage('BufMinVecAllo. Done.')

    # Plus
    buf_pl_vec_dist = Plus(in_raster_or_constant1=buf_euc_dist_geo,
                           in_raster_or_constant2=vec_euc_dist_geo)
    arcpy.AddMessage('BufPlVecDist. Done.')

    # Divide
    buf_divide_geo = Divide(in_raster_or_constant1=buf_min_vec_allo,
                            in_raster_or_constant2=buf_pl_vec_dist)
    arcpy.AddMessage('BufDivideGeo. Done.')

    # Times
    buf_times_geo = Times(in_raster_or_constant1=buf_divide_geo,
                          in_raster_or_constant2=vec_euc_dist_geo)
    arcpy.AddMessage('BufTimesGeo. Done.')

    # Plus #2
    arcpy.gp.Plus_sa(vec_euc_allo_geo,
                     buf_times_geo,
                     smooth_mod_geo)
    arcpy.AddMessage('SmoothModGeo. Done.')

    # Minus #3
    arcpy.gp.Minus_sa(smooth_geo_int,
                      sharp_drop,
                      sharp_mod_geo)
    arcpy.AddMessage('SharpModGeo. Done.')

    # Mosaic
    mosaic_list = [smooth_mod_geo, sharp_mod_geo]
    arcpy.Mosaic_management(mosaic_list, buffer_elev_geo,
                            "LAST", "FIRST", "", "", "NONE")
    arcpy.AddMessage('Mosaic. Done.')

    # Con #3
    arcpy.gp.Con_sa(ras,
                    buffer_elev_geo,
                    agree_dem_times,
                    "",
                    "")
    agree_dem = Raster(workspace + r"/agreeDEM_times") / 1000
    agree_dem.save(workspace + r"/Script_agreeDEM")
    arcpy.AddMessage('AgreeDEM. Done.')

    arcpy.AddMessage('Initialization of the "fill_channel_sinks" function.')
    fill_channel_sinks(workspace, agree_dem, channel_width, culverts)
    layers_to_remove.append(workspace + r"/ditch_buffer")
    layers_to_remove.append(workspace + r"/ditch_raster")
    layers_to_remove.append(workspace + r"/ditch_fill")

    if creating_agreedem is True:
        arcpy.AddMessage("AgreeDEM will be created")
        # Endorheic basins
        if endorheic_water_bodies != "":
            arcpy.AddMessage('Initialization of the "raster_endorheic_modification" function.')
            agree_dem = raster_endorheic_modification(workspace,
                                                      agree_dem,
                                                      cell_size,
                                                      endorheic_water_bodies)
            layers_to_remove.append(workspace + r"/Script_dem_lakes")

        # Fill sinks
        out_fill = Fill(in_surface_raster=agree_dem)
        out_fill.save(workspace + r"/Script_agreeDEM")
    else:
        layers_to_remove.append(workspace + r"/Script_agreeDEM")

    for layer in layers_to_remove:
        arcpy.Delete_management(layer)

    arcpy.AddMessage('Temporary files have been removed.\n'
                     'Now you can start the catchment processing.')
    return 1


def catchment_delineation(workspace, input_dem, input_correct_dem, catchment_area):

    """
    This is the second major function. Its purpose is to delineate catchment boundaries.
    A catchment is delineated based on a Flow Accumultaion raster, which is reclassified based on the catchment_area
    parameter. All cells with a higher value are considered part of the river system. At each nodal point, which is
    where two watercourses join, a catchment is created.
    Read more: https://desktop.arcgis.com/en/arcmap/10.3/tools/spatial-analyst-toolbox/identifying-stream-networks.htm
    :param workspace: a geodatabase in which results will be stored
    :param input_dem: original elevation model before modification (see raster_manipulation function)
    :param input_correct_dem: "AgreeDEM" from function "raster_manipulation" or any other depressionless raster
    :param catchment_area: minimum catchment area beyond which formation of a new watercourse begins [sq. m]
    :return: confirmation of successful function execution. Additionally, a feature class (polyline) representing
    the river network is created, as well as a feature class (polygon) containing all generated catchments
    """

    # Variables
    streams = workspace + r"/Script_streams"
    stream_ln = "in_memory" + r"/stream_ln"
    stream_order = "in_memory" + r"/stream_order"
    temp_basin = "in_memory" + r"/tempBasin"
    temp_basin2 = "in_memory" + r"/tempBasin2"
    catchment_border = "in_memory" + r"/catchment_border"
    union_basins = "in_memory" + r"/union_basins"
    catchment_area = square_km_to_cells(catchment_area, raster_cell_size(input_dem))
    output = workspace + r"/Script_catchments"
    expression = "VALUE > " + str(catchment_area)
    arcpy.AddMessage('Expression "' + str(expression) + '"')

    # Flow direction - correct surface
    flow_dir = FlowDirection(in_surface_raster=input_dem,
                             force_flow="NORMAL",)
    arcpy.AddMessage('Flow direction raster has been built.')

    # Sink
    sink = Sink(in_flow_direction_raster=flow_dir)
    arcpy.AddMessage('Sink raster has been built.')
    sink.save(workspace + r"/Script_sink")

    # Flow direction - correct surface
    flow_dir_correct = FlowDirection(in_surface_raster=input_correct_dem,
                                     force_flow="NORMAL",)
    arcpy.AddMessage('Flow direction (correct surface) raster has been built.')
    flow_dir_correct.save(workspace + r"/Script_flow_dir")

    # Flow accumulation
    flow_acc = FlowAccumulation(in_flow_direction_raster=flow_dir_correct,
                                data_type="INTEGER")
    arcpy.AddMessage('Flow accumulation raster has been built.')
    flow_acc.save(workspace + r"/Script_flow_acc")
    
    # Flow length
    flow_ln = FlowLength(in_flow_direction_raster=flow_dir_correct,
                         direction_measurement='UPSTREAM')
    flow_ln.save(workspace + r"/Script_flow_ln")

    # Slopes
    slope = Slope(in_raster=input_correct_dem, 
                  output_measurement='DEGREE')
    slope.save(workspace + r"/Script_slope")
    arcpy.AddMessage('Slope raster hass been built.')

    # Con
    stream = Con(in_conditional_raster=flow_acc,
                 in_true_raster_or_constant=1,
                 in_false_raster_or_constant='',
                 where_clause=expression)
    arcpy.AddMessage('Conditional raster has been built.')

    # Stream link
    str_ln = StreamLink(in_stream_raster=stream,
                        in_flow_direction_raster=flow_dir_correct)
    arcpy.AddMessage('Stream links have been found.')

    # Stream Order
    str_order = StreamOrder(in_stream_raster=stream,
                            in_flow_direction_raster=flow_dir_correct,
                            order_method='STRAHLER')
    arcpy.AddMessage('Stream order has been calculated.')

    # Stream to feature
    StreamToFeature(in_stream_raster=str_ln,
                    in_flow_direction_raster=flow_dir_correct,
                    out_polyline_features=stream_ln,
                    simplify="SIMPLIFY")
    arcpy.AddMessage('Streams have been converted to features.')
    
    # Stream order to feature
    StreamToFeature(in_stream_raster=str_order,
                    in_flow_direction_raster=flow_dir_correct,
                    out_polyline_features=stream_order,
                    simplify="SIMPLIFY")
    arcpy.AddMessage('Streams have been converted to features - order.')

    # Add field
    arcpy.AddField_management(in_table=stream_order,
                              field_name="Order",
                              field_type="Long",
                              field_alias="Order",
                              field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED")
    arcpy.AddMessage('New filed has been created - order.')

    '''
    For some reason name of the newly created field is not 'Order', but 'Order_'. I don't get it,
    but it's fine as long as it works fine. I just want to leve this comment here to explain
    this potential misunderstandig
    '''
    # Calculate field
    arcpy.CalculateField_management(in_table=stream_order,
                                    field="Order_",
                                    expression="!grid_code!",
                                    expression_type="PYTHON_9.3")
    arcpy.AddMessage('Values have been calculated - order.')

    # Creating a new field map
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(stream_order)
    fieldmappings.addTable(stream_ln)
    fields_to_keep = ['grid_code', 'from_node', 'to_node', 'Order_']
    for field in fieldmappings.fields:
        if field.name not in fields_to_keep:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

    # Spatial Join
    arcpy.SpatialJoin_analysis(target_features=stream_ln,
                               join_features=stream_order,
                               out_feature_class=streams,
                               join_operation='JOIN_ONE_TO_ONE',
                               join_type='KEEP_ALL',
                               field_mapping=fieldmappings,
                               match_option='ARE_IDENTICAL_TO')
    arcpy.AddMessage('Polylines have been joined')
    
    # Delete fields
    arcpy.DeleteField_management(in_table=streams,
                                 drop_field=['Join_Count', 'TARGET_FID'])
    arcpy.AddMessage('Fields have been removed')

    # Watershed
    cat = Watershed(in_flow_direction_raster=flow_dir_correct,
                    in_pour_point_data=str_ln,
                    pour_point_field="VALUE")
    arcpy.AddMessage('The watershed raster has been built.')

    # Build raster attribute table
    arcpy.BuildRasterAttributeTable_management(in_raster=cat,
                                               overwrite="Overwrite")

    # Raster to polygon
    arcpy.RasterToPolygon_conversion(in_raster=cat,
                                     out_polygon_features=temp_basin,
                                     simplify="NO_SIMPLIFY",
                                     raster_field="VALUE")
    arcpy.AddMessage('Raster has been been converted to polygon feature.')

    # Dissolve
    arcpy.Dissolve_management(in_features=temp_basin,
                              out_feature_class=output,
                              dissolve_field="gridcode",
                              multi_part="MULTI_PART",
                              unsplit_lines="DISSOLVE_LINES")
    arcpy.AddMessage('Catchments areas have been created.')

    # Add field
    arcpy.AddField_management(in_table=output,
                              field_name="GridID",
                              field_type="LONG",
                              field_alias="GridID",
                              field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED")
    arcpy.AddMessage('New filed has been created.')

    # Calculate field
    arcpy.CalculateField_management(in_table=output,
                                    field="GridID",
                                    expression="!gridcode!",
                                    expression_type="PYTHON")
    arcpy.AddMessage('Values have been calculated.')

    # Delete field
    arcpy.DeleteField_management(in_table=output,
                                 drop_field="gridcode")
    arcpy.AddMessage('Field has been removed.')

    # Add attribute index
    arcpy.AddIndex_management(in_table=output,
                              fields="GridID",
                              index_name="GridID_Index",
                              unique="NON_UNIQUE",
                              ascending="ASCENDING")

    # Polygon to line
    arcpy.PolygonToLine_management(in_features=output,
                                   out_feature_class=catchment_border,
                                   neighbor_option="IGNORE_NEIGHBORS")
    arcpy.AddMessage('Polygons have been converted to lines.')

    # Feature to polygon
    arcpy.FeatureToPolygon_management(in_features=catchment_border,
                                      out_feature_class=temp_basin2)
    arcpy.AddMessage('Lines have been converted to polygons.')

    # Union
    arcpy.Union_analysis(in_features=[output, temp_basin2],
                         out_feature_class=union_basins,
                         join_attributes="ALL",
                         cluster_tolerance=0,
                         gaps="NO_GAPS")
    arcpy.AddMessage('Geometric union of the input features has been created.')

    # Dissolve
    arcpy.Dissolve_management(in_features=union_basins,
                              out_feature_class=output,
                              dissolve_field="GridID",
                              multi_part="MULTI_PART",
                              unsplit_lines="DISSOLVE_LINES")
    arcpy.AddMessage('Catchments have been created.')

    # Delete field
    arcpy.DeleteField_management(in_table=output,
                                 drop_field="GridID")
    arcpy.AddMessage('Field has been removed.')
    arcpy.Delete_management("in_memory")
    arcpy.AddMessage('Temporary files have been removed.')
    return output


def domain_creation(workspace, input_raster, rise, catchments, buildings, buffer_distance,
                    output_folder, simplify_catchment):

    """
    The third major function. Its purpose is to create ASCII files, ready to convert to Dfs2 and create the Mike21 model
    :param workspace: a geodatabase in which results will be stored
    :param input_raster: "Filled_channels" from function "raster_manipulation" or any other digital elevation model
    :param rise: Height of buildings [m]
    :param catchments: a feature class containing the selected catchments from the "catchment_delineation" function
    or any other polygon
    :param buildings: a feature class containing buildings (polygons)
    :param buffer_distance: size of the buffer by which the terrain model will be extended [m]
    :param output_folder: the folder where the ASCII files are to be saved
    :param simplify_catchment: variable specyfing whether the final catchment area will be simplified
    :return: confirmation of successful function execution. Additionally, 3 ASCII files are created
    """

    # Variables
    # Elevation model
    catchment = "in_memory" + r"/catchment"
    catchment_buffer = "in_memory" + r"/catchment_buffer"
    catchment_simple = "in_memory" + r"/catchment_simple"
    model_boundary = "in_memory" + r"/model_boundary"
    catchment_box = "in_memory" + r"/catchment_box"
    rasterized_buildings = "in_memory" + r"/rasterized_buildings"
    rasterized_buildings_calc = "in_memory" + r"/rasterized_buildings_calc"
    rasterized_catchment_box = "in_memory" + r"/rasterized_catchment_box"
    dem_buildings = "in_memory" + r"/dem_buildings"
    field_name = "new_elev"
    model_domain_grid = workspace + r"/model_domain_grid"  # I'd like to keep it in the workspace

    layers_to_remove = [model_domain_grid]

    # Catchment
    # Add field
    arcpy.AddField_management(in_table=catchments,
                              field_name=field_name,
                              field_type="SHORT")
    arcpy.AddMessage("New field has been created.")

    # Calculate field
    arcpy.CalculateField_management(in_table=catchments,
                                    field=field_name,
                                    expression=999,
                                    expression_type="PYTHON_9.3")
    arcpy.AddMessage("Values have been assigned.")

    # Dissolve
    arcpy.Dissolve_management(in_features=catchments,
                              out_feature_class=catchment,
                              dissolve_field=field_name,
                              multi_part="MULTI_PART")
    arcpy.AddMessage("New catchment has been created.")

    # Graphic buffer
    if buffer_distance != 0:
        arcpy.GraphicBuffer_analysis(in_features=catchment,
                                     out_feature_class=catchment_buffer,
                                     buffer_distance_or_field=buffer_distance,
                                     line_caps="SQUARE",
                                     line_joins="MITER")
        arcpy.AddMessage("The catchment area has been extended.")
        # Simplify polygon (catchment)
        if simplify_catchment is True:
            arcpy.AddMessage("Catchment areas will be simplified")
            ca.SimplifyPolygon(in_features=catchment_buffer,
                               out_feature_class=catchment_simple,
                               algorithm="POINT_REMOVE",
                               tolerance=(abs(buffer_distance) / 2),
                               error_option="NO_CHECK",
                               collapsed_point_option="NO_KEEP")
            arcpy.AddMessage("The catchment are has been simplified.")
            arcpy.CopyFeatures_management(catchment_simple, model_boundary)
        else:
            arcpy.AddMessage("Catchment area will not be simplified")
            arcpy.CopyFeatures_management(catchment_buffer, model_boundary)
    else:
        # catchment_buffer = catchment
        arcpy.CopyFeatures_management(catchment, model_boundary)

    # Minimum bounding geometry
    arcpy.MinimumBoundingGeometry_management(in_features=model_boundary,
                                             out_feature_class=catchment_box,
                                             geometry_type="ENVELOPE")

    # Buildings
    # Add field
    arcpy.AddField_management(buildings, field_name, "SHORT")
    arcpy.AddMessage("New field has been created.")

    # Calculate field
    arcpy.CalculateField_management(in_table=buildings,
                                    field=field_name,
                                    expression=rise,
                                    expression_type="PYTHON_9.3")
    arcpy.AddMessage("Values have been assigned.")

    # Feature to raster
    cell_size = raster_cell_size(input_raster)
    arcpy.FeatureToRaster_conversion(in_features=buildings,
                                     field=field_name,
                                     out_raster=rasterized_buildings,
                                     cell_size=cell_size)
    arcpy.AddMessage("Buildings have been rasterized.")

    # Raster calculator
    calc = Raster(input_raster) + Raster(rasterized_buildings)
    calc.save(rasterized_buildings_calc)
    arcpy.AddMessage("New elevations have been calculated.")

    # Mosaic to new raster
    dem_buildings_input = [rasterized_buildings_calc, input_raster]
    arcpy.MosaicToNewRaster_management(input_rasters=dem_buildings_input,
                                       output_location="in_memory",
                                       raster_dataset_name_with_extension="dem_buildings",
                                       pixel_type="32_BIT_FLOAT",
                                       cellsize=cell_size,
                                       number_of_bands=1,
                                       mosaic_method="FIRST",
                                       mosaic_colormap_mode="FIRST")
    arcpy.AddMessage("New DEM has been built.")

    # New extent
    extent = feature_extent(catchment_box)
    arcpy.AddMessage("Box extent: " + str(extent))

    # Env extent - for some unknown reason clipped rasters have the same extent as in_dem.
    # I would like to make them smaller
    desc = arcpy.Describe(catchment_box)
    x_max = desc.extent.XMax
    y_max = desc.extent.YMax
    x_min = desc.extent.XMin
    y_min = desc.extent.YMin
    arcpy.env.extent = arcpy.Extent(x_min, y_min, x_max, y_max)

    arcpy.PolygonToRaster_conversion(in_features=catchment_box,
                                     value_field="OBJECTID",
                                     out_rasterdataset=rasterized_catchment_box,
                                     cellsize=cell_size)

    left = arcpy.GetRasterProperties_management(rasterized_catchment_box, "LEFT")
    left = str(left)
    left = left.replace(',', '.')
    bottom = arcpy.GetRasterProperties_management(rasterized_catchment_box, "BOTTOM")
    bottom = str(bottom)
    bottom = bottom.replace(',', '.')
    right = arcpy.GetRasterProperties_management(rasterized_catchment_box, "RIGHT")
    right = str(right)
    right = right.replace(',', '.')
    top = arcpy.GetRasterProperties_management(rasterized_catchment_box, "TOP")
    top = str(top)
    top = top.replace(',', '.')
    arcpy.env.extent = arcpy.Extent(left, bottom, right, top)

    arcpy.AddMessage('New environment settings set.')
    arcpy.AddMessage("Model extent: " + str(left) + " " + str(bottom) + " " + str(right) + " " + str(top))

    '''
    NEW DIGITAL ELEVATION MODEL
    '''
    # Clip
    arcpy.Clip_management(in_raster=dem_buildings,
                          rectangle=extent,
                          out_raster=model_domain_grid,
                          in_template_dataset=model_boundary,
                          nodata_value="999",
                          clipping_geometry="ClippingGeometry",
                          maintain_clipping_extent="NO_MAINTAIN_EXTENT")
    arcpy.AddMessage("DEM has been clipped.")

    '''
    DATA EXPORT
    '''
    # Model domain to ASCII
    model_domain_output_file = output_folder + str("/bathymetry.asc")
    arcpy.RasterToASCII_conversion("model_domain_grid", model_domain_output_file)
    arcpy.AddMessage("Model domain raster has been exported to ASCII.")

    # Model domain to Shapefile
    arcpy.FeatureClassToShapefile_conversion(Input_Features=model_boundary,
                                             Output_Folder=output_folder)
    arcpy.AddMessage("Model boundary has been exported to Shapefile.")

    for layer in layers_to_remove:
        arcpy.Delete_management(layer)
    arcpy.Delete_management("in_memory")
    arcpy.AddMessage('Temporary files have been removed.')
    return 1


def gap_interpolation(radius, input_raster):

    """
    This function is used to interpolate the NoData cell values inside the raster
    :param radius: a radius of the area around the cell that will be used to interpolate the values [m]
    :param input_raster: a raster whose cells we want to interpolate
    :return: a new raster
    """

    out_con = Con(in_conditional_raster=IsNull(input_raster),
                  in_true_raster_or_constant=FocalStatistics(in_raster=input_raster,
                                                             neighborhood=NbrRectangle(width=radius,
                                                                                       height=radius,
                                                                                       units="CELL"),
                                                             statistics_type="MEAN"),
                  in_false_raster_or_constant=input_raster)
    arcpy.AddMessage('Gaps have been interpolated.')
    return out_con


def las2dtm(workspace_gdb, workspace_folder, input_las_catalog,
            coordinate_system, class_codes, cell_size, output_raster_name):

    """
    A function that converts las files (folder) to raster
    :param workspace_gdb: a geodatabase in which results will be stored
    :param workspace_folder: a folder in which intermediate steps will be stored
    :param input_las_catalog: a folder which contains input las data (folder)
    :param coordinate_system: las files coordinate system
    :param class_codes: desktop.arcgis.com/en/arcmap/latest/manage-data/las-dataset/lidar-point-classification.htm
    :param cell_size: output raster cell size [m]
    :param output_raster_name: output raster file name
    :return: confirmation of successful function execution
    """

    # Variables
    output_raster_path = workspace_gdb + r"/" + str(output_raster_name)
    output_las = workspace_folder + r"/LasDataset.lasd"
    class_codes = list(class_codes.split(', '))

    # Create LAS dataset
    if coordinate_system != '':
        arcpy.CreateLasDataset_management(input=input_las_catalog,
                                          out_las_dataset=output_las,
                                          folder_recursion='NO_RECURSION',
                                          spatial_reference=coordinate_system)
    else:
        arcpy.CreateLasDataset_management(input=input_las_catalog,
                                          out_las_dataset=output_las,
                                          folder_recursion='NO_RECURSION')
    arcpy.AddMessage('LAS dataset has been created.')

    # Create LAS dataset layer
    arcpy.MakeLasDatasetLayer_management(in_las_dataset=output_las,
                                         out_layer='LasLayer',
                                         class_code=class_codes,
                                         no_flag='EXCLUDE_UNFLAGGED',
                                         synthetic='EXCLUDE_SYNTHETIC')
    arcpy.AddMessage('LAS dataset layer has been made.')

    # LAS dataset to raster
    arcpy.LasDatasetToRaster_conversion(in_las_dataset='LasLayer',
                                        out_raster=output_raster_path,
                                        value_field='ELEVATION',
                                        interpolation_type='BINNING AVERAGE LINEAR',
                                        data_type='FLOAT',
                                        sampling_type='CELLSIZE',
                                        sampling_value=cell_size)
    arcpy.AddMessage('Raster has been created.')
    return 1


def mask_below_threshold(workspace, cell_size, input_raster, threshold_value, nodata_polygons, domain):

    """
    Function that removes raster cells with a value lower than the threshold value.
    Example: If we have a raster with water depth, flow velocity, and elevation, and our parameter is a minimum depth
    of 10 cm, then we can perform this analysis on the depth raster and use the mask created this way to crop
    the other rasters
    :param workspace: a geodatabase in which results will be stored
    :param cell_size: input raster cell size [m]
    :param input_raster: a raster to be modified
    :param threshold_value: cells with a value lower than this will be converted to NoData [-]
    :param nodata_polygons: additional NoData areas
    :param domain: a feature class (polygon) limiting the scope of analysis
    :return: a raster that will be used as a mask to crop other rasters
    """

    # Variables
    layers_to_remove = []

    # Input raster properties
    extent = raster_extent(input_raster)
    min_depth = arcpy.GetRasterProperties_management(input_raster, "MINIMUM")
    max_depth = arcpy.GetRasterProperties_management(input_raster, "MAXIMUM")
    if cell_size == '':
        arcpy.AddMessage('Initialization of the "raster_cell_size" function.')
        raster_cell_size(input_raster)

    # Reclassify input raster
    reclassified_input_raster = Reclassify(in_raster=input_raster,
                                           reclass_field="VALUE",
                                           remap=RemapRange([[min_depth, threshold_value, 0],
                                                             [threshold_value, max_depth, 1]]))

    # Check in polygons should be removed from raster
    if nodata_polygons != '':
        rasterized_polygons = "in_memory" + r"/rasterized_polygons"
        depth_buildings_raster = "in_memory" + r"/depth_buildings_raster"
        layers_to_remove.extend([rasterized_polygons, depth_buildings_raster])
        # Polygons to raster
        arcpy.PolygonToRaster_conversion(in_features=nodata_polygons,
                                         value_field="OBJECTID",
                                         out_rasterdataset=rasterized_polygons,
                                         cell_assignment="CELL_CENTER",
                                         cellsize=cell_size)
        arcpy.AddMessage("Polygons have been rasterized.")

        # Properties of the new raster
        max_id = arcpy.GetRasterProperties_management(rasterized_polygons, "MAXIMUM")

        # Reclassify rasterized polygons
        reclassified_poly_raster = Reclassify(in_raster=rasterized_polygons,
                                              reclass_field="VALUE",
                                              remap=RemapRange([[0, max_id, 0]]))
        arcpy.AddMessage("Rasterized polygons have been reclassified.")

        # Mosaic to new raster
        arcpy.MosaicToNewRaster_management(input_rasters=[reclassified_poly_raster, reclassified_input_raster],
                                           output_location="in_memory",
                                           raster_dataset_name_with_extension="depth_buildings_raster",
                                           pixel_type="1_BIT",
                                           cellsize=cell_size,
                                           number_of_bands=1,
                                           mosaic_method="FIRST",
                                           mosaic_colormap_mode="FIRST")
        arcpy.AddMessage('New raster has been created.')

        # Set null
        out_set_null = SetNull(in_conditional_raster=depth_buildings_raster,
                               in_false_raster_or_constant="in_memory" + r"/depth_buildings_raster",
                               where_clause="Value = 0")
    else:
        # Set null
        out_set_null = SetNull(in_conditional_raster=reclassified_input_raster,
                               in_false_raster_or_constant=reclassified_input_raster,
                               where_clause="Value = 0")
    arcpy.AddMessage("Null values have been assigned.")

    # Check if the domain was predefined
    if domain != '':
        out_set_null_clipped = "in_memory" + r"/out_set_null_clipped"
        layers_to_remove.append(out_set_null_clipped)
        # Clip
        arcpy.Clip_management(in_raster=out_set_null,
                              rectangle=extent,
                              out_raster=out_set_null_clipped,
                              in_template_dataset=domain,
                              clipping_geometry="ClippingGeometry",
                              maintain_clipping_extent="NO_MAINTAIN_EXTENT")
        arcpy.AddMessage('Raster has been clipped.')

        # Extract by mask
        # created_mask = ExtractByMask(input_raster, out_set_null_clipped)
        created_mask = out_set_null_clipped
    else:
        # Extract by mask
        # created_mask = ExtractByMask(input_raster, out_set_null)
        created_mask = out_set_null

    arcpy.AddMessage('Mask has been created.')
    for layer in layers_to_remove:
        arcpy.Delete_management(layer)
    arcpy.AddMessage('Temporary files have been removed.')
    return created_mask


def mask_and_export(mask, in_rasters, output_folder):
    a = 0  # counter
    b = len(in_rasters)
    base_ascii = ''
    mask_extension = mask.split('.')[-1]

    # If the input mask file is an ASCII file, it will be used as a reference raster for validating new ASCII files
    if mask_extension == 'asc':
        base_ascii = AscFile(mask)

    for raster in in_rasters:
        arcpy.AddMessage('Progress: ' + str(a) + r'/' + str(b))
        out_ascii_file = os.path.splitext(os.path.basename(raster))[0]  # extracting a raster name
        out_ascii_file = str(output_folder) + '/' + out_ascii_file + '.asc'

        # Phase 1 - processing
        masked_raster = ExtractByMask(raster, mask)
        arcpy.RasterToASCII_conversion(masked_raster, out_ascii_file)

        # Phase 2 - validation
        if a == 0 and base_ascii == '':
            base_ascii = AscFile(out_ascii_file)
        else:
            another_ascii = AscFile(out_ascii_file)
            if base_ascii.get_properties() != another_ascii.get_properties():
                arcpy.AddMessage("/nRaster files does not match!/n")
        arcpy.AddMessage('Ok!')
        a += 1

    arcpy.AddMessage('Progress: ' + str(a) + r'/' + str(b))
    arcpy.AddMessage("Raster files have been exported.")


def fastighetskartan_markytor_simplifed(workspace, in_feature_class):
    # Let's start with green areas
    out_green_areas_lyr = "S_green_areas_layer"
    out_green_areas_fc = workspace + r"\S_green_areas"
    sql_expression = "DETALJTYP = 'BEBHÖG' OR DETALJTYP = 'BEBLÅG' OR DETALJTYP = 'ODLFRUKT' OR DETALJTYP = 'ODLÅKER' OR DETALJTYP = 'SKOGBARR' OR DETALJTYP = 'SKOGLÖV' OR DETALJTYP = 'ÖPMARK'"
    arcpy.AddMessage(sql_expression)
    arcpy.MakeFeatureLayer_management(in_features=in_feature_class,
                                      out_layer=out_green_areas_lyr)
    arcpy.management.SelectLayerByAttribute(in_layer_or_view=out_green_areas_lyr,
                                            selection_type='NEW_SELECTION',
                                            where_clause=sql_expression)
    arcpy.CopyFeatures_management(in_features=out_green_areas_lyr,
                                  out_feature_class=out_green_areas_fc)
    arcpy.AddMessage("Green areas have been exported")

    # Hard areas
    out_hard_areas_lyr = "S_hard_areas_layer"
    out_hard_areas_fc = workspace + r"\S_hard_areas"
    sql_expression = "DETALJTYP = 'ÖPTORG' OR DETALJTYP = 'BEBIND' OR DETALJTYP = 'BEBSLUT'"
    arcpy.AddMessage(sql_expression)
    arcpy.MakeFeatureLayer_management(in_features=in_feature_class,
                                      out_layer=out_hard_areas_lyr)
    arcpy.management.SelectLayerByAttribute(in_layer_or_view=out_hard_areas_lyr,
                                            selection_type='NEW_SELECTION',
                                            where_clause=sql_expression)
    arcpy.CopyFeatures_management(in_features=out_hard_areas_lyr,
                                  out_feature_class=out_hard_areas_fc)
    arcpy.AddMessage("Hard areas have been exported")

    # Last but not least - water
    out_water_lyr = "S_water_layer"
    out_water_fc = workspace + r"\S_water"
    sql_expression = "DETALJTYP = 'VATTEN'"
    arcpy.AddMessage(sql_expression)
    arcpy.MakeFeatureLayer_management(in_features=in_feature_class,
                                      out_layer=out_water_lyr)
    arcpy.management.SelectLayerByAttribute(in_layer_or_view=out_water_lyr,
                                            selection_type='NEW_SELECTION',
                                            where_clause=sql_expression)
    arcpy.CopyFeatures_management(in_features=out_water_lyr,
                                  out_feature_class=out_water_fc)
    arcpy.AddMessage("Water bodies have been exported")
    return 1
