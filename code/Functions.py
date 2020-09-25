import arcpy
from arcpy.sa import *  # spatial analyst module
# from arcpy.da import *  # data access module
arcpy.CheckOutExtension("Spatial")


def square_km_to_cells(area, cell_size):
    area = float(area)
    area = (area * 1000000) / (2 * cell_size)
    area = int(area)
    arcpy.AddMessage('Area unit conversion completed.')
    return area


def raster_cell_size(input_raster):
    x_direction = arcpy.GetRasterProperties_management(input_raster, "CELLSIZEX")
    y_direction = arcpy.GetRasterProperties_management(input_raster, "CELLSIZEY")
    x_direction = float(x_direction.getOutput(0))
    y_direction = float(y_direction.getOutput(0))
    input_raster_cell_size = (x_direction + y_direction) / 2
    if x_direction != y_direction:
        arcpy.AddMessage('Cell size in the x-direction is different from cell size in the y-direction!')
    arcpy.AddMessage('Cell size has been calculated.')
    return input_raster_cell_size


def raster_extent(input_raster):
    x_min = arcpy.GetRasterProperties_management(input_raster, "LEFT")
    y_min = arcpy.GetRasterProperties_management(input_raster, "BOTTOM")
    x_max = arcpy.GetRasterProperties_management(input_raster, "RIGHT")
    y_max = arcpy.GetRasterProperties_management(input_raster, "TOP")
    extent = str(x_min) + " " + str(y_min) + " " + str(x_max) + " " + str(y_max)
    return extent


def feature_extent(input_feature):
    desc = arcpy.Describe(input_feature)
    x_max = desc.extent.XMax
    y_max = desc.extent.YMax
    x_min = desc.extent.XMin
    y_min = desc.extent.YMin
    extent = str(x_min) + " " + str(y_min) + " " + str(x_max) + " " + str(y_max)
    return extent


def fill_channel_sinks(workspace, input_raster, channel_width, channel_axis):
    # Variables
    ditch_buffer = workspace + r"/ditch_buffer"
    ditch_raster = workspace + r"/ditch_raster"
    ditch_fill = workspace + r"/ditch_fill"

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
    input_str = str(ditch_fill) + "; " + str(input_raster)  # maybe list instead of string?
    arcpy.MosaicToNewRaster_management(input_rasters=input_str,
                                       output_location=workspace,
                                       raster_dataset_name_with_extension="filled_channels",
                                       pixel_type="32_BIT_FLOAT",
                                       cellsize=cell_size,
                                       number_of_bands=1,
                                       mosaic_method="FIRST",
                                       mosaic_colormap_mode="FIRST")
    arcpy.AddMessage('New raster has been created.')

    layers_to_remove = [ditch_buffer, ditch_raster, ditch_fill]
    for layer in layers_to_remove:
        arcpy.Delete_management(layer)
    output_raster = workspace + r"/filled_channels"
    arcpy.AddMessage('Sinks have been filled.')
    return output_raster


def raster_endorheic_modification(workspace, input_raster, cell_size, water_bodies):
    # Variables
    new_field_name = "LakeElev"
    lakes = workspace + r"/lakes"
    dem_manip = workspace + r"/dem_manip"
    dem_lakes = workspace + r"\dem_lakes"

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
                                       output_location=workspace,
                                       raster_dataset_name_with_extension="dem_manip",
                                       pixel_type="32_BIT_FLOAT",
                                       cellsize=cell_size,
                                       number_of_bands=1,
                                       mosaic_method="FIRST",
                                       mosaic_colormap_mode="FIRST")
    arcpy.AddMessage('New raster has been created.')

    # Set null
    out_set_null = SetNull(in_conditional_raster=workspace + r"/dem_manip",
                           in_false_raster_or_constant=workspace + r"/dem_manip",
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
                        endorheic_water_bodies):
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
    bottom = arcpy.GetRasterProperties_management(ras, "BOTTOM")
    right = arcpy.GetRasterProperties_management(ras, "RIGHT")
    top = arcpy.GetRasterProperties_management(ras, "TOP")
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
    """
    THESE APPROACHES DO NOT WORK - WRONG NUMBER OF BANDS

    arcpy.Mosaic_management(inputs="smooth_mod_geo;sharp_mod_geo",
                            target=buffer_elev_geo,
                            mosaic_type="LAST",
                            colormap="FIRST")
    """
    arcpy.AddMessage('Mosaic. Done.')

    # Con #3
    arcpy.gp.Con_sa(ras,
                    buffer_elev_geo,
                    agree_dem_times,
                    "",
                    "")
    agree_dem = Raster(workspace + r"/agreeDEM_times") / 1000
    agree_dem.save(workspace + r"/AgreeDEM")
    arcpy.AddMessage('AgreeDEM. Done.')

    arcpy.AddMessage('Initialization of the "fill_channel_sinks" function.')
    fill_channel_sinks(workspace, agree_dem, channel_width, culverts)
    layers_to_remove.append(workspace + r"/ditch_buffer")
    layers_to_remove.append(workspace + r"/ditch_raster")
    layers_to_remove.append(workspace + r"/ditch_fill")

    # Endorheic basins
    if endorheic_water_bodies != "#":
        arcpy.AddMessage('Initialization of the "raster_endorheic_modification" function.')
        agree_dem = raster_endorheic_modification(workspace,
                                                  agree_dem,
                                                  cell_size,
                                                  endorheic_water_bodies)
        layers_to_remove.append(workspace + r"/dem_lakes")

    # Fill sinks
    out_fill = Fill(in_surface_raster=agree_dem)
    out_fill.save(workspace + r"/AgreeDEM")

    for layer in layers_to_remove:
        arcpy.Delete_management(layer)

    arcpy.AddMessage('Temporary files have been removed.\n'
                     'Now you can start the catchment processing.')
    return 1


def catchment_delineation(workspace, input_raster, catchment_area, output):
    # Variables
    streams = workspace + r"/streams"
    temp_basin = workspace + r"/tempBasin"
    temp_basin2 = workspace + r"/tempBasin2"
    catchment_border = workspace + r"/catchment_border"
    union_basins = workspace + r"/union_basins"
    layers_to_remove = [temp_basin, temp_basin2, catchment_border, union_basins]
    catchment_area = square_km_to_cells(catchment_area, raster_cell_size(input_raster))
    output = workspace + r"/" + output
    expression = "VALUE > " + str(catchment_area)
    arcpy.AddMessage('Expression "' + str(expression) + '"')

    # Flow direction
    flow_dir = FlowDirection(in_surface_raster=input_raster,
                             force_flow="NORMAL",)
    arcpy.AddMessage('Flow direction raster has been built.')

    # Flow accumulation
    flow_acc = FlowAccumulation(in_flow_direction_raster=flow_dir,
                                data_type="INTEGER")
    arcpy.AddMessage('Flow accumulation raster has been built.')

    # Con
    stream = Con(in_conditional_raster=flow_acc,
                 in_true_raster_or_constant=1,
                 in_false_raster_or_constant='',
                 where_clause=expression)
    arcpy.AddMessage('Conditional raster has been built.')

    # Stream link
    str_ln = StreamLink(in_stream_raster=stream,
                        in_flow_direction_raster=flow_dir)
    arcpy.AddMessage('Stream links have been found.')

    # Stream to feature
    StreamToFeature(in_stream_raster=str_ln,
                    in_flow_direction_raster=flow_dir,
                    out_polyline_features=streams,
                    simplify="NO_SIMPLIFY")
    arcpy.AddMessage('Streams have been converted to features.')

    # Watershed
    cat = Watershed(in_flow_direction_raster=flow_dir,
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
    for layer in layers_to_remove:
        arcpy.Delete_management(layer)
    arcpy.AddMessage('Temporary files have been removed.')
    return output


def domain_creation(workspace, input_raster, rise, catchments, buildings, landuse_raster, inclination, output_folder):
    # Variables
    # Elevation model
    catchment = workspace + r"/catchment"
    catchment_buffer = workspace + r"/catchment_buffer"
    rasterized_buffer = workspace + r"/rasterized_buffer"
    rasterized_buildings = workspace + r"/rasterized_buildings"
    rasterized_buildings_calc = workspace + r"/rasterized_buildings_calc"
    clipped_dem = workspace + r"/clipped_dem"
    dem_buildings = workspace + r"/dem_buildings"
    field_name = "new_elev"

    # Land use raster
    land_use_clip = workspace + r"/land_use_clip"
    landuse_grid = workspace + r"/landuse_grid"

    # Roughness rasters
    slope_grid = workspace + r"/slope_grid"
    steep_slopes_grid = workspace + r"/steep_slopes_grid"
    steep_slopes_grid_clip = workspace + r"/steep_slopes_grid_clip"

    layers_to_remove = [catchment_buffer, rasterized_buffer,
                        rasterized_buildings, rasterized_buildings_calc,
                        clipped_dem, dem_buildings,
                        slope_grid]

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
                                       output_location=workspace,
                                       raster_dataset_name_with_extension="dem_buildings",
                                       pixel_type="32_BIT_FLOAT",
                                       cellsize=cell_size,
                                       number_of_bands=1,
                                       mosaic_method="FIRST",
                                       mosaic_colormap_mode="FIRST")
    arcpy.AddMessage("New DEM has been built.")

    '''
    NEW DIGITAL ELEVATION MODEL
    '''
    # Clip
    extent = raster_extent(input_raster)
    arcpy.Clip_management(in_raster=dem_buildings,
                          rectangle=extent,
                          out_raster=clipped_dem,
                          in_template_dataset=catchment,
                          nodata_value="999",
                          clipping_geometry="ClippingGeometry",
                          maintain_clipping_extent="NO_MAINTAIN_EXTENT")
    arcpy.AddMessage("DEM has been clipped.")

    # Buffer
    buffer_dist = int(cell_size) * 2
    arcpy.Buffer_analysis(in_features=catchment,
                          out_feature_class=catchment_buffer,
                          buffer_distance_or_field=buffer_dist,
                          line_side="OUTSIDE_ONLY")
    arcpy.AddMessage("Buffer has been created.")

    # Rasterize
    arcpy.FeatureToRaster_conversion(in_features=catchment_buffer,
                                     field=field_name,
                                     out_raster=rasterized_buffer,
                                     cell_size=cell_size)
    arcpy.AddMessage("Buffer has been rasterized.")

    # Mosaic to new raster
    output_mosaic_list = [clipped_dem, rasterized_buffer]
    arcpy.MosaicToNewRaster_management(input_rasters=output_mosaic_list,
                                       output_location=workspace,
                                       raster_dataset_name_with_extension="model_domain_grid",
                                       pixel_type="32_BIT_FLOAT",
                                       cellsize=cell_size,
                                       number_of_bands=1,
                                       mosaic_method="FIRST",
                                       mosaic_colormap_mode="FIRST")
    arcpy.AddMessage("Domain raster has been built.")

    '''
    LAND USE GRID
    '''
    # Clip
    arcpy.Clip_management(in_raster=landuse_raster,
                          rectangle=extent,
                          out_raster=land_use_clip,
                          in_template_dataset=catchment,
                          clipping_geometry="ClippingGeometry",
                          maintain_clipping_extent="NO_MAINTAIN_EXTENT")
    arcpy.AddMessage("Land use raster has been clipped.")

    # Mosaic to new raster
    land_use_mosaic_list = [land_use_clip, rasterized_buffer]
    arcpy.MosaicToNewRaster_management(input_rasters=land_use_mosaic_list,
                                       output_location=workspace,
                                       raster_dataset_name_with_extension="landuse_grid",
                                       pixel_type="16_BIT_UNSIGNED",
                                       cellsize=cell_size,
                                       number_of_bands=1,
                                       mosaic_method="FIRST",
                                       mosaic_colormap_mode="FIRST")
    arcpy.AddMessage("Lands use raster has been built.")

    '''
    ROUGHNESS GRID (LAND USE + STEEP SLOPES)
    '''
    # Slope
    arcpy.Slope_3d(dem_buildings, slope_grid, "DEGREE", 1.0)
    arcpy.AddMessage("Slopes have been calculated.")

    # Reclassify
    additional_roughness = Reclassify(slope_grid, "Value", RemapRange([[0, inclination, "NODATA"],
                                                                       [inclination, 180, 998]]))
    additional_roughness.save(steep_slopes_grid)
    arcpy.AddMessage("Raster has been reclassified.")

    # Clip
    arcpy.Clip_management(in_raster=steep_slopes_grid,
                          rectangle=extent,
                          out_raster=steep_slopes_grid_clip,
                          in_template_dataset=catchment,
                          clipping_geometry="ClippingGeometry",
                          maintain_clipping_extent="NO_MAINTAIN_EXTENT")
    arcpy.AddMessage("Land use raster has been clipped.")

    # Mosaic to new raster
    roughness_mosaic_list = [steep_slopes_grid_clip, landuse_grid]
    arcpy.MosaicToNewRaster_management(input_rasters=roughness_mosaic_list,
                                       output_location=workspace,
                                       raster_dataset_name_with_extension="roughness_grid",
                                       pixel_type="16_BIT_UNSIGNED",
                                       cellsize=cell_size,
                                       number_of_bands=1,
                                       mosaic_method="FIRST",
                                       mosaic_colormap_mode="FIRST")
    arcpy.AddMessage("Roughness raster has been built.")

    '''
    DATA EXPORT
    '''
    # Model domain to ASCII
    model_domain_output_file = output_folder + str("/model_domain.asc")
    arcpy.RasterToASCII_conversion("model_domain_grid", model_domain_output_file)
    arcpy.AddMessage("Model domain raster has been exported to ASCII.")

    # Land use to ASCII
    land_use_output_file = output_folder + str("/land_use.asc")
    arcpy.RasterToASCII_conversion("landuse_grid", land_use_output_file)
    arcpy.AddMessage("Land use raster has been exported to ASCII.")

    # Roughness to ASCII
    roughness_output_file = output_folder + str("/roughness.asc")
    arcpy.RasterToASCII_conversion("roughness_grid", roughness_output_file)
    arcpy.AddMessage("Roughness raster has been exported to ASCII.")

    # ASCII validation
    comlumns_rows_check(land_use_output_file, model_domain_output_file,
                        roughness_output_file)

    for layer in layers_to_remove:
        arcpy.Delete_management(layer)
    return 1


def gap_interpolation(radius, input_raster):
    out_con = Con(in_conditional_raster=IsNull(input_raster),
                  in_true_raster_or_constant=FocalStatistics(in_raster=input_raster,
                                                             neighborhood=NbrRectangle(width=radius,
                                                                                       height=radius,
                                                                                       units="CELL"),
                                                             statistics_type="MEAN"),
                  in_false_raster_or_constant=input_raster)
    arcpy.AddMessage('Gaps have been interpolated.')
    return out_con

def comlumns_rows_check(land_use_path, model_domain_path, roughness_path):
    land_use = open(land_use_path, "r")
    model_domain = open(model_domain_path, "r")
    roughness = open(roughness_path, "r")
    model_domain_columns = model_domain.readline()
    model_domain_rows = model_domain.readline()
    model_domain_x = model_domain.readline()
    model_domain_y = model_domain.readline()
    land_use_columns = land_use.readline()
    land_use_rows = land_use.readline()
    land_use_x = land_use.readline()
    land_use_y = land_use.readline()
    roughness_columns = roughness.readline()
    roughness_rows = roughness.readline()
    roughness_x = roughness.readline()
    roughness_y = roughness.readline()
    if model_domain_columns == land_use_columns and\
            land_use_columns == roughness_columns:
        arcpy.AddMessage('Number of columns match')
    else:
        arcpy.AddMessage('Wrong number of columns')
    if model_domain_rows == land_use_rows and\
            land_use_rows == roughness_rows:
        arcpy.AddMessage('Number of rows match')
    else:
        arcpy.AddMessage('Wrong number of rows')
    if model_domain_x == land_use_x and\
            land_use_x == roughness_x:
        arcpy.AddMessage('X match')
    else:
        arcpy.AddMessage('Wrong X')
    if model_domain_y == land_use_y and\
            land_use_y == roughness_y:
        arcpy.AddMessage('Y match')
    else:
        arcpy.AddMessage('Wrong Y')
