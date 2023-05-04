import os
from zipfile import ZipFile

import numpy as np
import pandas as pd
import requests
import tqdm
import webcolors
from PIL import Image
from sklearn.cluster import KMeans
from tqdm import tqdm


def download_and_extract_flags(url, output_dir):
    if os.path.exists(output_dir):
        user_input = input(
            f'O diretório "{output_dir}" já existe. Deseja continuar? (s/n): '
        )
        if user_input.lower() != "s":
            print("Download cancelado.")
            return

    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024

    zip_file_name = os.path.basename(url)

    progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)
    with open(zip_file_name, "wb") as f:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            f.write(data)
    progress_bar.close()

    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("Falha no download.")

    os.makedirs(output_dir, exist_ok=True)

    with ZipFile(zip_file_name, "r") as zip_ref:
        zip_ref.extractall(output_dir)


def remove_large_filenames(directory):
    print("Removendo bandeiras desnecessárias...")

    for filename in os.listdir(directory):
        name, extension = os.path.splitext(filename)

        if len(name) > 2:
            file_path = os.path.join(directory, filename)
            os.remove(file_path)
            print(f"Removido: {file_path}")


def closest_color(requested_color):
    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]


def get_color_name(requested_color):
    try:
        color_name = webcolors.rgb_to_name(requested_color)
    except ValueError:
        color_name = closest_color(requested_color)
    return color_name


def secondary_color(main_colors, color_counts):
    max_count_index = np.argmax(color_counts)
    color_counts[max_count_index] = 0  # Zera a contagem da cor predominante
    secondary_count_index = np.argmax(color_counts)
    return main_colors[secondary_count_index]


def extract_features(image_path):
    img = Image.open(image_path)
    img_rgba = img.convert("RGBA")
    img_np = np.array(img_rgba)

    # Descarte o canal alfa e mantenha apenas os canais RGB
    img_rgb = img_np[:, :, :3]

    # Calcule o número de cores distintas na imagem
    unique_colors = np.unique(img_rgb.reshape(-1, 3), axis=0)
    num_unique_colors = len(unique_colors)

    # Extrai as cores principais usando KMeans
    kmeans = KMeans(n_clusters=min(8, num_unique_colors), n_init=10)
    kmeans.fit(img_rgb.reshape(-1, 3))  # Use apenas os canais RGB
    main_colors = kmeans.cluster_centers_
    color_counts = np.bincount(kmeans.labels_)

    # Ignore cores com baixa presença na imagem (por exemplo, menos de 1%)
    significant_color_indices = np.where(color_counts / img_rgb.size > 0.02)[0]
    main_colors = main_colors[significant_color_indices]
    color_counts = color_counts[significant_color_indices]

    # Converção das cores principais para formatos nomes legíveis
    main_colors = [tuple(map(int, color)) for color in main_colors]
    color_names = [get_color_name(color) for color in main_colors]
    color_names = "|".join(color_names)

    # Contagem de cores principais
    num_colors = len(set(main_colors))

    # Encontre a cor predominante após filtragem das cores significativas
    predominant_color_index = np.argmax(color_counts)
    predominant_color = main_colors[predominant_color_index]
    predominant_color_name = get_color_name(predominant_color)

    secondary_color_rgb = secondary_color(main_colors, color_counts)
    secondary_color_name = get_color_name(secondary_color_rgb)

    print(image_path)

    return {
        "alpha_code": os.path.splitext(os.path.basename(image_path))[0],
        "num_colors": num_colors,
        "predominant_color_name": predominant_color_name,
        "secondary_color": secondary_color_name,
        "color_names": color_names,
    }


def main():
    url = "https://flagcdn.com/w2560.zip"

    current_dir = os.getcwd()
    flags_path = os.path.join(current_dir, "flags")
    dados_path = os.path.join(current_dir, "dados", "1_flags_features.csv")

    download_and_extract_flags(url, flags_path)
    remove_large_filenames(flags_path)

    print("Iniciando análise...")

    flags = [os.path.join(flags_path, f) for f in os.listdir(flags_path)]
    features = [extract_features(flag) for flag in flags]

    df = pd.DataFrame(features)
    df.to_csv(dados_path, index=False)


if __name__ == "__main__":
    main()
