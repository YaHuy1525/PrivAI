import json
import os
import subprocess
import joblib
from scipy.sparse import save_npz
from sklearn.feature_extraction.text import TfidfVectorizer

# Define paths
REPO_URL = 'https://github.com/smartbugs/smartbugs-curated.git'
REPO_DIR = '/tmp/sb-curated'
VULNERABILITIES_JSON_PATH = os.path.join(REPO_DIR, 'vulnerabilities.json')
KNOWLEDGE_BASE_DIR = 'smart_contract_scanner/knowledge_base'

# Output file paths
VECTORIZER_PATH = os.path.join(KNOWLEDGE_BASE_DIR, 'tfidf_vectorizer.joblib')
MATRIX_PATH = os.path.join(KNOWLEDGE_BASE_DIR, 'tfidf_matrix.npz')
MAPPING_PATH = os.path.join(KNOWLEDGE_BASE_DIR, 'vulnerability_mapping.json')

def clone_repo():
    """Clones the dataset repository if it doesn't exist."""
    if os.path.exists(REPO_DIR):
        print(f"Repository already exists at {REPO_DIR}. Skipping clone.")
        return
    print(f"Cloning repository from {REPO_URL}...")
    subprocess.run(['git', 'clone', REPO_URL, REPO_DIR], check=True)

def extract_vulnerable_lines(contract_path, line_numbers):
    """Extracts specific lines of code from a contract file."""
    try:
        with open(contract_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        vulnerable_code = ""
        for line_num in sorted(line_numbers):
            if 1 <= line_num <= len(lines):
                vulnerable_code += lines[line_num - 1]
        return vulnerable_code.strip()
    except Exception as e:
        print(f"Error reading file {contract_path}: {e}")
        return None

def main():
    """
    Builds a knowledge base by creating TF-IDF vectors from vulnerable
    code snippets.
    """
    # 1. Get the data
    clone_repo()

    # 2. Prepare directories and data structures
    os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)

    with open(VULNERABILITIES_JSON_PATH, 'r') as f:
        vulnerabilities_data = json.load(f)

    corpus = []
    mapping = []

    print("Processing vulnerabilities and extracting code snippets...")
    # 3. Process data and create corpus and mapping
    for contract_info in vulnerabilities_data:
        contract_full_path = os.path.join(REPO_DIR, contract_info['path'])

        for vuln in contract_info['vulnerabilities']:
            snippet = extract_vulnerable_lines(contract_full_path, vuln['lines'])

            if snippet:
                corpus.append(snippet)
                mapping.append({
                    'category': vuln['category'],
                    'file': contract_info['name'],
                    'lines': vuln['lines'],
                    'code': snippet
                })

    if not corpus:
        print("No snippets were extracted. Exiting.")
        return

    print(f"Extracted {len(corpus)} snippets.")
    print("Building TF-IDF model...")

    # 4. Create and train the TF-IDF Vectorizer
    # We use sublinear_tf for logarithmic scaling and analyze char_wb for better
    # matching on code-like text.
    vectorizer = TfidfVectorizer(
        sublinear_tf=True,
        strip_accents='unicode',
        analyzer='char_wb',
        ngram_range=(2, 4),
        max_features=4000
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # 5. Save the artifacts
    print(f"Saving TF-IDF vectorizer to {VECTORIZER_PATH}")
    joblib.dump(vectorizer, VECTORIZER_PATH)

    print(f"Saving TF-IDF matrix to {MATRIX_PATH}")
    save_npz(MATRIX_PATH, tfidf_matrix)

    print(f"Saving vulnerability mapping to {MAPPING_PATH}")
    with open(MAPPING_PATH, 'w') as f:
        json.dump(mapping, f, indent=2)

    print("\nKnowledge base build complete!")
    print(f"Created {VECTORIZER_PATH}, {MATRIX_PATH}, and {MAPPING_PATH}")

if __name__ == '__main__':
    main()
