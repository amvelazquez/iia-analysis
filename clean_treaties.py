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

# +
import os
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import PyPDF2
import pandas as pd
import datetime as dt
import numpy as np
import pycountry
import re

import nltk.corpus

nltk.download("stopwords")
from nltk.corpus import stopwords

from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
# -

"""Cleans raw investment agreement data. Produces features for prediction."""


def split_signers(df, string, string_len):
    index = 1
    for i in range(string_len):

        col_1 = "signer_" + str(index)
        col_2 = "signer_" + str(index + 1)

        if index == 1:
            split_col = "parties"
        else:
            split_col = col_1

        df.loc[df["parties"] == string, [col_1, col_2],] = (
            df.loc[df["parties"] == string, split_col,]
            .str.split(", ", n=1, expand=True)
            .values
        )

        index += 1

    return df


def merge_with_signer(signer, df1, df2):

    df1 = df1.loc[df1["lname"].notnull()].add_suffix("_" + signer)

    merged = pd.merge(
        df2,
        df1,
        how="left",
        left_on=[signer, "year"],
        right_on=["lname_" + signer, "year_" + signer],
    )

    return merged


def compute_delta(df, col_nm, temp_nm, new_nm):
    for s1 in [
        "signer_1",
        "signer_2",
        "signer_3",
        "signer_4",
        "signer_5",
        "signer_6",
        "signer_7",
        "signer_8",
        "signer_9",
        "signer_10",
        "signer_11",
        "signer_12",
        "signer_13",
        "signer_14",
    ]:
        for s2 in [
            "signer_1",
            "signer_2",
            "signer_3",
            "signer_4",
            "signer_5",
            "signer_6",
            "signer_7",
            "signer_8",
            "signer_9",
            "signer_10",
            "signer_11",
            "signer_12",
            "signer_13",
            "signer_14",
        ]:
            temp_nm_1 = temp_nm + "_" + s1 + "_" + s2
            temp_nm_2 = temp_nm + "_" + s2 + "_" + s1

            col_nm_1 = col_nm + "_" + s1
            col_nm_2 = col_nm + "_" + s2

            if s1 == s2 or temp_nm_1 in df.columns or temp_nm_2 in df.columns:
                pass
            else:
                df[temp_nm_1] = abs(df[col_nm_1] - df[col_nm_2])

            df[new_nm] = df[df.columns[df.columns.str.startswith(temp_nm + "_")]].mean(
                axis=1
            )
            df.loc[df["signer_3"].isna(), [new_nm]] = abs(
                df[col_nm + "_signer_1"] - df[col_nm + "_signer_2"]
            )

            unwanted = df.columns[df.columns.str.startswith(temp_nm + "_")]
            df = df.drop(unwanted, axis=1)

            return df


def compute_bloc_vars(col, df1, df2, include_EU=True):
    for s in ["signer_" + str(i) for i in range(1, 15)]:
        new_col = col + "_" + s

        for k, v in blocs.items():
            if not include_EU:
                if k == "EU (European Union)":
                    pass
            for i in range(len(df2.loc[(df2[s] == k)])):
                l = df2.loc[(df2[s] == k)].index.values[i]
                treaty_yr = df2.loc[l, "year"]
                dist = {}
                for y in v.keys():
                    if y <= treaty_yr:
                        dist[y] = treaty_yr - y
                    if len(dist) > 0:
                        right_key = min(dist, key=dist.get)

                        df2.loc[l, new_col] = np.mean(
                            df1.loc[
                                (df1["lname"].isin(v[right_key]))
                                & (df1["year"] == treaty_yr),
                                col,
                            ].values
                        )
                        df2 = df2.reset_index(drop=True)
                    else:
                        pass
    return df2


blocs = {
    "EU (European Union)": {
        1964: ["Belgium", "France", "Italy", "Luxembourg", "Netherlands", "Germany"],
        1973: [
            "Belgium",
            "France",
            "Italy",
            "Luxembourg",
            "Netherlands",
            "Germany",
            "United Kingdom",
            "Ireland",
            "Denmark",
        ],
        1981: [
            "Belgium",
            "France",
            "Italy",
            "Luxembourg",
            "Netherlands",
            "Germany",
            "United Kingdom",
            "Ireland",
            "Denmark",
            "Greece",
        ],
        1986: [
            "Belgium",
            "France",
            "Italy",
            "Luxembourg",
            "Netherlands",
            "Germany",
            "United Kingdom",
            "Ireland",
            "Denmark",
            "Greece",
            "Portugal",
            "Spain",
        ],
        1995: [
            "Belgium",
            "France",
            "Italy",
            "Luxembourg",
            "Netherlands",
            "Germany",
            "United Kingdom",
            "Ireland",
            "Denmark",
            "Greece",
            "Portugal",
            "Spain",
            "Austria",
            "Finland",
            "Sweden",
        ],
        2004: [
            "Belgium",
            "France",
            "Italy",
            "Luxembourg",
            "Netherlands",
            "Germany",
            "United Kingdom",
            "Ireland",
            "Denmark",
            "Greece",
            "Portugal",
            "Spain",
            "Austria",
            "Finland",
            "Sweden",
            "Cyprus",
            "Czech Republic",
            "Estonia",
            "Hungary",
            "Latvia",
            "Lithuania",
            "Malta",
            "Poland",
            "Slovakia",
            "Slovenia",
        ],
        2007: [
            "Belgium",
            "France",
            "Italy",
            "Luxembourg",
            "Netherlands",
            "Germany",
            "United Kingdom",
            "Ireland",
            "Denmark",
            "Greece",
            "Portugal",
            "Spain",
            "Austria",
            "Finland",
            "Sweden",
            "Cyprus",
            "Czech Republic",
            "Estonia",
            "Hungary",
            "Latvia",
            "Lithuania",
            "Malta",
            "Poland",
            "Slovakia",
            "Slovenia",
            "Bulgaria",
            "Romania",
        ],
        2013: [
            "Belgium",
            "France",
            "Italy",
            "Luxembourg",
            "Netherlands",
            "Germany",
            "United Kingdom",
            "Ireland",
            "Denmark",
            "Greece",
            "Portugal",
            "Spain",
            "Austria",
            "Finland",
            "Sweden",
            "Cyprus",
            "Czech Republic",
            "Estonia",
            "Hungary",
            "Latvia",
            "Lithuania",
            "Malta",
            "Poland",
            "Slovakia",
            "Slovenia",
            "Bulgaria",
            "Romania",
            "Croatia",
        ],
        2020: [
            "Belgium",
            "France",
            "Italy",
            "Luxembourg",
            "Netherlands",
            "Germany",
            "Ireland",
            "Denmark",
            "Greece",
            "Portugal",
            "Spain",
            "Austria",
            "Finland",
            "Sweden",
            "Cyprus",
            "Czech Republic",
            "Estonia",
            "Hungary",
            "Latvia",
            "Lithuania",
            "Malta",
            "Poland",
            "Slovakia",
            "Slovenia",
            "Bulgaria",
            "Romania",
            "Croatia",
        ],
    },
    "ASEAN (Association of South-East Asian Nations)": {
        1967: ["Indonesia", "Malaysia", "Philippines", "Singapore", "Thailand"],
        1984: [
            "Indonesia",
            "Malaysia",
            "Philippines",
            "Singapore",
            "Thailand",
            "Brunei Darussalam",
        ],
        1995: [
            "Indonesia",
            "Malaysia",
            "Philippines",
            "Singapore",
            "Thailand",
            "Brunei Darussalam",
            "Vietnam",
        ],
        1997: [
            "Indonesia",
            "Malaysia",
            "Philippines",
            "Singapore",
            "Thailand",
            "Brunei Darussalam",
            "Vietnam",
            "Myanmar",
        ],
        1999: [
            "Indonesia",
            "Malaysia",
            "Philippines",
            "Singapore",
            "Thailand",
            "Brunei Darussalam",
            "Vietnam",
            "Myanmar",
            "Cambodia",
        ],
    },
    "BLEU (Belgium-Luxembourg Economic Union)": {1923: ["Belgium", "Luxembourg"]},
    "EFTA (European Free Trade Association)": {
        1960: [
            "Austria",
            "Denmark",
            "Portugal",
            "Sweden",
            "United Kingdom",
            "Norway",
            "Switzerland",
        ],
        1970: [
            "Austria",
            "Denmark",
            "Portugal",
            "Sweden",
            "United Kingdom",
            "Norway",
            "Switzerland",
            "Iceland",
        ],
        1972: ["Austria", "Portugal", "Sweden", "Norway", "Switzerland", "Iceland",],
        1985: ["Austria", "Finland", "Sweden", "Norway", "Switzerland", "Iceland"],
        1991: [
            "Austria",
            "Finland",
            "Sweden",
            "Norway",
            "Switzerland",
            "Iceland",
            "Liechtenstein",
        ],
        1994: ["Norway", "Switzerland", "Iceland", "Liechtenstein",],
    },
    "Eurasian Economic Union": {
        2014: ["Russian Federation", "Armenia", "Belarus", "Kazakhstan", "Kyrgyzstan"]
    },
}

treaty_df = pd.read_csv("raw_iia.csv")

# Date-Related Variables

for date in ["sign_date", "entry_force_date", "termination_date"]:
    treaty_df[date] = pd.to_datetime(treaty_df[date], infer_datetime_format=True)
    treaty_df[date + "_year"] = treaty_df[date].dt.year.fillna(0).astype(int)
    treaty_df[date + "_decade"] = (
        (np.floor(treaty_df[date + "_year"] / 10) * 10).fillna(0).astype(int)
    )

treaty_df["time_to_entry"] = treaty_df["entry_force_date"] - treaty_df["sign_date"]
treaty_df["time_to_entry"] = treaty_df["time_to_entry"].dt.days
treaty_df["time_to_termination"] = (
    treaty_df["termination_date"] - treaty_df["entry_force_date"]
)
treaty_df["time_to_termination"] = treaty_df["time_to_termination"].dt.days

# Less or Greater than 1 year dummy?



# Status Variables

treaty_df["status"] = treaty_df["status"].str.lower()
treaty_df["status"] = treaty_df["status"].str.replace(
    " (not in force)", "", regex=False
)
treaty_df["status"] = treaty_df["status"].str.replace(" ", "_", regex=False)

# Treaty Type

treaty_df["treaty_type"] = treaty_df["title"].apply(
    lambda x: " ".join(re.findall(r"\w+(?=\s+\()", x))
)
treaty_df.loc[treaty_df["treaty_type"] == "Agreement", "treaty_type"] = (
    treaty_df["title"].apply(lambda x: " ".join(re.findall(r"\w+(?=\s+Agreement)", x)))
    + " Agreement"
)
treaty_df.loc[treaty_df["treaty_type"] == "BLEU BIT", "treaty_type"] = "BIT"
treaty_df.loc[treaty_df["treaty_type"] == "Investment Agreement", "treaty_type"] = "MIT"
treaty_df.loc[
    treaty_df["treaty_type"] == "EPCA", "treaty_type"
] = "Association Agreement"
treaty_df.loc[treaty_df["treaty_type"] == "TPP", "treaty_type"] = "FTA"
treaty_df.loc[treaty_df["treaty_type"] == "Macedonia", "treaty_type"] = "BIT"
treaty_df.loc[treaty_df["treaty_type"] == "Association Agreement", "treaty_type"] = "AA"
treaty_df.loc[
    ~treaty_df["treaty_type"].isin(["BIT", "FTA", "MIT", "AA", "EPA"]), "treaty_type"
] = "OTHER"

treaty_df["year"] = treaty_df["sign_date_year"]
treaty_df = pd.get_dummies(
    treaty_df,
    prefix=["yr", "dec", "is", None],
    columns=["sign_date_year", "sign_date_decade", "treaty_type", "status"],
)

# Country-Related Data

treaty_df[["signer_1", "signer_2"]] = treaty_df["parties"].str.split(
    ", ", n=1, expand=True
)

# +
treaty_df.loc[treaty_df["parties"].str.contains(r",*of,"), ["signer_1", "signer_2"]] = (
    treaty_df.loc[treaty_df["parties"].str.contains(r",*of,"), "parties"]
    .str.split(" of,", n=1, expand=True)
    .values
)

treaty_df.loc[treaty_df["parties"].str.contains(r",*of,"), ["signer_1"]] = (
    treaty_df.loc[treaty_df["parties"].str.contains(r",*of,"), ["signer_1"]].values
    + " of"
)

# +
treaty_df.loc[
    treaty_df["parties"].str.contains(r",*of the,"), ["signer_1", "signer_2"]
] = (
    treaty_df.loc[treaty_df["parties"].str.contains(r",*of the,"), "parties"]
    .str.split(" of the,", n=1, expand=True)
    .values
)

treaty_df.loc[treaty_df["parties"].str.contains(r",*of the,"), ["signer_1"]] = (
    treaty_df.loc[treaty_df["parties"].str.contains(r",*of the,"), ["signer_1"]].values
    + " of the"
)
# -

treaty_df["signer_1"] = treaty_df["signer_1"].replace(
    r",*(China SAR),*", r"", regex=True
)
treaty_df["signer_2"] = treaty_df["signer_2"].replace(
    r",*(China SAR),*", r"", regex=True
)

treaty_df["signer_2"] = treaty_df["signer_2"].replace(r"^ +| +$", r"", regex=True)

treaty_df["signer_2"] = treaty_df["signer_2"].replace(r",$", r"", regex=True)

# Clean Signer 1

# +
treaty_df.loc[
    treaty_df["signer_1"] == "Taiwan Province of China", ["signer_1"]
] = "Taiwan, Province of China"

treaty_df.loc[treaty_df["signer_1"] == "Türkiye", ["signer_1"]] = "Turkey"

treaty_df.loc[
    treaty_df["signer_1"] == "United States of America", ["signer_1"]
] = "United States"

treaty_df.loc[
    treaty_df["signer_1"] == "Korea, Dem. People's Rep. of", ["signer_1"]
] = "Korea, Democratic People's Republic of"
# -

# Clean Signer 2

treaty_df.loc[
    treaty_df["signer_2"] == "Taiwan Province of China", ["signer_2"]
] = "Taiwan, Province of China"
treaty_df.loc[treaty_df["signer_2"] == "Türkiye", ["signer_2"]] = "Turkey"
treaty_df.loc[
    treaty_df["signer_2"] == "State of Palestine", ["signer_2"]
] = "Palestine, State of"
treaty_df.loc[
    treaty_df["signer_2"] == "United States of America", ["signer_2"]
] = "United States"
treaty_df.loc[
    treaty_df["signer_2"] == "Korea, Dem. People's Rep. of", ["signer_2"]
] = "Korea, Democratic People's Republic of"
treaty_df.loc[
    treaty_df["signer_2"] == "Congo, Democratic Republic of the", ["signer_2"]
] = "Congo, The Democratic Republic of the"

# Add extra signers for FTAs

treaty_df["signer_3"] = np.nan
treaty_df["signer_4"] = np.nan
treaty_df["signer_5"] = np.nan
treaty_df["signer_6"] = np.nan
treaty_df["signer_7"] = np.nan
treaty_df["signer_8"] = np.nan
treaty_df["signer_9"] = np.nan
treaty_df["signer_10"] = np.nan
treaty_df["signer_11"] = np.nan
treaty_df["signer_12"] = np.nan
treaty_df["signer_13"] = np.nan
treaty_df["signer_14"] = np.nan

# More complicated signer splits

# +
treaty_df.loc[
    treaty_df["parties"]
    == "Australia, Cook Islands, Micronesia, Federated States of, Kiribati, Nauru, New Zealand, Niue, Palau, Marshall Islands, Samoa, Solomon Islands, Tonga, Tuvalu, Vanuatu",
    "parties",
] = "Australia, Cook Islands, Micronesia, Kiribati, Nauru, New Zealand, Niue, Palau, Marshall Islands, Samoa, Solomon Islands, Tonga, Tuvalu, Vanuatu"


treaty_df.loc[
    treaty_df["parties"]
    == "Australia, Brunei Darussalam, Canada, Chile, Japan, Malaysia, Mexico, New Zealand, Peru, Singapore, United States of America, Viet Nam",
    "parties",
] = "Australia, Brunei Darussalam, Canada, Chile, Japan, Malaysia, Mexico, New Zealand, Peru, Singapore, United States, Vietnam"

# +
treaty_df = split_signers(
    treaty_df,
    "Australia, Cook Islands, Micronesia, Kiribati, Nauru, New Zealand, Niue, Palau, Marshall Islands, Samoa, Solomon Islands, Tonga, Tuvalu, Vanuatu",
    13,
)

treaty_df = split_signers(
    treaty_df,
    "Australia, Brunei Darussalam, Canada, Chile, Japan, Malaysia, Mexico, New Zealand, Peru, Singapore, United States, Vietnam",
    11,
)


treaty_df = split_signers(
    treaty_df, "EFTA (European Free Trade Association), Costa Rica, Panama", 2,
)

treaty_df = split_signers(treaty_df, "Colombia, Peru, Mexico, Chile", 3,)
# -

treaty_df.loc[
    treaty_df["signer_1"] == "Japan, Korea, Republic of",
    ["signer_1", "signer_2", "signer_3"],
] = ("Japan", "Korea, Republic of", "China")

# Make was_renegotiated var

# +
# treaty_df.loc[treaty_df[['signer_1', 'signer_2']].duplicated()]

# +
# treaty_df.groupby(['signer_1', 'signer_2'])['sign_date_year'].min()['was_renegotiated'] = True
# -

# #### External Variables

# Standardize country names

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

    countries.append(country_dict)

countries_df = pd.DataFrame(countries)
# -

countries_df["lname"] = countries_df["lname"].replace(r"^ +| +$", r"", regex=True)

# https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv
regions_df = pd.read_csv("regions.csv")

regions_df.loc[
    regions_df["intermediate-region"] == "Caribbean", ["sub-region"]
] = "Caribbean"
regions_df.loc[
    regions_df["sub-region"] == "Latin America and the Caribbean", ["sub-region"]
] = "Latin America"

countries_df = pd.merge(
    countries_df,
    regions_df[["alpha-3", "sub-region"]],
    how="left",
    left_on="abbrev",
    right_on="alpha-3",
)

# Clean country economic data

country_df = pd.read_csv("08_31_22_1003pm_wep.csv", sep=",", encoding="latin-1")

country_df.loc[country_df["country"] == "Bulgaria", ["ifs"]] = "BGR"
country_df.loc[country_df["country"] == "Andorra", ["ifs"]] = "AND"
country_df.loc[
    country_df["country"] == "Congo, Democratic Republic of (Zair", ["ifs"]
] = "COD"
country_df.loc[country_df["country"] == "Rumania", ["ifs"]] = "ROU"
country_df.loc[country_df["country"] == "South Sudan", ["ifs"]] = "SSD"
country_df.loc[country_df["country"] == "Hong Kong", ["ifs"]] = "HKG"
country_df.loc[country_df["country"].str.contains("Vietnam"), ["ifs"]] = "VNM"
country_df.loc[country_df["country"] == "East Timor", ["ifs"]] = "TLS"
country_df.loc[country_df["country"] == "Nauru", ["ifs"]] = "NRU"
country_df.loc[
    country_df["country"] == "Federated States of Micronesia", ["ifs"]
] = "FSM"

country_df = pd.merge(
    country_df, countries_df, how="left", left_on=["ifs"], right_on=["abbrev"]
)

countries_df["sub-region"] = countries_df["sub-region"].str.lower()
countries_df["sub-region"] = countries_df["sub-region"].str.replace(
    "-", "_", regex=False
)
countries_df["sub-region"] = countries_df["sub-region"].str.replace(
    " ", "_", regex=False
)

region_dict = {}
for r in countries_df["sub-region"].unique():
    region_dict[r] = list(
        countries_df.loc[countries_df["sub-region"] == r, "lname"].values
    )

for r in region_dict.keys():
    treaty_df[r] = 0

for r, v in region_dict.items():
    for c in v:
        for s in [
            "signer_1",
            "signer_2",
            "signer_3",
            "signer_4",
            "signer_5",
            "signer_6",
            "signer_7",
            "signer_8",
            "signer_9",
            "signer_10",
            "signer_11",
            "signer_12",
            "signer_13",
            "signer_14",
        ]:

            treaty_df.loc[(treaty_df[s] == c), [r]] = 1

# +
# country_df.loc[country_df['abbrev'].isnull(),'country'].unique()
# countries_df[countries_df['cname'].str.contains('Micronesia')]
# country_df.loc[country_df['country'].str.contains('Micronesia')]

# +
# len(set(country_df['oname'].to_list()))

# +
# len(set(treaty_df['signer_1'].to_list()))

# +
# len(set(treaty_df['signer_2'].to_list()))

# +
# set(treaty_df['signer_1'].to_list()) - set(country_df['lname'].to_list())

# +
# set(treaty_df['signer_2'].to_list()) - set(country_df['lname'].to_list())

# +
# countries_df.loc[countries_df['cname'].str.contains('Kyrgyzstan')]

# +
# country_df.loc[country_df['country'].str.contains("United Kingdom"), ['country','year','gdp_WDI','lname','abbrev']]
# -

eu_gdp = pd.read_csv("API_NY.GDP.PCAP.CD_DS2_en_csv_v2_4473274.csv", encoding="latin-1")
eu_gdp = eu_gdp.rename(columns={'ï»¿"Country Name"': "lname"})
eu_gdp = eu_gdp.loc[eu_gdp["lname"] == "European Union"]
eu_gdp.loc[eu_gdp["lname"] == "European Union", ["lname"]] = "EU (European Union)"
eu_gdp = eu_gdp.drop(
    ["Country Code", "Indicator Name", "Indicator Code", "Unnamed: 66"], axis=1
)
eu_gdp = pd.wide_to_long(eu_gdp, i="lname", stubnames="", j="year").reset_index()
eu_gdp = eu_gdp.rename(columns={"": "gdppc_WDI"})

country_df = pd.concat([eu_gdp, country_df])

# GDP

for s in [
    "signer_1",
    "signer_2",
    "signer_3",
    "signer_4",
    "signer_5",
    "signer_6",
    "signer_7",
    "signer_8",
    "signer_9",
    "signer_10",
    "signer_11",
    "signer_12",
    "signer_13",
    "signer_14",
]:

    print(f"On {s}")
    treaty_df = merge_with_signer(
        s,
        country_df[
            [
                "lname",
                "abbrev",
                "year",
                "gdp_WDI",
                "gdppc_WDI",
                "fdi_inper_WDI",
                "fdi_outper_WDI",
                "pop_den_WDI",
                "ex_agri_WDI",
                "ex_mfg_WDI",
            ]
        ],
        treaty_df,
    )

treaty_df = treaty_df.loc[:, treaty_df.columns.notna()]

unwanted = treaty_df.columns[
    treaty_df.columns.str.startswith("lname_")
    | treaty_df.columns.str.startswith("abbrev_")
    | treaty_df.columns.str.startswith("year_signer_")
]
treaty_df = treaty_df.drop(unwanted, axis=1)

treaty_df = compute_bloc_vars("gdppc_WDI", country_df, treaty_df, include_EU=False)

treaty_df = compute_bloc_vars("ex_agri_WDI", country_df, treaty_df)

# GDP Delta

treaty_df = compute_delta(treaty_df, "gdppc_WDI", "diff_gdppc", "gdp_delta")

treaty_df = compute_delta(treaty_df, "ex_agri_WDI", "diff_agexp", "agexp_delta")

# Regimes

polity = pd.read_excel("p5v2018.xls")

polity = polity.loc[polity["year"] >= treaty_df["sign_date"].dt.year.min()]

polity.loc[polity["country"] == "Korea North", ["country"]] = "North Korea"
polity.loc[polity["country"] == "Korea South", ["country"]] = "South Korea"
polity.loc[polity["country"] == "Bosnia", ["country"]] = "Bosnia and Herzegovina"
polity.loc[polity["country"] == "Cape Verde", ["country"]] = "Cabo Verde"
polity.loc[
    polity["country"] == "Laos", ["country"]
] = "Lao People's Democratic Republic"
polity.loc[polity["country"] == "Iran", ["country"]] = "Iran, Islamic Republic of"
polity.loc[
    (polity["country"] == "Cote D'Ivoire") | (polity["country"] == "Ivory Coast"),
    ["country"],
] = "Côte d'Ivoire"
polity.loc[
    (polity["country"] == "Congo Brazzaville")
    | (polity["country"] == "Congo-Brazzaville"),
    ["country"],
] = "Congo"
polity.loc[
    polity["country"] == "Congo Kinshasa", ["country"]
] = "Congo, The Democratic Republic of the"
polity.loc[polity["country"] == "Russia", ["country"]] = "Russian Federation"
polity.loc[polity["country"] == "Macedonia", ["country"]] = "North Macedonia"
polity.loc[polity["country"] == "Myanmar (Burma)", ["country"]] = "Myanmar"
polity.loc[polity["country"] == "UAE", ["country"]] = "United Arab Emirates"
polity.loc[polity["country"] == "Syria", ["country"]] = "Syrian Arab Republic"
polity.loc[polity["country"] == "Timor Leste", ["country"]] = "Timor-Leste"
polity.loc[polity["country"] == "Czech Republic", ["country"]] = "Czechia"
polity.loc[polity["country"] == "Slovak Republic", ["country"]] = "Slovakia"
polity.loc[
    polity["country"] == "United States                   ", ["country"]
] = "United States"

# +
# set(polity['country'].to_list()) - set(countries_df['cname'].to_list())
# -

polity = pd.merge(
    polity[["country", "year", "polity2"]],
    countries_df,
    how="inner",
    left_on="country",
    right_on="cname",
)

for s in [
    "signer_1",
    "signer_2",
    "signer_3",
    "signer_4",
    "signer_5",
    "signer_6",
    "signer_7",
    "signer_8",
    "signer_9",
    "signer_10",
    "signer_11",
    "signer_12",
    "signer_13",
    "signer_14",
]:

    print(f"On {s}")
    treaty_df = merge_with_signer(s, polity[["lname", "year", "polity2"]], treaty_df)

treaty_df = compute_bloc_vars("polity2", polity, treaty_df)

# Polity Delta

treaty_df = compute_delta(treaty_df, "polity2", "diff_polity", "polity2_delta")

# Litigation?

# +
# list(blocs.keys())
# -

# Number of Parties

# +
# treaty_df=treaty_df.reset_index(drop=True)
# -

treaty_df["n_parties"] = 0
for s in ["signer_" + str(i) for i in range(1, 15)]:
    treaty_df.loc[
        (treaty_df[s].notna()) & ~(treaty_df[s].isin(list(blocs.keys()))), ["n_parties"]
    ] += 1
    for k, v in blocs.items():
        for i in range(len(treaty_df.loc[(treaty_df[s] == k)])):
            l = treaty_df.loc[(treaty_df[s] == k)].index.values[i]
            treaty_yr = treaty_df.loc[l, "year"]
            dist = {}
            for y in v.keys():
                if y <= treaty_yr:
                    dist[y] = treaty_yr - y
            if len(dist) > 0:
                right_key = min(dist, key=dist.get)
                # print(k, len(v[right_key]))
                treaty_df.loc[l, "n_parties"] += len(v[right_key])
                treaty_df = treaty_df.reset_index(drop=True)
            else:
                pass

# +
# treaty_df.loc[treaty_df['n_parties']==10, ['parties']].values
# -

treaty_df["n_parties"].value_counts()

treaty_df.loc[
    (treaty_df["n_parties"] > 2) & (treaty_df["is_BIT"] == 1), ["is_BIT", "is_MIT"]
] = (0, 1)

treaty_df["is_MIT"].value_counts()

len(treaty_df)

treaty_df = treaty_df.dropna(axis=0, subset=["text"])

len(treaty_df)

2584 - 2558

# Get text-derived variables

treaty_df["text"] = treaty_df["text"].str.lower()

# Replace punctiation

treaty_df["text"] = treaty_df["text"].replace(
    r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", regex=True
)

# Didn't use these

stop_en = stopwords.words("english")
stop_es = stopwords.words("spanish")

# Extra

# +
# "prohibition of performance requirements"
# r"contributions to the sustainable",
# r"workers? rights|derechos? del trab",
# r"labou?r standard",
# r"environmental measures necessary"
# investments should strive to make the maximum feasible contributions to the sustainable development of the host state and local community through high levels of socially responsible practices
# "neither contracting party may impose or enforce any of the following requirements or enforce any commitment or undertaking in connection with an investment or investment activities of an investor of the other contracting party in its territory   a to achieve a given level or percentage of domestic content   b to purchase use or accord a preference to goods produced or services provided in its territory or to purchase goods or services from a natural person or an enterprise in its territory   c to relate in any way the volume or value of imports to the volume or value of exports or to the amount of foreign exchange inflows associated with an investment of the investor   d to restrict sales of goods or services in its territory that an investment of the investor produces or provides by relating such sales in any way to the volume or value of its exports or foreign exchange earnings   e to restrict the exportation or sale for export    f  to export a given level or percentage of goods or services   g to transfer technology a production process or other proprietary knowledge to a natural person or an enterprise in its territory except those undertaken in a manner not inconsistent with the trips agreement   h to adopt   i a given rate  or amount of royalty under a license contract or   ii  a given duration of the term of a license contract    in regard to any license contract freely entered into between the investor and a natural person or an enterprise in its territory whether it has been entered into or not provided that the requirement is imposed or the commitment or undertaking is enforced by an exercise of governmental authority of the contracting party    note a  license contract  referred to in this subparagraph means any license contract concerning transfer of technology a production process or other proprietary knowledge    i  to locate the headquarters of the investor for a specific region or the world market in its territory    j to hire a given number or percentage of its nationals   k to achieve a given level or value of research and development in its territory or   l to supply one or more of the goods that the investor produces or the services that the investor provides to a specific region or the world market exclusively from its territory 2 the provisions of paragraph 1 do not preclude either contracting party from conditioning the receipt or continued receipt of an advantage in connection with an investment or investment activities of an investor of the other contracting party in its territory on compliance with     a  any requirement other than the requirements set forth in subparagraphs 1a through 1e    b a requirement to locate production supply or acquire a service train or employ workers construct or expand particular facilities or carry out research and development in its territory or   c the requirements set forth in subparagraphs 1a and 1b when the requirements relating to the content of goods necessary to qualify for preferential tariffs or preferential quotas are imposed by an importing contracting party  3 subparagraphs 1g and 1h shall not apply when the requirement is imposed or the commitment or undertaking is enforced by a court of justice administrative tribunal or competition authority to remedy an alleged violation of competition laws  4 this article does not preclude enforcement of any commitment undertaking or requirement between private parties where a contracting party did not impose or require the commitment undertaking or requirement  a"
# such performance requirements are major burdens on investors and impair their competitivenes
# treaty_df.loc[(treaty_df["text"].str.contains(
#        r"training"
#    )) &
#    ~(treaty_df["text"].str.contains(
#        r"neither party may.*impose.*enforce"
#    ))&
#    ~(treaty_df["text"].str.contains(
#        r"not impose|not enforce"
#    )), ['signer_1', 'signer_2','year']]
# -

host_int = {
    "general": [
        r"fair transparent and predictable investment",
        r"fundamental interests of society|intereses fundamentales de la sociedad|fondamentaux de la soc",
        r"policy objectives|national policy objectives|polí?i?ticas? nacional",
        r"investments should be made|investments should strive|investments must|shall not encourage investment",
        r"promptly respond",
    ],
    "environmental": [
        r"promote sustainable investment",
        r"sustainable development|desarrollo sostenible|dé?e?veloppement durable",
        r"low\s?carbon|gesto de carbon",
        r"energy efficien|eficiencia ener",
        r"\semissions? of|pollut?c?",
        r"environmental|ambiental|medioambient",
        r"ecolabel",
    ],
    "governance": [
        r"inapropiado?a?|inappropriate to encourage|no es adec?uado fomentar",
        r"human\s?rights|derechos\s?humanos|droits\s?de\sl\s?'?homme|direitos\s?humanos",
        r"poverty|pobreza|pauvre",
        r"corporate\s?social\s?responsibility|responsabilidade?\s?social|responsabilit\s?sociale",
        r"aboriginal|indigenous|indi?í?gena|indige?è?ne",
        r"corrup|anticorrup",
    ],
    "economic": [
        r"investment as an engine",
        r"sustainable development|desarrollo sostenible|dé?e?veloppement durable",
        r"development objectives|development goals|desarrollo economico",
        r"increase\s*of\s*productive\s*capacity|capacity building|creació?o?n de capacidad",
        r"maximum percentage of foreign|majority of the board of directors",
        r"research development|research activities",
    ],
}

for k in host_int.keys():
    treaty_df[k] = 0
for k, v in host_int.items():
    # val = 1/len(v)
    for regexp in v:
        treaty_df.loc[treaty_df["text"].str.contains(regexp), [k]] += 1

list(treaty_df)

treaty_df["general"].value_counts()

treaty_df["environmental"].value_counts()

treaty_df["governance"].value_counts()

treaty_df["economic"].value_counts()

treaty_df["interest_score"] = 0
for k in host_int.keys():
    treaty_df.loc[(treaty_df[k] > 0), ["interest_score"]] += 1

treaty_df["interest_score"].value_counts()

23 / 2303

treaty_df["interest_dummy"] = 0
treaty_df.loc[treaty_df["interest_score"] > 0, ["interest_dummy"]] = 1

treaty_df["interest_dummy"].value_counts()

treaty_df.to_csv("full_cleaned_iia.csv", index=False)

predictive = treaty_df[
    [
        "time_to_entry",
        "time_to_termination",
        "yr_1959",
        "yr_1960",
        "yr_1961",
        "yr_1962",
        "yr_1963",
        "yr_1964",
        "yr_1965",
        "yr_1966",
        "yr_1967",
        "yr_1968",
        "yr_1969",
        "yr_1970",
        "yr_1971",
        "yr_1972",
        "yr_1973",
        "yr_1974",
        "yr_1975",
        "yr_1976",
        "yr_1977",
        "yr_1978",
        "yr_1979",
        "yr_1980",
        "yr_1981",
        "yr_1982",
        "yr_1983",
        "yr_1984",
        "yr_1985",
        "yr_1986",
        "yr_1987",
        "yr_1988",
        "yr_1989",
        "yr_1990",
        "yr_1991",
        "yr_1992",
        "yr_1993",
        "yr_1994",
        "yr_1995",
        "yr_1996",
        "yr_1997",
        "yr_1998",
        "yr_1999",
        "yr_2000",
        "yr_2001",
        "yr_2002",
        "yr_2003",
        "yr_2004",
        "yr_2005",
        "yr_2006",
        "yr_2007",
        "yr_2008",
        "yr_2009",
        "yr_2010",
        "yr_2011",
        "yr_2012",
        "yr_2013",
        "yr_2014",
        "yr_2015",
        "yr_2016",
        "yr_2017",
        "yr_2018",
        "yr_2019",
        "dec_1950",
        "dec_1960",
        "dec_1970",
        "dec_1980",
        "dec_1990",
        "dec_2000",
        "dec_2010",
        "is_AA",
        "is_BIT",
        "is_EPA",
        "is_FTA",
        "is_MIT",
        "is_OTHER",
        "in_force",
        "signed",
        "terminated",
        "caribbean",
        "southern_asia",
        "sub_saharan_africa",
        "northern_europe",
        "southern_europe",
        "western_asia",
        "latin_america",
        "polynesia",
        "australia_and_new_zealand",
        "western_europe",
        "eastern_europe",
        "northern_america",
        "south_eastern_asia",
        "eastern_asia",
        "northern_africa",
        "melanesia",
        "micronesia",
        "central_asia",
        "gdp_delta",
        "agexp_delta",
        "polity2_delta",
        "n_parties",
        "general",
        "environmental",
        "governance",
        "economic",
        "interest_score",
        "interest_dummy",
    ]
]

predictive.to_csv("features_iia.csv", index=False)

predictive

stop_en = stopwords.words("english")

treaty_df["text_no"] = treaty_df["text"].apply(
    lambda x: " ".join([word for word in x.split() if word not in (stop_en)])
)

treaty_txt = treaty_df.loc[treaty_df["interest_dummy"] == 1, "text_no"].to_list()



word_list = []
for txt in treaty_txt:
    for var in host_int["general"]:
        if re.findall(r"((\w+\W+){0,10}\b" + var + r"\b(\W+\w+){0,10})", txt) != []:
            word_list.append(
                re.findall(r"((\w+\W+){0,10}\b" + var + r"\b(\W+\w+){0,10})", txt)[0][0]
            )
            # print(re.findall(r'((\w+\W+){0,10}\b'+var+r'\b(\W+\w+){0,10})', txt)[0][0])
    for var in host_int["economic"]:
        if re.findall(r"((\w+\W+){0,10}\b" + var + r"\b(\W+\w+){0,10})", txt) != []:
            word_list.append(
                re.findall(r"((\w+\W+){0,10}\b" + var + r"\b(\W+\w+){0,10})", txt)[0][0]
            )
    for var in host_int["environmental"]:
        if re.findall(r"((\w+\W+){0,10}\b" + var + r"\b(\W+\w+){0,10})", txt) != []:
            word_list.append(
                re.findall(r"((\w+\W+){0,10}\b" + var + r"\b(\W+\w+){0,10})", txt)[0][0]
            )
    for var in host_int["governance"]:
        if re.findall(r"((\w+\W+){0,10}\b" + var + r"\b(\W+\w+){0,10})", txt) != []:
            word_list.append(
                re.findall(r"((\w+\W+){0,10}\b" + var + r"\b(\W+\w+){0,10})", txt)[0][0]
            )

len(word_list)

alltext = " ".join(word_list)

f = open("int_treaties.txt", "w")
print(alltext, file=f)
f.close()
