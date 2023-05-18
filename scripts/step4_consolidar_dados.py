import os

import pandas as pd

external_selected_columns = [
    "pop2023",
    "cca2",
    "density",
    "hdiTier",
    "area",
    "landAreaKm",
    "growthRate",
    "hdi2021",
    "densityMi",
]

current_dir = os.getcwd()
merged_data_path = os.path.join(current_dir, "dados", "3_dataset_pre_consolidacao.csv")

developed_path = os.path.join(current_dir, "dados", "developed.csv")
developing_path = os.path.join(current_dir, "dados", "developing.csv")

developed_df = pd.read_csv(developed_path, usecols=external_selected_columns)
developing_df = pd.read_csv(developing_path, usecols=external_selected_columns)

developed_df["country_or_territory_status"] = "Developed"
developing_df["country_or_territory_status"] = "Developing"

status_df = pd.concat([developed_df, developing_df], ignore_index=True)
status_df["cca2"] = status_df["cca2"].str.lower()

df = pd.read_csv(merged_data_path)
df = pd.merge(
    df, status_df, left_on="alpha_code", right_on="cca2", how="left", validate="1:1"
)


def calculate_weights(dataframe, columns):
    weights = {}
    for col in columns:
        values = dataframe[col].str.split("|").explode().value_counts()
        weights.update(values)
    return weights


multi_value_columns = ["languages", "religion", "currency", "color_names"]
weights = calculate_weights(df, multi_value_columns)


def primary_secondary_values(values, weights):
    sorted_values = sorted(values, key=lambda x: weights.get(x, 0), reverse=True)
    primary = sorted_values[0]
    secondary = sorted_values[1] if len(sorted_values) > 1 else primary
    return primary, secondary


for col in ["languages", "religion", "currency"]:
    df[f"{col}_primary"], df[f"{col}_secondary"] = zip(
        *df[col].apply(
            lambda x: primary_secondary_values(x.split("|"), weights)
            if isinstance(x, str)
            else (x, x)
        )
    )
    df.drop(col, axis=1, inplace=True)


df["most_ranked_color"] = df["color_names"].apply(
    lambda x: max(x.split("|"), key=lambda y: weights.get(y, 0))
    if isinstance(x, str)
    else x
)


df.drop("alpha_code", axis=1, inplace=True)
df.drop("cca2", axis=1, inplace=True)
df.drop("color_names", axis=1, inplace=True)
df.rename(columns={"predominant_color_name": "primary_color"}, inplace=True)

# Tratamento de valores nulos
fill_values = {col: "Other" for col in df.columns}

numeric_columns = [
    "pop2023",
    "density",
    "area",
    "landAreaKm",
    "growthRate",
    "hdi2021",
    "densityMi",
]
for col in numeric_columns:
    fill_values[col] = 0

fill_values["country_or_territory_status"] = "Unknown"
df.fillna(fill_values, inplace=True)


columns_order = [
    "country_or_territory",
    "zone",
    "region",
    "subregion",
    "life_expectancy",
    "fertility_rate",
    "num_colors",
    "primary_color",
    "secondary_color",
    "most_ranked_color",
    "currency_primary",
    "currency_secondary",
    "languages_primary",
    "languages_secondary",
    "religion_primary",
    "religion_secondary",
    "pop2023",
    "density",
    "hdiTier",
    "area",
    "landAreaKm",
    "growthRate",
    "hdi2021",
    "densityMi",
    "country_or_territory_status",
]

df = df[columns_order]

dataset_final = os.path.join(current_dir, "dados", "4_dataset_final.csv")
df.to_csv(dataset_final, index=False, encoding="utf-8")
