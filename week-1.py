#import requests
import requests

def get_paper_metadata(paper_id):
    """
    Function 1: Fetches raw JSON data from Semantic Scholar API.
    Separated so you can debug API connection issues easily.
    """
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
    query_params = {'fields': 'title,abstract,url,citationCount,year'}
    
    try:
        response = requests.get(url, params=query_params, timeout=10)
        response.raise_for_status() # This will catch 404 or 500 errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
        return None

def extract_abstract(data):
    """
    Function 2: Safely extracts only the abstract from the metadata.
    Separated so you can debug missing data issues.
    """
    if data and 'abstract' in data:
        return data['abstract']
    print("Warning: Abstract not found in paper metadata.")
    return ""

# Test Section
if _name_ == "_main_":
    sample_id = "10.1145/3368089"
    raw_data = get_paper_metadata(sample_id)
    abstract = extract_abstract(raw_data)
    
    if abstract:
        print(f"Successfully retrieved abstract for: {raw_data.get('title')}")
