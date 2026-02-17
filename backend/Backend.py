import os
import re
import io
import pickle
import requests
import arxiv 
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
    words = [w for w in re.findall(r'[a-z\-]+', text) if len(w) > 2]
    stopwords = {'the', 'and', 'for', 'that', 'can', 'this', 'which', 'are', 'from', 'our', 'not', 'with', 'cid', 'was', 'were'}
    d = {}
    for w in words:
        if w not in stopwords: 
            d[w] = d.get(w, 0) + 1
    return d

# --- 3. ANALYSIS ---
def calculate_similarity(train_pubs, test_pub):
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
    
    return sorted(results, key=lambda x: x[1], reverse=True)

# --- 4. API SEARCH (Replacing Scraper) ---
def search_arxiv(keyword="Machine Learning", limit=5):
    """Fetches real research papers using the official arXiv API."""
    client = arxiv.Client()
    search = arxiv.Search(
        query=keyword,
        max_results=limit,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    pubs = []
    print(f"Searching arXiv for: {keyword}...")
    
    for result in client.results(search):
        pubs.append({
            'title': result.title,
            'pdf': result.pdf_url,
            'year': result.published.year,
            'summary': result.summary
        })
    return pubs

# --- 5. EXECUTION ---
if __name__ == "__main__":
    # Step 1: Gather papers via API
    keyword_to_search = "Artificial Intelligence"
    raw_data = search_arxiv(keyword_to_search, limit=5)
    print(f"Found {len(raw_data)} papers via arXiv API.")

    # Step 2: Process papers
    processed_pubs = []
    
    print(f"Step 2: Downloading & Analyzing papers...")
    for i, paper in enumerate(raw_data):
        print(f"[{i+1}/{len(raw_data)}] Processing: {paper['title'][:50]}...")
        full_text = convertPDF(paper['pdf'])
        if full_text:
            paper['pdf_text'] = stringToWordDictionary(full_text)
            processed_pubs.append(paper)

    # Step 3: Save results
    savePubs('pubs_data.pkl', processed_pubs)

    # Step 4: Analyze
    db = loadPubs('pubs_data.pkl')
    if db:
        print(f"\nSimilarity analysis for: {db[0]['title']}")
        sims = calculate_similarity(db, db[0])
        for title, score in sims[:3]:
            print(f" - {score:.2f} match with: {title}")