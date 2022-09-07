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

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import seaborn as sns

"""Using complete cases across all variables, predicts how many host country interests a treaty will mention."""

df = pd.read_csv("features_iia.csv")

# +
score_features = df[
    [
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
        "interest_score",
    ]
]


dummy_features = df[
    [
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
        "interest_dummy",
    ]
]
# -

print(score_features.isnull().sum())

len(score_features)

score_features = score_features.dropna()

score_features.dtypes


# +
def label_encoder(y):
    le = LabelEncoder()
    score_features[y] = le.fit_transform(score_features[y])


label_list = ["gdp_delta", "agexp_delta", "polity2_delta"]

for l in label_list:
    label_encoder(l)
# -

score_features

# +
X = score_features.drop(["interest_score"], axis=1)
y = score_features["interest_score"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=True
)

y_train = y_train.values.reshape(-1, 1)
y_test = y_test.values.reshape(-1, 1)

print("X_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)
print("y_train shape:", y_train.shape)
print("y_test shape:", y_test.shape)
# -

# Feature Scaling
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.fit_transform(X_test)

result_dict_train = {}
result_dict_test = {}

# +
rfc = RandomForestClassifier(random_state=42)
accuracies = cross_val_score(rfc, X_train, y_train, cv=5)
rfc.fit(X_train, y_train)
y_pred = rfc.predict(X_test)

print("Train Score:", np.mean(accuracies))
print("Test Score:", rfc.score(X_test, y_test))


# -

def plot_feature_importance(importance, names):

    # Create arrays from feature importance and feature names
    feature_importance = np.array(importance)
    feature_names = np.array(names)

    # Create a DataFrame using a Dictionary
    data = {"feature_names": feature_names, "feature_importance": feature_importance}
    fi_df = pd.DataFrame(data)

    # Sort the DataFrame in order decreasing feature importance
    fi_df.sort_values(by=["feature_importance"], ascending=False, inplace=True)
    fi_df = fi_df.iloc[0:10]

    # Define size of bar plot
    plt.figure(figsize=(35, 15))
    # Plot Searborn bar chart

    sns.set(font_scale=2.5)
    sns.set_style("whitegrid")
    sns.barplot(
        x=fi_df["feature_importance"],
        y=fi_df["feature_names"],
        color="#faa200",
        alpha=0.5,
    )
    # Add chart labels
    # plt.title(model_type + 'Feature Importance')
    plt.xlabel("\nFeature Importance")
    plt.ylabel("Feature Names\n")
    plt.savefig("rfc_feature_imp.png", dpi=300)


len(list(X))

plot_feature_importance(rfc.feature_importances_, X.columns)
