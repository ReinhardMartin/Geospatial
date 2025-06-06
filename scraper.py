import os
import yaml
import requests
import json
import time
import re

from bs4 import BeautifulSoup
from rich.progress import Progress
from rich.console import Console
from rich.table import Table
from urllib.parse import urljoin

def scrape_idealista(url: str) -> list[dict]:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        all_homes = []
        with Progress() as progress:
            task = progress.add_task(
                "[green]Collecting: Please stand by...", total=None
            )
            current_url = url
            while current_url:
                response = requests.get(current_url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")

                listings = soup.find_all("article", class_="item")
                for listing in listings:
                    title = listing.find("a", class_="item-link").text.strip()
                    price_euro = listing.find("span", class_="item-price").text.strip()
                    link_path = listing.find("a", class_="item-link")["href"]
                    link = urljoin(url, link_path)

                    try:
                        time.sleep(1)  # Prevents request spam
                        listing_response = requests.get(link, headers=headers)
                        listing_response.raise_for_status()
                        listing_soup = BeautifulSoup(listing_response.content, "html.parser")

                        details_property_section = listing_soup.find_all("div", class_="details-property-feature-one")
                        details_property_section = details_property_section[1]
                        features_list = details_property_section.find_all("li")

                        area = floor = rooms = bathrooms = "N/A"

                        for feature in features_list:
                            text = feature.text.strip()

                            area_match = re.search(r"(\d{1,3})\s*m²", text)
                            if area_match:
                                area = area_match.group(1)

                            if "piano" in text.lower():
                                if "terra" in text.lower():
                                    floor = "0"  # Ground floor
                                else:
                                    floor_match = re.search(r"(\d+)º?\s*piano", text) 
                                    if floor_match:
                                        floor = floor_match.group(1)

                            if "locali" in text:  # Multiple rooms
                                rooms_match = re.search(r"(\d+)\s*locali", text)
                                if rooms_match:
                                    rooms = rooms_match.group(1)
                            elif "locale" in text:  # Single room
                                rooms = "1"

                            if "bagni" in text:  # Multiple bathrooms
                                bathrooms_match = re.search(r"(\d+)\s*bagni", text)
                                if bathrooms_match:
                                    bathrooms = bathrooms_match.group(1)
                            elif "bagno" in text:  # Single bathroom
                                bathrooms = "1"

                        location = "N/A"
                        location_section = listing_soup.find("div", id="headerMap")
                        if location_section:
                            location_list = location_section.find_all("li", class_="header-map-list")
                            if location_list:
                                location = location_list[0].text.strip()

                    except requests.exceptions.RequestException as e:
                        print(f"[WARNING] Could not fetch details for {link}: {e}")

                    home_info = {
                        "Title": title,
                        "Price (Euro)": price_euro,
                        "Area (m²)": area,
                        "Floor": floor,
                        "Rooms": rooms,
                        "Bathrooms": bathrooms,
                        "Location": location,
                    }
                    all_homes.append(home_info)

                progress.advance(task)

                next_page = soup.find("li", class_="next")
                if next_page:
                    next_link = next_page.find("a", class_="icon-arrow-right-after")
                    if next_link and "href" in next_link.attrs:
                        current_url = urljoin(url, next_link["href"])
                    else:
                        print("[INFO] No more pages found. Stopping pagination.")
                        break 
                else:
                    print("[INFO] No 'next' button found. Stopping pagination.")
                    break

        return all_homes
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
        exit()
    except requests.exceptions.RequestException as e:
        print("Failed to fetch data:", e)
        return []
    except Exception as e:
        print("An error occurred:", e)
        return []


def read_config() -> str:
    with open("data/config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
        return config.get("url", "")

def save_to_json(data: list[dict], filename: str = "idealista_data.json"):
    """Saves data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"[INFO] Data saved to {filename}")

if __name__ == "__main__":
    url = read_config()
    homes = scrape_idealista(url)

    if homes:
        console = Console()

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("No.", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Price (Euro)", style="yellow")
        table.add_column("Area (m²)", style="cyan")
        table.add_column("Floor", style="blue")
        table.add_column("Rooms", style="magenta")
        table.add_column("Bathrooms", style="magenta")
        table.add_column("Location", style="green")

        for idx, home in enumerate(homes, start=1):
            table.add_row(
                str(idx),
                home["Title"],
                home["Price (Euro)"],
                home.get("Area (m²)", "N/A"),
                home.get("Floor", "N/A"),
                home.get("Rooms", "N/A"),
                home.get("Bathrooms", "N/A"),
                home.get("Location", "N/A"),
            )

        console.print(table)
        save_to_json(homes)