import re
from pathlib import Path

import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')


EXCEL_PATH = Path("2019-20-historical-migration-statistics-locked.xlsx")

# Countrys' name discrepancies between two excel sheets
DIFF_32 = [
    "Bosnia-Herzegovina", "Cape Verde", "Cambodia, the Kingdom of", 
    "China, People's Republic of", "Congo", "Democratic Republic of Congo", 
    "Czech Republic", "Egypt, Arab Republic of", "Swaziland", 
    "Germany, Federal Rep. Of", "Hong Kong (SAR of China)", 
    "Ireland", "Korea, Dem Peoples Rep Of", "Korea, Republic of", 
    "Lao Peoples Democratic Rep", "Macau Spec Admin Rgn", 
    "Netherlands", "Fmr Yugo Rep of Macedonia", "South Sudan", "St Lucia", 
    "South Africa, Republic of", "St Kitts-Nevis", "Syria", 
    "Dem Republic Of Timor-Leste", "Yemen", "British Indian Ocean Terr"]

DIFF_33 =[
    "Bosnia and Herzegovina", "Cabo Verde", "Cambodia", "China, Peoples Republic of (excl SARs)", 
    "Congo, Republic of", "Congo, Dem Republic of The", "Czechia", "Egypt", "Eswatini", 
    "Germany, Fed Republic of", "Hong Kong (SAR of the PRC)", "Ireland, Republic of", 
    "Korea, North", "Korea, South", "Lao Peoples Dem Republic", "Macau (SAR of the PRC)", 
    "Netherlands, Kingdom of The", "North Macedonia", "Republic of South Sudan", 
    "Saint Lucia", "South Africa", "St Kitts and Nevis", "Syrian Arab Republic", "Timor-Leste", 
    "Yemen, Republic of", "British Indian Ocean Territories"]



def load_data(path=EXCEL_PATH):
    """
    to load data from specified excel file
    :param path: path to the excel file
    :return: two instances of pandas dataframe
    
    tip1: header={num} to assumed skiprow={num} applied beforeahnd.
    tip2: using two level header to avoind auto-rename for duplicated country names.
    """
    df1 = pd.read_excel(path, sheet_name="3.2", skiprows=6, 
                        header=[0, 1], skipfooter=10)
    df2 = pd.read_excel(path, sheet_name="3.3", skiprows=6, 
                        header=[0, 1], skipfooter=8)
    
    return df1, df2


def get_transposed_df(df):
    """
    to transpose df in a more redable view
    :param df: pandas df instance
    :return: panda df instance
    """
    df_transpose = df.T
    df_transpose.reset_index(inplace=True)
    df_transpose.columns = df_transpose.iloc[1]
    df_transpose.drop([0,1], inplace=True)
    df_transpose.rename(columns={"Unnamed: 1_level_0":"Stream", "Year":"Country"}, inplace=True)
    df_transpose.reset_index(drop=True, inplace=True)
    
    return df_transpose


def get_clean_df(df):
    """
    to clean df ready for exploration
    :param df: pandas df instance
    :return: panda df instance 
    """
    # removing unneccessary rows/columns
    df = df[
        ~df["Country"].str.contains("total", case=False, regex=False) &
        ~df["Stream"].str.contains("total", case=False, regex=False)
    ]
    
    # stripping white space from column names
    names = df.columns.tolist()
    new_names = [n.strip() for n in names]
    df.rename(columns=dict(zip(names, new_names)), inplace=True)
    
    # removing special characters    
    for c in new_names[2:]:
        df[c] = df[c].astype(str)
        df[c] = df[c].str.extract(r'(\d+)')
        df[c] = df[c].astype(int)
    
    return df


def resolve_country_name(df1, df2, diff1=DIFF_32, diff2=DIFF_33):
    """
    to resolve dicrepancies between country names
    :param df1: first dataframe; column names to be replaced
    :param df2: second dataframe
    :param diff1: countries from df1 with different spelling
    :param diff2: countries from df2 with different spelling
    :return: two panda dataframe instances
    """
    df1.replace(dict(zip(diff1, diff2)), inplace=True)
    
    # removing countries missing from each sheet
    missing_from_df1 = [c for c in df2.Country.unique() if c not in df1.Country.unique()]
    missing_from_df2 = [c for c in df1.Country.unique() if c not in df2.Country.unique()]
    
    df1 = df1[~df1["Country"].isin(missing_from_df2)]
    df2 = df2[~df2["Country"].isin(missing_from_df1)]

    df1.reset_index(drop=True, inplace=True)
    df2.reset_index(drop=True, inplace=True)
    
    return df1, df2


def get_merged_df(df1, df2):
    """
    to merge two dataframes as final source
    :param df1, df2: pandas datagrame instances
    :return: pandas dataframe
    """
    df = pd.merge(df1, df2, how="outer", 
                  on=["Stream", "Country"])
    df.fillna(0, inplace=True)
    for c in df.columns[2:]:
        df[c] = df[c].astype(int)
    
    return df