import numpy as np


def replace_na_repr_with_nan(df, null_values: list[str] | str, column_name: str):
    if isinstance(null_values, str):
        null_values = [null_values]
    
    indexes = df[df[column_name].isin(null_values)].index

    df.loc[indexes, column_name] = np.nan

    return df
