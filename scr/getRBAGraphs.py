import requests
import os
import cairosvg

base_url = "https://www.rba.gov.au/chart-pack/images/"

# List of URLs to download
urls_to_download = [
    f"{base_url}world-economy/gdp-growth-advanced-economies.svg",
    f"{base_url}world-economy/gdp-growth-china-and-india.svg",
    f"{base_url}world-economy/inflation-advanced-economies.svg",
    f"{base_url}au-growth/gdp-growth.svg",
]

# Directory to save the downloaded files
download_directory = "downloaded_files"
os.makedirs(download_directory, exist_ok=True)

for url in urls_to_download:
    try:
        # Get the filename from the URL
        svg_filename = os.path.basename(url)
        svg_path = os.path.join(download_directory, svg_filename)
        png_path = svg_path.replace(".svg", ".png")

        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Save SVG file locally
        with open(svg_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Downloaded: {svg_filename}")

        # ✅ Convert SVG → PNG using CairoSVG
        cairosvg.svg2png(url=svg_path, write_to=png_path)
        print(f"🎨 Converted to PNG: {os.path.basename(png_path)}")

        # (Optional) remove the SVG if you only want the PNG
        # os.remove(svg_path)

    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading {url}: {e}")
    except IOError as e:
        print(f"❌ Error saving or converting {svg_filename}: {e}")

print("\n✅ All downloads and conversions complete!")

# import requests
# import os

# base_url = "https://www.rba.gov.au/chart-pack/images/"

# # List of URLs to download
# urls_to_download = [
#     f"{base_url}world-economy/gdp-growth-advanced-economies.svg",
#     f"{base_url}world-economy/gdp-growth-china-and-india.svg",
#     f"{base_url}world-economy/inflation-advanced-economies.svg",
#     f"{base_url}au-growth/gdp-growth.svg",
# ]

# # Directory to save the downloaded files
# download_directory = "downloaded_files"

# # Create the directory if it doesn't exist
# os.makedirs(download_directory, exist_ok=True)

# for url in urls_to_download:
#     try:
#         # Get the filename from the URL
#         filename = os.path.join(download_directory, os.path.basename(url))

#         # Send a GET request to the URL
#         response = requests.get(url, stream=True)
#         response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

#         # Save the content to the local file
#         with open(filename, 'wb') as f:
#             for chunk in response.iter_content(chunk_size=8192):
#                 f.write(chunk)
#         print(f"Downloaded: {filename}")

#     except requests.exceptions.RequestException as e:
#         print(f"Error downloading {url}: {e}")
#     except IOError as e:
#         print(f"Error saving file {filename}: {e}")
