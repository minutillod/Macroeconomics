import requests
import os

# List of URLs to download
urls_to_download = [
    "https://www.rba.gov.au/chart-pack/images/au-growth/gdp-growth.svg",
]

# Directory to save the downloaded files
download_directory = "downloaded_files"

# Create the directory if it doesn't exist
os.makedirs(download_directory, exist_ok=True)

for url in urls_to_download:
    try:
        # Get the filename from the URL
        filename = os.path.join(download_directory, os.path.basename(url))

        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Save the content to the local file
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
    except IOError as e:
        print(f"Error saving file {filename}: {e}")
