import asyncio
import csv
import json
import os

import aiohttp
from bs4 import BeautifulSoup
from tqdm import tqdm


def get_most_recent_value(data):
    for item in data:
        if item.get("value") is not None:
            return item.get("value")
    return "N/A"


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def get_religion_from_wikipedia(session, country_name):
    wikipedia_url = f"https://en.wikipedia.org/wiki/{country_name}"
    content = await fetch(session, wikipedia_url)
    soup = BeautifulSoup(content, "html.parser")

    infobox = soup.find("table", {"class": "infobox"})
    if infobox:
        for row in infobox.find_all("tr"):
            header = row.find("th")
            if header and "religion" in header.get_text(strip=True).lower():
                cell = row.find("td")
                if cell:
                    religions = "|".join(
                        [
                            religion.get_text(strip=True).replace(",", "-")
                            for religion in cell.find_all("a")
                        ]
                    )
                    return religions
    return "N/A"


def get_quadrant_by_coordinates(latitude, longitude):
    if latitude > 0 and longitude > 0:
        return "NE"
    elif latitude > 0 and longitude < 0:
        return "NW"
    elif latitude < 0 and longitude > 0:
        return "SE"
    elif latitude < 0 and longitude < 0:
        return "SW"
    else:
        return "Equator or Greenwich"


async def main():
    restcountries_url = "https://restcountries.com/v3.1/all"
    worldbank_url = "http://api.worldbank.org/v2/country/{}/indicator/{}?format=json"

    country_data = []

    async with aiohttp.ClientSession() as session:
        response = await fetch(session, restcountries_url)
        countries = json.loads(response)

        for country in tqdm(countries, desc="Processing countries"):
            alpha_code = country.get("cca2").lower()
            country_name = country.get("name", {}).get("common", "N/A")
            country_name = country_name.replace(",", " -")
            zone = get_quadrant_by_coordinates(
                country.get("latlng")[0], country.get("latlng")[1]
            )
            languages = "|".join(list(country.get("languages", {}).values())) or "N/A"
            currency = (
                "|".join(
                    [
                        curr.get("name", "")
                        for curr in country.get("currencies", {}).values()
                    ]
                )
                or "N/A"
            )
            region = country.get("region", "N/A")
            subregion = country.get("subregion", "N/A")

            religion = await get_religion_from_wikipedia(session, country_name)

            country_code = country.get("cca3")
            life_expectancy_code = "SP.DYN.LE00.IN"
            fertility_rate_code = "SP.DYN.TFRT.IN"

            if country_code != "N/A":
                life_expectancy_url = worldbank_url.format(
                    country_code, life_expectancy_code
                )
                fertility_rate_url = worldbank_url.format(
                    country_code, fertility_rate_code
                )

                life_expectancy_content, fertility_rate_content = await asyncio.gather(
                    fetch(session, life_expectancy_url),
                    fetch(session, fertility_rate_url),
                )

                life_expectancy_data = json.loads(life_expectancy_content)
                fertility_rate_data = json.loads(fertility_rate_content)

                life_expectancy = (
                    get_most_recent_value(life_expectancy_data[1])
                    if len(life_expectancy_data) > 1 and life_expectancy_data[1]
                    else "N/A"
                )
                life_expectancy = (
                    (lambda x, base=5: base * round(x / base))(int(life_expectancy))
                    if life_expectancy != "N/A"
                    else 0
                )

                fertility_rate = (
                    get_most_recent_value(fertility_rate_data[1])
                    if len(fertility_rate_data) > 1 and fertility_rate_data[1]
                    else "N/A"
                )
                fertility_rate = (
                    # round(float(fertility_rate), 3)
                    int(fertility_rate)
                    if fertility_rate != "N/A"
                    else 0
                )
            else:
                life_expectancy = 0
                fertility_rate = 0

            country_data.append(
                [
                    alpha_code,
                    country_name,
                    zone,
                    languages,
                    religion,
                    currency,
                    region,
                    subregion,
                    life_expectancy,
                    fertility_rate,
                ]
            )

    current_dir = os.getcwd()
    data_path = os.path.join(current_dir, "dados", "2_country_data.csv")

    with open(data_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "Alpha Code",
                "Country or Territory",
                "Zone",
                "Languages",
                "Religion",
                "Currency",
                "Region",
                "Subregion",
                "Life Expectancy",
                "Fertility Rate",
            ]
        )
        writer.writerows(country_data)


if __name__ == "__main__":
    asyncio.run(main())
