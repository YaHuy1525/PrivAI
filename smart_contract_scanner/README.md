# Smart Contract Vulnerability Scanner (AI-Powered)

This project is a prototype of a smart contract vulnerability scanner that uses machine learning to detect potential vulnerabilities. It leverages a TF-IDF (Term Frequency-Inverse Document Frequency) model to find similarities between a user's smart contract and a knowledge base of known vulnerable code snippets.

This tool was developed based on the roadmap outlined in the "Roadmap for a Smart Contract Vulnerability Detection Model" document and represents a lightweight but effective implementation of an AI-driven RAG (Retrieval-Augmented Generation) pipeline.

## How It Works

The scanner operates in two main stages:

1.  **Knowledge Base:** The tool uses a pre-built knowledge base located in the `smart_contract_scanner/knowledge_base` directory. This knowledge base was created by processing the [SB Curated dataset](https://github.com/smartbugs/smartbugs-curated). It consists of:
    *   A **TF-IDF Vectorizer** model that has learned the vocabulary of vulnerable Solidity code.
    *   A **TF-IDF Matrix** containing the vector representations of hundreds of vulnerable code snippets.
    *   A **Mapping File** that links each vector in the matrix back to its original vulnerability metadata (category, source file, etc.).

2.  **Scanning (AI-Powered Retrieval):** When you scan a contract, the tool:
    *   Reads the lines of your Solidity code.
    *   Uses the loaded TF-IDF vectorizer to convert each line into a vector.
    *   Calculates the cosine similarity between your code's vectors and all the vectors in the vulnerability knowledge base.
    *   If the similarity score for a line exceeds a certain threshold, it's flagged as a potential vulnerability.

3.  **Reporting:** For each potential vulnerability, the tool generates a report that includes the line of code, the vulnerability it's similar to, and the confidence score (based on similarity).

## Features

-   **AI-Based Detection:** Uses a TF-IDF model and cosine similarity to find textually similar vulnerabilities.
-   **Contextual Examples:** Provides the exact vulnerable snippet from the knowledge base that matched your code.
-   **Adjustable Threshold:** Allows you to set the similarity threshold for finding matches.
-   **Command-Line Interface:** Easy-to-use CLI for scanning `.sol` files.

## Installation

To set up the scanner, clone the repository and install the dependencies.

```bash
pip install -r smart_contract_scanner/requirements.txt
```

You may also need to build the knowledge base for the first time by running the script:
```bash
python3 smart_contract_scanner/scripts/build_knowledge_base.py
```

## Usage

To scan a smart contract, run the following command from the root of the project:

```bash
python3 -m smart_contract_scanner <path_to_your_solidity_file.sol> [options]
```

### Options
- `--threshold <float>`: Set the similarity score threshold (0.0 to 1.0) for reporting vulnerabilities. The default is `0.6`. A lower value will find more potential matches (including more false positives), while a higher value will only report very close matches.

### Example

```bash
# Scan with the default threshold (0.6)
python3 -m smart_contract_scanner path/to/MyContract.sol

# Scan with a higher, more strict threshold
python3 -m smart_contract_scanner path/to/MyContract.sol --threshold 0.8
```

## Disclaimer

This tool is a proof-of-concept and should **not** be used as a replacement for a comprehensive security audit. The detection mechanism is based on a statistical text model and may produce false positives or miss vulnerabilities that are not textually similar to its knowledge base. Always have your smart contracts professionally audited before deploying them to production.
