import os
import pandas as pd
import itertools

# Função para criar combinações únicas
def create_combinations(df, columns):
    combinations = []
    for index, row in df.iterrows():
        values = [row[col].split("|") if isinstance(row[col], str) and row[col] != "N/A" else [row[col]] for col in columns]
        for combination in itertools.product(*values):
            new_row = row.copy()
            for idx, col in enumerate(columns):
                new_row[col] = combination[idx]
            combinations.append(new_row)
    return pd.DataFrame(combinations)

# Carregar conjunto de dados mesclado
current_dir = os.getcwd()
merged_data_path = os.path.join(current_dir, "dados", "3_dataset_pre_consolidacao.csv")

merged_data = pd.read_csv(merged_data_path)

# Especificar colunas com campos multivalorados
multi_value_columns = ["languages", "religion", "currency", "color_names"]

# Criar combinações únicas para as colunas especificadas
unique_combinations = create_combinations(merged_data, multi_value_columns)

# Salvar o conjunto de dados com combinações únicas em um arquivo CSV (UTF-8 sem BOM)
dataset_final = os.path.join(current_dir, "dados", "4_dataset_final.csv")

with open(dataset_final, "w", newline="", encoding="utf-8-sig") as csvfile:
    unique_combinations.to_csv(csvfile, index=False)
