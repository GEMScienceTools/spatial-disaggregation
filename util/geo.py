# Load dependencies
from _config import *


# Resample one raster to desired grid resolution
def resample_raster_to_resolution(original_raster, file_name, res,
                                  sample_agg="average"):
    ''' This function resamples the existing raster data (e.g. WorldPop) to
    a coarser desired resolution (res) and aggregated the values using the
    sample_agg. At the time of creation, there was no SUM option and so
    the AVERAGE option was used'''

    # Confirm raster file exists
    if not os.path.exists(original_raster):
        print_red(f"ERROR: You need to download raster data first, could not find {original_raster}.")

    # Arrange new file name
    new_raster = original_raster.replace(file_name, "resampled_" + file_name)

    # Call GDAL translate
    kwargs = {"xRes": res, "yRes": res, "resampleAlg": sample_agg,
              "format": 'GTiff'}
    _ = gdal.Translate(new_raster, original_raster, **kwargs)

    # Return new path
    return new_raster


# Get dataframe of grid points from raster and associate with admin bounds
def associate_grid_to_bounds(raster, adm_level, mapped_field,
                             remove_zeros=False, value_name='val'):
    ''' This function iterates through all rows of a GeoDataFrame and extracts
    raster values within those bounds, then returns a dataframe with all raster
    data associated with attributes from that GeoDataFrame and geolocation.
    Optional argument remove_zeros will remove values equal to 0 if set to
    True.'''

    # Get dimensions
    n = adm_level.shape[0]

    # Initialize list to store dataframes, which can be collapsed later
    dfs = [None for _ in range(0, n)]

    # Initialize list for exceptions
    exceptions = []

    # Iterate through each boundary such that the boundary ID can be retained
    for i, adm in adm_level.iterrows():
        # Get geometry and extent of admin region
        geom = adm.geometry
        # If geometry is polygon, convert to list for rasterio.mask
        if type(geom) == shapely.geometry.polygon.Polygon:
            geom = [geom]
        # Perform mask on raster data
        with rasterio.open(raster) as src:
            # Mask to boundary
            out_image, out_transform = rasterio.mask.mask(src, geom, crop=True)
            no_data = src.nodata
        # Extract data from masked image
        data = out_image[0]  # get first (only) band
        # Remove nodata values
        if remove_zeros:
            r, c = np.where((data != no_data) & (data != 0))
            values = np.extract((data != no_data) & (data != 0), data)
        else:
            r, c = np.where(data != no_data)
            values = np.extract(data != no_data, data)
        # Convert cell row and col to point x and y
        T1 = out_transform * Affine.translation(0.5, 0.5)  # ref. pixel centre
        rc2xy = lambda r, c: (c, r) * T1
        # Construct dataframe from raster data
        dfs[i] = gpd.GeoDataFrame({'col':c,'row':r, value_name:values})
        # Implement try-except for cases where mask produces no pixels
        if dfs[i].shape[0] > 0:
            dfs[i]['x'] = dfs[i].apply(
                lambda row: rc2xy(row.row, row.col)[0], axis=1
                )
            dfs[i]['y'] = dfs[i].apply(
                lambda row: rc2xy(row.row, row.col)[1], axis=1
                )
            dfs[i]['geometry'] = dfs[i].apply(
                lambda row: shapely.geometry.Point(row['x'], row['y']), axis=1
                )
            # Include information from vector data (admin bounds)
            for col, val in adm.iteritems():
                if col == "geometry":
                    pass  # skip poly geom from admin bound, as this is pt data
                else:
                    dfs[i][col] = val
        # Warn user if mask produced no pixels
        else:
            # TODO: Figure out an approach to handle these exceptions
            exceptions.append(adm[mapped_field])

    # Concatenate across all bounds
    df = pd.concat(dfs, axis=0)

    # Return result
    return df, exceptions


# Added excepted bounds into dataframe and sample nearest
def add_excepted_bounds(df, adm, important_exceptions, mapped_field):
    ''' This function handles the case where certain boundaries have no grid
    cell with corresponding data from the external datasets (e.g. WorldPop).
    This case might occur for small admin boundaries where the desired
    resolution (res) is too large and therefore no grid cell is associated with
    that boundary. Since there is no grid cell associated, the boundary's
    representative_point will instead be used for the geolocation'''

    # Get last index and create range of new indicies
    i_new = df.index[-1]
    idx_new = list(range(i_new+1, i_new+1+len(important_exceptions)))

    # Construct new df with rows equal to important_exceptions
    df_new = pd.DataFrame(data={
                                mapped_field: important_exceptions
                            },
                          columns=df.columns,
                          index=idx_new
                          )

    # Construct geometry from centroid of adm level
    for exception in important_exceptions:
        # Get repr. point from matching mapped_field (dissolve in case of dup)
        idx = (adm[mapped_field] == exception)
        area = adm[idx].to_crs(desired_crs).geometry.area
        point = adm[idx].to_crs(desired_crs).geometry.representative_point()
        x, y = point.x, point.y
        # Check if more than one entity retrieved, and take larger if so
        if point.shape[0] > 1:
            i_larger = area.idxmax()
            point, x, y = point[i_larger], x[i_larger], y[i_larger]
        # Arrange in df_new
        jdx = (df_new[mapped_field] == exception)
        df_new.loc[jdx, 'x'] = float(x)
        df_new.loc[jdx, 'y'] = float(y)

    # Add geometry
    df_new['geometry'] = df_new.apply(
        lambda row: shapely.geometry.Point(row['x'], row['y']), axis=1
        )

    # Find nearest smod_string and built_string from raster grid
    df_new = ckdnearest(df_new, df, gdfB_cols=['smod_string', 'built_string', 'count'])
    # Maintain index and replace 0 values with small number
    df_new.index = idx_new
    df_new.loc[df_new['count'] == 0, 'count'] = 0.1

    # Append new dataframe rows
    df = pd.concat([df, df_new], axis=0)

    return df.copy()
