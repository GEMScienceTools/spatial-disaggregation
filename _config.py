# ------------------------------------------------------------------------------
#   GENERIC DEPENDENCIES
# ------------------------------------------------------------------------------

# Dependencies - reading, writing, and parsing files
import os
import sys

# Dependencies - other
from functools import reduce
import random
import math
import itertools
from operator import itemgetter

# ------------------------------------------------------------------------------
#   EXTERNAL DEPENDENCIES
# ------------------------------------------------------------------------------

# Rasterio - working with raster data
import rasterio as rio
from rasterio.plot import plotting_extent
from rasterio.warp import calculate_default_transform, reproject, Resampling
import rasterio.transform
import rasterio.mask
from rasterio import Affine

# Shapefiles - working with vector data
import shapely.geometry
from shapely.ops import cascaded_union
import geopandas as gpd

# GDAL
from osgeo import gdal, gdalconst

# Numeric
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree


# ------------------------------------------------------------------------------
#   INTERNAL DEPENDENCIES
# ------------------------------------------------------------------------------

from util.util import *

# ------------------------------------------------------------------------------
#   "GLOBAL" VARIABLES
# ------------------------------------------------------------------------------

# Desired resolution to resampling of raster data (i.e. WorldPop)
# In the same units as the desired_crs (e.g. degrees for EPSG:4326)
# Cannot be equal to or less than the original resolution of the downloaded
# data
res = 0.05

# Desired coordinate reference system corresponding to input files
desired_crs = "EPSG:4326"
# Desired coordinate reference system for calculating areas (you may need to
# look up which flat projection would work well for your region); however it's
# not particularly important to the calculation and therefore OK to be a bit
# inaccurate
area_crs = "EPSG:3035" # Suitable for EU

# Input shapefile parameters - field_name needs to exist in both the input
# shapefile and the input exposure CSV file. Directly replace field_name
# with the field of interest
adm_level = 1
field_name = f"ID_{adm_level}"

# Threshold for checking that sampled asset counts match original input
thresh = 0.001

# Estimate buildings based on specified function
# NOTE: This function could be adjusted according to needs. Currently,
# the function assumes that buildings are directly proportional to the
# estimated population, with a minimum threshold of estimated population
# applied. Another option, which might be desirable for industrial
# buildings would be to sample buildings proportional to the square root of
# the estimated population (which would yield more spread)
pop_thresh = 0.35
# NOTE: The pop input will be a df column of the population estimates
population_to_buildings = lambda pop : [x if x > pop_thresh else 0 for x in pop]


# Loss types to aggregate from the exposure input file
loss_types = ["structural", "night"]

# Tags to retain from the exposure input file
retain_tags = ["taxonomy"]

# Input exposure directory
exp_directory = os.path.join("data", "exposure_in")

# Mosaic mapping file
mosaic_mapping = os.path.join("data", "input_mosaic_mapping_scheme.csv")

# Initialize worldpop info and directory paths
worldpop_year = 2020

# Directory locations - inputs
shp_directory = os.path.join("data", "shapefile_in")
wp_directory = os.path.join("data", "worldpop")

# File locations - inputs
name = "Austria"
shp_file = f"Adm{adm_level}_{name}.shp"

# Directory locations - outputs
output_dir = os.path.join("output")
