import os
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.cluster import KMeans
import webcolors
from math import log2


def rgb2gray(rgb):
    return np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])


def image_entropy(img):
    hist = img.histogram()
    hist_size = sum(hist)
    hist = [float(h) / hist_size for h in hist]
    entropy = -sum(p * log2(p) for p in hist if p != 0)
    return entropy / 24


def combined_complexity_score(color_complexity, img_entropy):
    return (color_complexity + img_entropy) / 2


def color_complexity_score(primary_count, secondary_count, total_count):
    primary_ratio = primary_count / total_count
    secondary_ratio = secondary_count / total_count
    complexity_score = 0.5 * primary_ratio + 0.5 * secondary_ratio
    return complexity_score


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
    # Carregue a imagem usando Pillow
    img = Image.open(image_path)

    # Converta a imagem para RGBA (incluindo o canal alfa)
    img_rgba = img.convert("RGBA")

    # Converta a imagem RGBA para um array NumPy
    img_np = np.array(img_rgba)

    # Descarte o canal alfa e mantenha apenas os canais RGB
    img_rgb = img_np[:, :, :3]

    # Calcule a entropia da imagem
    img_entropy = image_entropy(img_rgba)
    img_entropy = round(img_entropy, 3)

    # Calcule o número de cores distintas na imagem
    unique_colors = np.unique(img_rgb.reshape(-1, 3), axis=0)
    num_unique_colors = len(unique_colors)

    # Extraia as cores principais usando KMeans
    kmeans = KMeans(n_clusters=min(8, num_unique_colors), n_init=10)
    kmeans.fit(img_rgb.reshape(-1, 3))  # Use apenas os canais RGB
    main_colors = kmeans.cluster_centers_
    color_counts = np.bincount(kmeans.labels_)

    # Ignore cores com baixa presença na imagem (por exemplo, menos de 1%)
    significant_color_indices = np.where(color_counts / img_rgb.size > 0.02)[0]
    main_colors = main_colors[significant_color_indices]
    color_counts = color_counts[significant_color_indices]

    # Converta as cores principais para formatos legíveis e obtenha os nomes das cores
    main_colors = [tuple(map(int, color)) for color in main_colors]
    color_names = [get_color_name(color) for color in main_colors]
    color_names = '|'.join(color_names)

    # Contagem de cores principais
    num_colors = len(set(main_colors))

    # Encontre a cor predominante após a filtragem das cores significativas
    predominant_color_index = np.argmax(color_counts)
    predominant_color = main_colors[predominant_color_index]
    predominant_color_name = get_color_name(predominant_color)

    secondary_color_rgb = secondary_color(main_colors, color_counts)
    secondary_color_name = get_color_name(secondary_color_rgb)

    # Contagem de cores primárias e secundárias
    primary_count = color_counts[predominant_color_index]
    secondary_count = color_counts[np.argmax(color_counts)]

    # Calcule a pontuação de complexidade das cores
    complexity_score = round(color_complexity_score(primary_count, secondary_count, img_rgb.size), 3)

    # Calcule a pontuação combinada de complexidade
    combined_complexity = combined_complexity_score(complexity_score, img_entropy)
    combined_complexity = round(combined_complexity, 3)

    print(image_path)

    return {
        "alpha_code": os.path.splitext(os.path.basename(image_path))[0],
        "num_colors": num_colors,
        "color_complexity_score": complexity_score,
        "image_entropy_score": img_entropy,
        "combined_complexity_score": combined_complexity,
        "predominant_color_name": predominant_color_name,
        "secondary_color": secondary_color_name,
        "color_names": color_names,
    }


def main():
    current_dir = os.getcwd()
    flags_path = os.path.join(current_dir, "flags")
    dados_path = os.path.join(current_dir, "dados", "1_flags_features.csv")

    flags = [os.path.join(flags_path, f) for f in os.listdir(flags_path)]
    features = [extract_features(flag) for flag in flags]

    df = pd.DataFrame(features)
    df.to_csv(dados_path, index=False)

if __name__ == "__main__":
    main()