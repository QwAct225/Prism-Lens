import os
import json
import csv
from typing import Dict, List, Any, Optional


def ensure_dir(directory: str) -> None:
    """Ensure that a directory exists, creating it if necessary"""
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_json(data: Any, filepath: str) -> None:
    """Save data to a JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(filepath: str) -> Any:
    """Load data from a JSON file"""
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_csv(filepath: str) -> List[Dict[str, Any]]:
    """Read a CSV file and return a list of dictionaries"""
    if not os.path.exists(filepath):
        return []

    result = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            result.append(dict(row))

    return result


def write_csv(data: List[Dict[str, Any]], filepath: str, fieldnames: Optional[List[str]] = None) -> None:
    """Write a list of dictionaries to a CSV file"""
    if not data:
        return

    if fieldnames is None:
        fieldnames = list(data[0].keys())

    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)