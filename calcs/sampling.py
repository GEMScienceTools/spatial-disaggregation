# Load dependencies
from _config import *


# Resample assets based on additional data (e.g. WorldPop)
def resample_assets(df, assets, bound_names, mapped_field):
    ''' This function takes the input exposure CSV and resamples for each
    bound_name in the mapped_field using the additional data (e.g. WorldPop)
    at the desired resolution (res) specified in _config.py'''

    # Retain specific columns
    retain_cols = ["x", "y", "number"] + retain_tags + loss_types

    # Determine number of bound_names
    n_bounds = len(bound_names)

    # Initialize empty dataframe to store sample locations
    samples = pd.DataFrame(columns=retain_cols)

    # Initialize dataframes for each bound_name
    bound_samples = [pd.DataFrame(columns=df.columns) for i in range(n_bounds)]

    # For each admin bound
    for j in range(n_bounds):

        # Get bound name
        bound_name = bound_names[j]
        print(bound_name)

        # Grab relevant assets from input exposure
        idx = (assets[mapped_field] == bound_name)

        # Get relevant locations from df grid
        jdx = df[mapped_field] == bound_name
        df_jdx = df[jdx]

        # Sample only if not empty; pass otherewise (e.g. water bodies)
        if assets[idx].shape[0] > 0:

            # Retrieve indices
            i_jdx = df_jdx.index.values

            # Normalize count to get probabilities
            p_jdx = df_jdx['count'] / df_jdx['count'].sum()

            # Pivot by retain_tags and loss_types
            asset_idx_pivot = assets[idx].pivot_table(
                index=retain_tags,
                values=["number"] + loss_types,
                aggfunc="sum"
            )

            # Iterate through each class and append to samples
            for i, row in asset_idx_pivot.iterrows():

                # Get number of samples desired
                n_samples = math.ceil(row["number"])

                # Get weights of each sample
                w_samples = np.ones((n_samples,))
                if n_samples != row["number"]:
                    w_samples[-1] = n_samples - row["number"]

                # Sample locations on df grid
                sampled_jdx = random.choices(i_jdx, weights=p_jdx, k=n_samples)

                # Arrange into dataframe format
                new_samples = df_jdx.loc[sampled_jdx].copy()
                new_samples["weights"] = w_samples
                new_samples["taxonomy"] = i  # FIXME: should be automatic from retain_tags

                # Add number and loss type values according to weight
                for col in ["number"] + loss_types:
                    new_samples[col] = row[col] * new_samples["weights"] / new_samples["weights"].sum()

                # Arranged sampled indices into desired dataframe format
                bound_samples[j] = pd.concat([bound_samples[j], new_samples],
                                             axis=0, ignore_index=True)

            # Aggregate samples with same location/taxonomy; assign bound_name
            bound_samples[j] = bound_samples[j][retain_cols].groupby(
                ["x", "y"] + retain_tags
                ).agg(
                    "sum"
                ).reset_index()
            bound_samples[j][mapped_field] = bound_name

        else:

            pass

    # Concatenate to overall samples
    samples = pd.concat(bound_samples, axis=0, ignore_index=True)

    # Return result
    return samples
