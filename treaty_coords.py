# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python [conda env:root] *
#     language: python
#     name: conda-root-py
# ---

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import geopandas as gpd
import pycountry

"""Generates dataframe of signer countries' capital city coordinates."""

bits = pd.read_csv("full_cleaned_iia.csv")

bits = bits.loc[bits["is_BIT"] == 1]

bits = bits[["signer_1", "signer_2", "year"]]

capital_geo = pd.read_csv("country-capitals.csv")

# +
countries = []
for country in pycountry.countries:
    country_dict = {}
    try:
        country_dict["cname"] = country.common_name

    except:
        country_dict["cname"] = country.name
        pass

    try:
        country_dict["oname"] = country.official_name

    except:
        country_dict["oname"] = country.name

    country_dict["lname"] = country.name
    country_dict["num"] = country.numeric
    country_dict["abbrev"] = country.alpha_3
    country_dict["abbrev2"] = country.alpha_2

    countries.append(country_dict)

countries_df = pd.DataFrame(countries)
# -

set(capital_geo["CountryCode"]) - set(countries_df["abbrev2"])

capital_geo = pd.merge(
    capital_geo, countries_df, how="left", left_on="CountryCode", right_on="abbrev2"
)

capital_geo = capital_geo[
    ["lname", "CapitalLatitude", "CapitalLongitude", "abbrev"]
].dropna(axis=0, subset=["lname"])


def merge_with_signer(signer, df1, df2):

    df1 = df1.loc[df1["lname"].notnull()].add_suffix("_" + signer)

    merged = pd.merge(
        df2, df1, how="left", left_on=[signer], right_on=["lname_" + signer]
    )

    return merged


for s in ["signer_1", "signer_2"]:
    bits = merge_with_signer(s, capital_geo, bits)

bits.to_csv("lat_lon_bits.csv", index=False)

capital_geo.to_csv("lat_lon_allcountries.csv", index=False)
