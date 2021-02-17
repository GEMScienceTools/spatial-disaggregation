# Load dependencies
from _config import *


# Define function to parse admin bounds shapefile
def parse_adm():
    ''' This function reads in a local shapefile of administrative boundaries,
     of which the input exposure CSV is based upon.'''

    # Determine desired number of adm levels
    file_path = os.path.join(shp_directory, shp_file)

    # Initialize geodataframes and read files
    adm = gpd.read_file(file_path, encoding='utf-8').to_crs(desired_crs)

    # Return result
    return adm


# Parse input exposure CSV
def parse_exposure(country, group, mapped_field):
    ''' This function reads in a local CSV of the input exposure model,
     of which the input exposure CSV is based upon.'''

    # Arrange path
    file_name = f"Exposure_{group}_{country}.csv"
    file_path = os.path.join(exp_directory, file_name)

    # Read in CSV
    assets = pd.read_csv(file_path, encoding="utf-8")

    # Convert mapped_field into consistent format
    assets = assets.rename(columns={
        mapped_field.lower(): mapped_field
        })

    # Get distinct field values from query
    field_values = assets[mapped_field].unique()

    return assets, field_values
