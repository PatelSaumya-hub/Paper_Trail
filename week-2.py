#from sentence_transformers import Senten#

from sentence_transformers import SentenceTransformer, util

# Week 2: Semantic Similarity Engine
def calculate_paper_similarity(main_abstract, list_of_abstracts):
    """
    Uses a Transformer model to compare the 'DNA' of multiple papers.
    """
    # Load a pre-trained model optimized for scientific text
    model = SentenceTransformer('all-MiniLM-L6-v2') 

    # Encode the abstracts into 'Vectors' (Mathematical DNA)
    main_embedding = model.encode(main_abstract)
    comparison_embeddings = model.encode(list_of_abstracts)

    # Calculate Cosine Similarity
    similarities = util.cos_sim(main_embedding, comparison_embeddings)
    
    print("--- WEEK 2: SIMILARITY RESULTS ---")
    for i, score in enumerate(similarities[0]):
        print(f"Paper {i+1} Similarity Score: {score:.4f}")

# Example Test
if __name__ == "__main__":
    main_text = "AI-powered discovery for research papers using semantic analysis."
    others = [
        "Automated literature review using machine learning models.",
        "A study on global warming and ocean temperatures.",
        "Using NLP to find connections in scholarly data."
    ]
    calculate_paper_similarity(main_text, others)
