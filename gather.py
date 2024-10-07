import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
}

page_ids = [
    {"page_id": "Windows_1.0", "save_name": "win1"},
    {"page_id": "Windows_2.x", "save_name": "win2"},
    {"page_id": "Windows_3.0", "save_name": "win3"},
    {"page_id": "Windows_3.1x", "save_name": "win31"},
    {"page_id": "Windows_95", "save_name": "win95"},
    {"page_id": "Windows_Nashville", "save_name": "winnashville"},
    {"page_id": "Windows_98", "save_name": "win98"},
    {"page_id": "Windows_2000", "save_name": "win2000"},
    {"page_id": "Windows_ME", "save_name": "winme"},
    {"page_id": "Windows_Neptune", "save_name": "winneptune"},
    {"page_id": "Windows_XP", "save_name": "winxp"},
    {"page_id": "Windows_Vista", "save_name": "winvista"},
    {"page_id": "Windows_7", "save_name": "win7"},
    {"page_id": "Windows_8", "save_name": "win8"},
    {"page_id": "Windows_8.1", "save_name": "win81"},
    {"page_id": "Windows_10_(original_release)", "save_name": "win10_original"},
    {"page_id": "Cobalt", "save_name": "cobalt"},
    {"page_id": "Windows_10X", "save_name": "win10x"},
    {"page_id": "Windows_11_(original_release)", "save_name": "win11_original"}
]

base_url = "https://betawiki.net"
desired_color = "color:#009245;"
output_dir = "betas"
os.makedirs(output_dir, exist_ok=True)

def get_compiled_date(build_url):
    try:
        response = requests.get(build_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve build page {build_url}")
            return None
    except Exception as e:
        print(f"Error retrieving {build_url}: {e}")
        return None
    
    soup = BeautifulSoup(response.content, "html.parser")
    compiled_on_row = soup.find("th", class_="ib-label", text="Compiled on")
    
    if compiled_on_row:
        compiled_date = compiled_on_row.find_next("span", class_="mw-formatted-date")
        if compiled_date:
            date_str = compiled_date.get_text(strip=True)
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    
    return None

def scrape_page(page_id, save_name):
    filepath = os.path.join(output_dir, f"{save_name}.json")
    
    # Load existing builds if the file exists
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            result = json.load(file)
    else:
        result = []
    
    url = f"{base_url}/wiki/{page_id}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve page {page_id}")
        return
    
    soup = BeautifulSoup(response.content, "html.parser")
    known_builds_section = soup.find("span", id="List_of_known_builds")
    if not known_builds_section:
        print(f"'List of known builds' not found in page {page_id}")
        return
    
    content = known_builds_section.find_parent()
    current_channel = None
    
    for sibling in content.find_next_siblings():
        if sibling.name == "h3" and sibling.find("span", class_="mw-headline"):
            current_channel = sibling.get_text(strip=True).replace("[edit|edit source]", "")
        
        spans = sibling.find_all("span", style=desired_color)
        for span in spans:
            build_info = span.get_text(strip=True)
            if build_info and build_info != "Available build":
                build_link_tag = span.find_parent("a")
                if build_link_tag and build_link_tag.get("href"):
                    build_url = base_url + build_link_tag["href"]
                    
                    # Check if the build is already in the result list
                    if any(item['build'] == build_info for item in result):
                        print(f"Build {build_info} already exists, skipping...")
                        continue
                    
                    print(build_info)
                    compiled_date = get_compiled_date(build_url)

                    # Create a new entry for the build
                    new_entry = {
                        "channel": current_channel,
                        "build": build_info,
                        "compiled_date": compiled_date if compiled_date else "Unknown"
                    }

                    # Insert in order
                    insert_index = next((i for i, item in enumerate(result) if item['build'] > build_info), len(result))
                    result.insert(insert_index, new_entry)

    with open(filepath, "w") as outfile:
        json.dump(result, outfile, indent=4)

for page in page_ids:
    scrape_page(page["page_id"], page["save_name"])
    print(f"Page {page['page_id']} scraped and saved as {page['save_name']}.json.")
