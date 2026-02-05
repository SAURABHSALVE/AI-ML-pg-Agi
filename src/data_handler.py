import json
import os
from datetime import datetime
import pandas as pd

DATA_FILE = "data/candidates.json"

def init_db():
    """Initialize the local JSON storage if it doesn't exist."""
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)

def save_candidate_info(data):
    """Save candidate information to the local JSON file.
    
    Args:
        data (dict): Dictionary containing candidate details.
    """
    init_db()
    
    # Add timestamp
    data['timestamp'] = datetime.now().isoformat()
    
    try:
        with open(DATA_FILE, 'r') as f:
            current_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        current_data = []

    current_data.append(data)
    
    with open(DATA_FILE, 'w') as f:
        json.dump(current_data, f, indent=4)
        
def get_all_candidates():
    """Retrieve all candidates as a DataFrame (for internal viewing/debugging)."""
    init_db()
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)
