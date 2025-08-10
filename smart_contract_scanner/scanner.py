import os
import json
import joblib
import numpy as np
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity

class Scanner:
    def __init__(self, kb_path='smart_contract_scanner/knowledge_base', similarity_threshold=0.6):
        self.kb_path = kb_path
        self.similarity_threshold = similarity_threshold
        self.vectorizer = None
        self.tfidf_matrix = None
        self.vulnerability_mapping = None
        self._load_model()

    def _load_model(self):
        """Loads the pre-built TF-IDF model and vulnerability data."""
        try:
            vectorizer_path = os.path.join(self.kb_path, 'tfidf_vectorizer.joblib')
            matrix_path = os.path.join(self.kb_path, 'tfidf_matrix.npz')
            mapping_path = os.path.join(self.kb_path, 'vulnerability_mapping.json')

            self.vectorizer = joblib.load(vectorizer_path)
            self.tfidf_matrix = load_npz(matrix_path)
            with open(mapping_path, 'r') as f:
                self.vulnerability_mapping = json.load(f)

            print("TF-IDF model and knowledge base loaded successfully.")
        except FileNotFoundError as e:
            print(f"Error loading model: {e}. Please ensure the knowledge base is built.")
            self.vectorizer = None # Ensure scanner is in a non-working state

    def scan_contract(self, contract_path):
        """
        Scans a smart contract file for vulnerabilities using TF-IDF similarity.
        """
        if not self.vectorizer:
            return [{"error": "Scanner is not initialized. Please build the knowledge base first."}]

        try:
            with open(contract_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            return [{"error": f"File not found: {contract_path}"}]
        except Exception as e:
            return [{"error": f"Error reading file: {e}"}]

        if not lines:
            return []

        findings = []
        # Transform the entire contract's lines into TF-IDF vectors
        contract_vectors = self.vectorizer.transform(lines)

        # Calculate cosine similarity between contract lines and the vulnerability KB
        similarity_matrix = cosine_similarity(contract_vectors, self.tfidf_matrix)

        # Find matches above the threshold
        for i, line in enumerate(lines):
            # Find the index of the most similar vulnerability for this line
            best_match_idx = np.argmax(similarity_matrix[i])
            similarity_score = similarity_matrix[i][best_match_idx]

            if similarity_score >= self.similarity_threshold:
                vulnerability_info = self.vulnerability_mapping[best_match_idx]
                findings.append({
                    'line_number': i + 1, # Assuming lines are 1-indexed for reporting
                    'line_code': line,
                    'similarity_score': similarity_score,
                    'vulnerability': vulnerability_info
                })

        return self._deduplicate_findings(findings)

    def _deduplicate_findings(self, findings):
        """
        Deduplicates findings to report only the best match for each line.
        """
        line_findings = {}
        for finding in findings:
            line_num = finding['line_number']
            if line_num not in line_findings or finding['similarity_score'] > line_findings[line_num]['similarity_score']:
                line_findings[line_num] = finding
        return list(line_findings.values())


    def format_report(self, contract_path, findings):
        """Formats the scan results into a human-readable report."""
        report = f"Scan Report for: {contract_path}\n"
        report += "=" * 50 + "\n"

        if not findings:
            report += "No potential vulnerabilities found.\n"
            return report

        if "error" in findings[0]:
            report += f"Error: {findings[0]['error']}\n"
            return report

        report += f"Found {len(findings)} potential vulnerabilit(ies) with similarity >= {self.similarity_threshold}:\n\n"

        for finding in sorted(findings, key=lambda x: x['line_number']):
            vuln_info = finding['vulnerability']
            report += f"--- Vulnerability: {vuln_info['category'].replace('_', ' ').title()} ---\n"
            report += f"  Line {finding['line_number']}: {finding['line_code']}\n"
            report += f"  Confidence (Similarity Score): {finding['similarity_score']:.2f}\n"
            report += "  Most Similar Known Vulnerability:\n"
            report += f"    Category: {vuln_info['category']}\n"
            report += f"    Source File: {vuln_info['file']}\n"
            report += "    Code Snippet:\n"
            report += "      ```solidity\n"
            report += f"      {vuln_info['code']}\n"
            report += "      ```\n\n"

        return report
