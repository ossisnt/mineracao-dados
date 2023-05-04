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


# Função para selecionar o valor de maior peso ou o segundo de maior peso, caso a soma dos demais seja maior
def weighted_max(values, weights, adjustment_factor=0.8):
    sorted_values = sorted(values, key=lambda x: weights.get(x, 0), reverse=True)

    if len(sorted_values) > 1 and weights[sorted_values[0]] * adjustment_factor < sum(
        weights[v] for v in sorted_values[1:]
    ):
        return sorted_values[1]
    else:
        return sorted_values[0]


# Substituir os múltiplos valores pelo valor de maior peso ou o segundo de maior peso, conforme a lógica descrita
for col in multi_value_columns:
    if col == "religion":
        df[col] = df[col].apply(
            lambda x: weighted_max(x.split("|"), weights, 0.8)
            if isinstance(x, str)
            else x
        )
    else:
        df[col] = df[col].apply(
            lambda x: max(x.split("|"), key=lambda y: weights.get(y, 0))
            if isinstance(x, str)
            else x
        )

df.fillna("N/A", inplace=True)

dataset_final = os.path.join(current_dir, "dados", "4_dataset_final.csv")
df.to_csv(dataset_final, index=False, encoding="utf-8-sig")
