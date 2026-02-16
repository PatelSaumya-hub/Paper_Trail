import os
import re
import io
import pickle
import platform
import subprocess
import requests
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text

# --- 1. UTILITIES ---
def savePubs(filename, pubs_to_save):
    with open(filename, 'wb') as f:
        pickle.dump(pubs_to_save, f)
    print(f"Successfully saved to {filename}")

def loadPubs(filename):
    if not os.path.exists(filename): 
        print(f"File {filename} not found.")
        return []
    with open(filename, 'rb') as f:
        return pickle.load(f)

# --- 2. PDF & TEXT PROCESSING ---
def convertPDF(pdf_path):
    # Added headers to mimic a browser to avoid 403 Forbidden errors
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        if pdf_path.startswith('http'):
            r = requests.get(pdf_path, headers=headers, timeout=15)
            r.raise_for_status()
            return extract_text(io.BytesIO(r.content))
        return extract_text(pdf_path)
    except Exception as e:
        print(f"  Error reading PDF: {e}")
        return ""

def stringToWordDictionary(text):
    text = text.lower()
    # Captures words only, ignores numbers/punctuation
    words = [w for w in re.findall(r'[a-z\-]+', text) if len(w) > 2]
    # Expanded stopwords for better analysis
    stopwords = {'the', 'and', 'for', 'that', 'can', 'this', 'which', 'are', 'from', 'our', 'not', 'with', 'cid', 'was', 'were'}
    d = {}
    for w in words:
        if w not in stopwords: 
            d[w] = d.get(w, 0) + 1
    return d

# --- 3. ANALYSIS ---
def calculate_similarity(train_pubs, test_pub):
    """Computes Dice Coefficient similarity between a target paper and a list of papers."""
    if 'pdf_text' not in test_pub or not test_pub['pdf_text']: return []
    
    test_words = set(test_pub['pdf_text'].keys())
    results = []
    
    for p in train_pubs:
        if 'pdf_text' not in p or not p['pdf_text'] or p['title'] == test_pub['title']:
            continue
        
        train_words = set(p['pdf_text'].keys())
        overlap = len(test_words.intersection(train_words))
        score = 2.0 * overlap / (len(train_words) + len(test_words))
        results.append((p['title'], score))
    
    # Sort by highest similarity
    return sorted(results, key=lambda x: x[1], reverse=True)

# --- 4. SCRAPER ---
def scrape_nips(year=2023):
    pubs = []
    base_url = "https://proceedings.neurips.cc"
    url = f"{base_url}/paper_headings/Abstract/{year}"
    
    print(f"Scraping metadata for {year}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # NeurIPS structure: find links that point to 'Abstract' then convert to 'Paper'
    links = soup.find_all('a', href=re.compile(r'/hash/.*-Abstract-Conference\.html$'))
    
    for link in links:
        # Convert Abstract URL to PDF URL
        pdf_url = link.get('href').replace("-Abstract-Conference.html", "-Paper-Conference.pdf")
        pubs.append({
            'title': link.text,
            'pdf': base_url + pdf_url,
            'year': year
        })
    return pubs

# --- 5. EXECUTION ---
if __name__ == "__main__":
    # Step 1: Gather paper URLs
    # Using 2023 as an example
    raw_data = scrape_nips(2023)
    print(f"Found {len(raw_data)} papers.")

    # Step 2: Process a small batch (Limiting to 5 for speed)
    processed_pubs = []
    limit = 5
    
    print(f"Step 2: Processing first {limit} papers...")
    for i, paper in enumerate(raw_data[:limit]):
        print(f"[{i+1}/{limit}] Downloading & Analyzing: {paper['title'][:50]}...")
        full_text = convertPDF(paper['pdf'])
        if full_text:
            paper['pdf_text'] = stringToWordDictionary(full_text)
            processed_pubs.append(paper)

    # Step 3: Save results
    savePubs('pubs_nips.pkl', processed_pubs)

    # Step 4: Search and Analyze
    db = loadPubs('pubs_nips.pkl')
    if db:
        # Example 1: Search for a keyword
        keyword = 'learning'
        matches = [p['title'] for p in db if keyword in p.get('pdf_text', {})]
        print(f"\nFound {len(matches)} papers containing the word '{keyword}'.")

        # Example 2: Similarity Analysis
        if len(db) > 1:
            print(f"\nCalculating similarity for: {db[0]['title']}")
            sims = calculate_similarity(db, db[0])
            for title, score in sims[:3]:
                print(f" - {score:.2f} match with: {title}")
