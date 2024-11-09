import json

def add_downloads_to_json(filename):
    """Adds the "downloads": {"internetarchive": ""} field to each item in a JSON file.

    Args:
        filename (str): The path to the JSON file.
    """

    with open(filename, 'r') as f:
        data = json.load(f)

    for item in data:
        item['downloads'] = {'internetarchive': ''}

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    filename = 'winvista.json'  # Replace with your actual filename
    add_downloads_to_json(filename)