# Load dependencies
from _config import *


# Write model to CSV for OQ
def write_model(model, file_name, group):
    ''' This function writes the resampled exposure model to a CSV in the
    output_dir'''

    # Fill missing values
    model = model.fillna(0).reset_index()

    # Construct id column
    model["id"] = group.title() + "_" + model.index.astype(str)

    # FIXME: Handle this in a better way
    model["occupancy"] = group.title()

    # Arrange full path
    file_path = os.path.join(output_dir, file_name)

    # Export df to csv
    model.to_csv(file_path, index=False)
