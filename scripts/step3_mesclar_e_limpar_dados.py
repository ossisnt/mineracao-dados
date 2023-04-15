import os
import pandas as pd
import re
import unicodedata


def normalize_special_characters(text):
    normalized_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8-sig")
    return normalized_text


def clean_multivalue_field(field_value):
    if isinstance(field_value, float):
        field_value = str(field_value)
    field_value = re.sub(r"\[[^]]*\]", "", field_value)
    field_value = re.sub(r"\|\|", "|", field_value)
    field_value = field_value.rstrip("|")
    return field_value


def clean_religion_field(field_value):
    field_value = clean_multivalue_field(field_value)
    field_values = field_value.split("|")
    field_values = [re.sub(r"'(.)", "", value.strip()) for value in field_values]
    field_value = "|".join(field_values)
    field_value = re.sub(r"(?i)(other|none|no religion|official)s?\|?", "", field_value)
    field_value = field_value.strip("|")
    if field_value == "":
        field_value = "N/A"
    return field_value


# Ler os conjuntos de dados
current_dir = os.getcwd()
flags_features_path = os.path.join(current_dir, "dados", "1_flags_features.csv")
country_data_path = os.path.join(current_dir, "dados", "2_country_data.csv")

flags_features = pd.read_csv(flags_features_path)
country_data = pd.read_csv(country_data_path)

# Mesclar os conjuntos de dados com base no 'alpha_code'
merged_data = country_data.merge(flags_features, left_on="Alpha Code", right_on="alpha_code", how="outer").drop(columns=["alpha_code"])

# Reordenar as colunas para mover as colunas multivaloradas para o final
columns_order = [
    "Alpha Code", "Country", "Population", "Region", "Subregion", "Life Expectancy", "Fertility Rate",
    "Currency", "Languages", "Religion", "num_colors", "color_complexity_score",
    "image_entropy_score", "combined_complexity_score", "predominant_color_name",
    "secondary_color", "color_names"
]
merged_data = merged_data[columns_order]

# Renomear as colunas para minúsculas e substituir espaços por underscores
merged_data.columns = [col.lower().replace(" ", "_") for col in merged_data.columns]

# Limpar campos multivalorados (remover colchetes e seus conteúdos)
merged_data["languages"] = merged_data["languages"].apply(clean_multivalue_field)
merged_data["currency"] = merged_data["currency"].apply(clean_multivalue_field)
merged_data["religion"] = merged_data["religion"].apply(clean_religion_field)

# Normalizar caracteres especiais em todas as colunas
for col in merged_data.columns:
    merged_data[col] = merged_data[col].apply(lambda x: normalize_special_characters(str(x)) if isinstance(x, str) else x)

# Converter a coluna 'fertility_rate' para 'str'
merged_data["fertility_rate"] = merged_data["fertility_rate"].astype(str)

# Preencher campos em branco com "N/A"
merged_data.fillna("N/A", inplace=True)

# Substituir "nan" por "N/A" (após converter 'fertility_rate' para 'str')
merged_data.replace("nan", "N/A", inplace=True)

# Ordenar pelo campo 'alpha_code'
merged_data.sort_values(by="alpha_code", inplace=True)

# Salvar o conjunto de dados mesclado em um arquivo CSV (UTF-8 sem BOM)
dataset_path = os.path.join(current_dir, "dados", "3_dataset_pre_consolidacao.csv")

with open(dataset_path, "w", newline="", encoding="utf-8-sig") as csvfile:
    merged_data.to_csv(csvfile, index=False)
