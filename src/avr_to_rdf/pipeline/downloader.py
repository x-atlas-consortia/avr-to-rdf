"""Download AVR data from the API."""

import json
from pathlib import Path
import requests


def download_avr_data(output_path: Path, api_url: str = "https://avr.xconsortia.org/antibodies") -> None:
    """
    Download all AVR data from the API.
    
    Args:
        output_path: Path to save the JSON output
        api_url: Base URL for the AVR API
    """
    print(f"Downloading from {api_url}...")
    
    response = requests.get(api_url, timeout=60)
    response.raise_for_status()
    
    data = response.json()
    antibodies = data.get("antibodies", [])
    
    # Save to JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({"antibodies": antibodies}, f, indent=2)
    
    print(f"Downloaded {len(antibodies)} antibodies to {output_path}")
