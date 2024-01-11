import numpy as np


def replace_na_repr_with_nan(df, null_values: list[str] | str, column_name: str):
    if not isinstance(null_values, list):
        null_values = [null_values]

    prev_col_type = str(df[column_name].dtype)
    
    indexes = df[df[column_name].isin(null_values)].index

    df.loc[indexes, column_name] = np.nan

    if prev_col_type.startswith('int'):
        df[column_name] = df[column_name].astype('Int64')
    
    return df
