import requests

# Week 1: Basic Paper Discovery & Metadata Retrieval
def get_paper_dna(paper_id):
    """
    Fetches the 'DNA' (metadata) of a research paper using Semantic Scholar API.
    Input: DOI or Semantic Scholar ID
    """
    # Using the Public API (No key required for basic testing)
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
    params = {'fields': 'title,abstract,url,citationCount,influentialCitationCount,recommendations'}
    
    response = requests.get(url, params=params)
    
    if response.status_status == 200:
        data = response.json()
        print(f"--- WEEK 1: {data.get('title')} ---")
        print(f"Citations: {data.get('citationCount')}")
        print(f"Abstract Snippet: {data.get('abstract')[:150]}...")
        return data
    else:
        print("Error fetching paper data. Check your ID.")
        return None

# Test with a sample paper DOI
if __name__ == "__main__":
    get_paper_dna("10.1145/3368089")