import unittest
import os
import json
import joblib
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from smart_contract_scanner.scanner import Scanner

class TestTfidfScanner(unittest.TestCase):

    def setUp(self):
        """Set up a dummy TF-IDF model and knowledge base."""
        self.kb_dir = 'smart_contract_scanner/tests/dummy_kb_tfidf'
        os.makedirs(self.kb_dir, exist_ok=True)

        # 1. Create a dummy corpus and mapping
        self.dummy_corpus = [
            "require(msg.sender.call.value(amount)())", # Reentrancy
            "balance += amount", # Arithmetic
            "if (block.timestamp > 123)" # Time manipulation
        ]
        self.dummy_mapping = [
            {"category": "reentrancy", "file": "a.sol", "code": self.dummy_corpus[0]},
            {"category": "arithmetic", "file": "b.sol", "code": self.dummy_corpus[1]},
            {"category": "time_manipulation", "file": "c.sol", "code": self.dummy_corpus[2]}
        ]

        # 2. Create and fit a dummy vectorizer
        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
        self.tfidf_matrix = self.vectorizer.fit_transform(self.dummy_corpus)

        # 3. Save the dummy model artifacts
        joblib.dump(self.vectorizer, os.path.join(self.kb_dir, 'tfidf_vectorizer.joblib'))
        from scipy.sparse import save_npz
        save_npz(os.path.join(self.kb_dir, 'tfidf_matrix.npz'), self.tfidf_matrix)
        with open(os.path.join(self.kb_dir, 'vulnerability_mapping.json'), 'w') as f:
            json.dump(self.dummy_mapping, f)

        # 4. Instantiate the scanner
        self.scanner = Scanner(kb_path=self.kb_dir, similarity_threshold=0.7)

    def tearDown(self):
        """Clean up dummy files and directories."""
        for root, dirs, files in os.walk(self.kb_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.kb_dir)
        if os.path.exists('test_contract_tfidf.sol'):
            os.remove('test_contract_tfidf.sol')

    def test_model_loading(self):
        """Test that the TF-IDF model and KB are loaded correctly."""
        self.assertIsNotNone(self.scanner.vectorizer)
        self.assertIsNotNone(self.scanner.tfidf_matrix)
        self.assertEqual(len(self.scanner.vulnerability_mapping), 3)

    def test_scan_vulnerable_contract(self):
        """Test scanning a contract with a highly similar vulnerability."""
        # This line is very similar to the first entry in our dummy corpus
        contract_content = "contract A { function withdraw(uint amount) { require(msg.sender.call.value(amount)()); } }"
        with open('test_contract_tfidf.sol', 'w') as f:
            f.write(contract_content)

        findings = self.scanner.scan_contract('test_contract_tfidf.sol')

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['vulnerability']['category'], 'reentrancy')
        self.assertGreater(findings[0]['similarity_score'], self.scanner.similarity_threshold)

    def test_scan_safe_contract(self):
        """Test scanning a contract with no similar vulnerabilities."""
        # This line should have low similarity to our dummy corpus
        contract_content = "contract B { function safeFunc() public { uint x = 1; } }"
        with open('test_contract_tfidf.sol', 'w') as f:
            f.write(contract_content)

        findings = self.scanner.scan_contract('test_contract_tfidf.sol')
        self.assertEqual(len(findings), 0)

if __name__ == '__main__':
    unittest.main()
