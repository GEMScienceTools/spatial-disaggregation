# ------------------------------------------------------------------------------
#   LOADING DEPENDENCIES AND INPUTS
# ------------------------------------------------------------------------------

import time
from _config import *
from parsers.exposure import parse_adm, parse_exposure
from util.geo import resample_raster_to_resolution, associate_grid_to_bounds, add_excepted_bounds
from util.model import write_model
from calcs.sampling import resample_assets


# ------------------------------------------------------------------------------
#   DEFINE MAIN FUNCTION
# ------------------------------------------------------------------------------

def main(mapped_field, desired_level, country_name, country_iso, group):
    ''' This function takes in an input exposure model CSV along with a
    corresponding administrative boundaries shapefile, and then resamples
    the assets in that exposure model to a finer resolution using external
    datasets (e.g. WorldPop). This requires a matching field between the input
    exposure CSV and the input admin bounds shapefile (mapped_field). This
    also requires the population raster dataset (see download_worldpop.py).
    There are several parameters specified in the _config.py, including the
    anticipated file names/directories, the desired resolution, and the
    desired coordinate reference system.'''

    # --------------------------------------------------------------------------
    #   PARSE ADMIN BOUNDS & CITIES
    # --------------------------------------------------------------------------

    # Read admin bounds, which must exist locally
    # This will also associate desired admin shp and associated field
    adm = parse_adm()

    # --------------------------------------------------------------------------
    #   MERGE RASTERS AND ASSOCIATE POINTS TO ADMIN BOUNDS
    # --------------------------------------------------------------------------

    # Arrange full path
    wp_name = f"{country_iso.lower()}_ppp_{worldpop_year}.tif"
    wp_path = os.path.join(wp_directory, wp_name)

    # Resample (aggregate) WorldPop grid to specified coarser resolution
    wp_path = resample_raster_to_resolution(
        wp_path, wp_name, res
        )

    # Associate grid points from raster data to admin bounds (at desired level)
    wp, e_wp = associate_grid_to_bounds(
        wp_path, adm, mapped_field, value_name='wp'
        )

    # Find union of failed mapped_field values (where there are no pixels)
    exceptions = list(set(e_wp))
    # Print out exceptions
    if exceptions:
        print_yellow(f"WARNING: Could not find any pixel values for: {exceptions}")

    # Combine dataframes based on row and column index
    # NOTE: This is left for future development where multiple datasets used
    df = wp.copy()

    # --------------------------------------------------------------------------
    #   ESTIMATE BUILDING COUNTS
    # --------------------------------------------------------------------------

    # Apply population_to_buildings function to estimate buildding count from
    # population estimate (Adjust as needed from the config file)
    df['count'] = population_to_buildings(df["wp"])

    # Arrange data by fields used for taxonomy mapping
    bound_names = df[mapped_field].unique()

    # --------------------------------------------------------------------------
    #   PARSE INPUT EXPOSURE DATA
    # --------------------------------------------------------------------------

    # Read in data (NOTE: I am using a db for Baloise, but can be swapped for
    # csv for GRM)
    # Also going to get list of distinct mapped_field values to understand
    # important exceptions during raster resampling
    assets, distinct_field = parse_exposure(country_name, group, mapped_field)
    important_exceptions = list(
        np.setdiff1d(distinct_field, df[mapped_field].unique())
        )
    if important_exceptions:
        print_red(f"IMPORTANT WARNING: Will not be able to properly distribute {important_exceptions}; using nearest raster values instead")
        # Add important exceptions to df and raster values from nearest point
        df = add_excepted_bounds(df, adm[desired_level], important_exceptions,
                                 mapped_field)
        # Update bound_names accordingly
        bound_names = df[mapped_field].unique()

    # Get total number of building counts for future checks
    assets_total = assets["number"].sum()

    # --------------------------------------------------------------------------
    #   SAMPLE BUILDING LOCATIONS
    # --------------------------------------------------------------------------

    # Distribute buildings bound by bound
    model = resample_assets(df, assets, bound_names, mapped_field)

    # Remove sites with no assets allocated
    model = model[(model['number'] != 0)]

    # --------------------------------------------------------------------------
    #   WRITE EXPOSURE MODEL
    # --------------------------------------------------------------------------

    # Rename columns to be in oq format
    model.rename(columns={
        "x": "lon",
        "y": "lat"
        }, inplace=True)

    # Preview result
    print(f"There are {model['number'].sum():.0f} buildings in the exposure model")
    if np.abs(model['number'].sum() - assets_total)/assets_total > thresh:
        print_red(f"IMPORTANT WARNING: The number of buildings sampled to full taxonomies is less than the known number of buildings in exposure data, which is {assets_total}")

    # --------------------------------------------------------------------------
    #   RETURN RESULTS
    # --------------------------------------------------------------------------

    # Return result
    return model

# ------------------------------------------------------------------------------
#   CALLING MAIN FUNCTION
# ------------------------------------------------------------------------------


# Run main function if called as script
if __name__ == "__main__":

    # Time code
    tic = time.perf_counter()

    # Parse arguments (group name)
    input = sys.argv[1]
    group = sys.argv[2].title()

    # Determine whether country code or short name
    key = "short_name"
    if len(input) == 3:
        key = "iso_name"

    # Read in mapping scheme
    mf = pd.read_csv(mosaic_mapping, encoding="utf-8", header=0)
    mf = mf.set_index(key)

    # Grab relevant mosaic names and country name
    country = mf.loc[input, "country_name"]

    # Get ISO name
    if key == "iso_name":
        iso_name = input
    else:
        iso_name = mf.loc[input, "iso_name"]

    # Call main function  TODO: Write query to read in exposure CSV
    model = main(field_name, adm_level, country, iso_name, group)

    # Write model for entire group
    write_model(model, f"Exposure_{group}_{country}.csv", group)

    # Print time estimate
    toc = time.perf_counter()
    print(f"Code took {toc - tic:0.4f} seconds")
