import os

import pandas as pd

current_dir = os.getcwd()
merged_data_path = os.path.join(current_dir, "dados", "3_dataset_pre_consolidacao.csv")
df = pd.read_csv(merged_data_path)


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

df.drop("color_names", axis=1, inplace=True)
df.rename(columns={"predominant_color_name": "primary_color"}, inplace=True)
df.fillna("Other", inplace=True)

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
]
df = df[columns_order]

dataset_final = os.path.join(current_dir, "dados", "4_dataset_final.csv")
df.to_csv(dataset_final, index=False, encoding="utf-8")

# dummies
df_transformed = df.copy().drop(df.columns[0], axis=1)
dummies = pd.get_dummies(df_transformed, prefix_sep="_", columns=df_transformed.columns)
dummies.insert(0, df.columns[0], df[df.columns[0]])
df = dummies

dataset_final_transformed = os.path.join(current_dir, "dados", "4_dataset_final_transformed.csv")
df.to_csv(dataset_final_transformed, index=False, encoding="utf-8")