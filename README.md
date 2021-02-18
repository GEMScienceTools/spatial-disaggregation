# Exposure spatial disaggregation

## Overview

The purpose of this code is to distribute a coarse exposure model to a finer resolution based on additional datasets (e.g. WorldPop).

![Example application of code to commercial assets in Austria](demo_austria.png?raw=true "Example application of code to commercial assets in Austria")

## Dependencies

To install all dependencies using ``pip``, run the following command:

    pip install -r requirements.txt

The dependencies are as follows:

* numpy
* pandas
* geopandas
* rasterio
* shapely^
* osgeo
* GDAL^^

*^There is currently a known issue where importing from shapely returned an AssertionError when loading the GEOS library. This can be resolved by installing shapely before fiona, rasterio, and GDAL. See [this link](https://sgillies.net/2019/06/23/fix-for-geos-dll-bug-shapely-1-7a2.html) for more details. If that doesn't work, try using the command ``pip install shapely --no-binary shapely``*


*^^GDAL requires installation prior to ``pip`` installation. This can be done using ``brew``. Windows users might consider installing GDAL using [OSGeo4W](https://trac.osgeo.org/osgeo4w/). macOS users might consider using the [KyngChaos installer](https://www.kyngchaos.com/software/frameworks/)*

## Getting started

First, ensure you are in the appropriate working directory (i.e. the main directory)

We will need raster data from WorldPop to successfully execute the demo. This file was not included with the repository due to the large file size.

WorldPop data can be downloaded using the function **download_worldpop.py**.. This downloads the dataset to the expected location by **main_script.py**. You can call it as follows:

    python download_worldpop.py <country>

For example, to download the WorldPop data for Austria, you can call:

    python download_worldpop.py AUT

In this case, the ISO 3166-1 alpha-3 must be provided for the ``<country>``.

With WorldPop data downloaded, you can execute the core script as follows:

    python main_script.py <country> <group>

Demo files are included for the case of Austria (AUT) and the commercial (COM) and residential (RES) groups. Therefore, you can test the code first by using either commands:

    python main_script.py AUT COM
    python main_script.py Austria RES

Note that  for ``<country>`` either the ISO 3166-1 alpha-3 or the country name can be used, and the input files are expected to have consistent names.

Similarly, the ``<group>`` is expected to be included on the exposure input file, and will also be included in the exposure output file. This is for convenience where there are multiple groups (e.g. occupancies) within one country.

If successful, you should something similar to the following print statements:

    AUT.1_1
    AUT.2_1
    AUT.3_1
    AUT.4_1
    AUT.5_1
    AUT.6_1
    AUT.7_1
    AUT.8_1
    AUT.9_1
    There are 94262 buildings in the exposure model
    Code took 5.1628 seconds

The computation time is related to the number of administrative boundaries in the input data.

If the entire **spatial-disaggregation** repository was cloned, then the code should execute successfully provided the listed dependencies are installed.

To run for a different country or other use, you would need to manually enter some information to the **_config.py** file (such as the country name and ISO 3 of interest). Additionally, you may need to pre-download certain datasets at this stage. The code will be developed such that advance download and arrangement of external data is not necessary (provided you have a reliable internet connection), but at a later stage.
