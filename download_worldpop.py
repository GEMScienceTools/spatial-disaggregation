# Load dependencies
from _config import *
import urllib.request


# Parse function with grid; FIXME: Support other resolutions from WP beyond 1km
def download_worldpop(iso, year=2020, res="1km"):
    ''' This function downloads a raster file of population estimates from
    WorldPop. At the moment, this will download the 2020 population estimate
    at a 1km resolution for the desired country. This can be later expanded to
    download the 100m dataset, or (where possible) a direct estimate of the
    number of buildings.'''

    # Arrange url; defeault  - 1km, UN adj
    url = f'ftp://ftp.worldpop.org.uk/GIS/Population/Global_2000_2020_1km_UNadj/{year}/{iso.upper()}/{iso.lower()}_ppp_2020_1km_Aggregated_UNadj.tif'
    if res == "100m":
        # If requested, use 100m, UN adj
        url = f'ftp://ftp.worldpop.org.uk/GIS/Population/Global_2000_2020/{year}/{iso.upper()}/{iso.lower()}_ppp_{year}_UNadj.tif'

    # Submit request
    r = urllib.request.urlopen(url)

    # Arrange desired name
    wp_name = f"{iso.lower()}_ppp_{year}.tif"

    # Find relevant file
    file_path = os.path.join(wp_directory, wp_name)

    # Write to raster path
    f = open(file_path, 'wb')
    f.write(r.read())
    f.close()

    return f"Downloaded to {file_path}"


# Run main function if called as script
if __name__ == "__main__":

    # Parse arguments (group name)
    iso = sys.argv[1]
    year = 2020
    res = "1km"
    if len(sys.argv) > 2:
        res = sys.argv[2]

    # Call function
    download_worldpop(iso, year, res)
