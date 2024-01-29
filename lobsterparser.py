"""A parser for lobster output files"""

__version__ = "1.0.0"

import pandas as pd
from io import StringIO

# Helper functions
def get_interaction_from_line(line):
    interaction =  line.split(':')[1].split('->')[0] + line.split(':')[1].split('->')[1].split('(')[0]
    return interaction

def is_energy_in_range(e, edown, eup):
    return edown < e < eup

def get_subset_by_atomID(df, atomID):
    subset = [col for col in df.columns if col.startswith(atomID)]
    return subset

def get_mean_by_atomID(df, atomID):
    subset = get_subset_by_atomID(df, atomID)
    out_col = df[subset].mean(axis=1)
    return out_col

def insert_mean_by_atomID(df, atomID):
    # Hay que revisar esta que me parece que está redundante 
    out_df = df.copy() # Refer to Normands book on copy discipline
    out_df['m' + atomID] = get_mean_by_atomID(df,atomID)
    return out_df

def reorder_indices_last_to_second(df):
    out_df = df.copy() # Copy discipline
    all_but_one = len(df.columns) - 1 # range to be used bellow excludes last index
    new_order = [0, -1] + list(range(1, all_but_one))
    return out_df.iloc[:, new_order]

def df_energy_filtered(df, elow, ehigh):
    out_df = df.copy()
    return out_df[(elow < out_df['E']) & (out_df['E'] < ehigh)] # THis is ugly

def df_from_subset_by_atomID(df, atomID):
    subset_with_E = ['E'] + get_subset_by_atomID(df, atomID)
    out_df = df[subset_with_E].copy()
    out_df = insert_mean_by_atomID(out_df, atomID)
    out_df = reorder_indices_last_to_second(out_df)
    return out_df

# IO functions

def carfile_to_df(in_file):
    # Read the file content
    with open(in_file, 'r') as file:
        lines = file.readlines()

    interactions = [get_interaction_from_line(line) for line in lines if line.startswith("No.")]
    integrated_interactions = ['i' + interaction for interaction in interactions]
    alternating = [element for pair in zip(interactions,integrated_interactions) for element in pair] # This looks very arcane

    # Data starts after interactions, join the remaining lines
    data = ''.join(lines[(3 + len(interactions)):])

    # Read the data into a DataFrame
    df = pd.read_csv(StringIO(data), delim_whitespace=True, header=None)

    # Rename columns
    df.columns = ['E', 'total', 'itotal'] + alternating

    return df

def df_to_datfile(df, out_filename):
    df.to_csv(out_filename, sep=' ', index=None)

