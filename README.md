
# KoreaPetFriendlyCrawler

## Project Overview

`KoreaPetFriendlyCrawler` is a Python-based tool that crawls pet-friendly restaurant data in South Korea. It filters restaurant data to identify pet-friendly locations, retrieves their representative images, and saves the information in both a CSV file and individual JSON files. The tool also marks whether an image is available for each restaurant.

## Features

- Filters restaurants that allow pets (pet-friendly) from a dataset.
- Retrieves detailed information for each pet-friendly restaurant using the Google Places API.
- Downloads a representative image (if available) for each restaurant.
- Saves detailed JSON data and the downloaded image for each restaurant in structured folders.
- Marks whether an image exists (`IMG_EXIST`) in the output CSV file.
  
## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/KoreaPetFriendlyCrawler.git
    ```
2. Navigate to the project directory:
    ```bash
    cd KoreaPetFriendlyCrawler
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Create a `.env` file in the root directory and add your Google Places API key:
    ```
    GOOGLE_MAPS_API_KEY=your_google_maps_api_key
    ```

## Usage

1. Prepare the input CSV file (`KC_MTPCLT_RSTRNT_DATA_2023.csv`) which contains restaurant data in South Korea, including information about whether pets are allowed.
2. Run the script:
    ```bash
    python restaurant_image_crawler.py
    ```
   - The script filters the pet-friendly restaurants and retrieves their details from the Google Places API.
   - For each restaurant, it tries to download the representative image and saves it in the `images/` folder.
   - It saves detailed information for each restaurant in `jsons/` as `details.json`.
   - The script generates a new CSV file `pet_friendly_places_with_images.csv` which contains only the pet-friendly restaurants with an `IMG_EXIST` field indicating whether the image was successfully downloaded.

## Output Structure

- **CSV Output**: `pet_friendly_places_with_images.csv`
  - A CSV file containing only pet-friendly restaurants, with an additional `IMG_EXIST` column marking if an image was found and downloaded (`Y` or `N`).
  
- **Images**: `images/{row_number}/image.jpg`
  - For each restaurant, the image is saved in an individual folder named after its row number.
  
- **Details JSON**: `jsons/{row_number}/details.json`
  - The detailed information for each restaurant (as returned by the Google Places API) is saved in a corresponding folder.

## Example

An example of the folder structure after running the script:

```
KoreaPetFriendlyCrawler/
│
├── pet_friendly_places_with_images.csv
├── images/
│   ├── 1/
│   │   └── image.jpg
│   ├── 2/
│   │   └── image.jpg
│   └── ...
└── jsons/
    ├── 1/
    │   └── details.json
    ├── 2/
    │   └── details.json
    └── ...
```

## Configuration

- The number of restaurants processed can be controlled by editing the function call in `restaurant_image_crawler.py`:
  ```python
  process_pet_friendly_places(N)
  ```
  Set `N` to the number of rows you want to process, or `-1` to process all rows.

## Dependencies

- `pandas`
- `requests`
- `python-dotenv`

Install all dependencies using:
```bash
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License.
