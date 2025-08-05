# Smart Contract Vulnerability Scanner

This project is a prototype of a smart contract vulnerability scanner based on the principles of Retrieval-Augmented Generation (RAG). It scans Solidity source code for patterns indicative of common vulnerabilities and provides contextual examples from a knowledge base of known exploits.

This tool was developed based on the roadmap outlined in the "Roadmap for a Smart Contract Vulnerability Detection Model" document. It implements a simplified version of the RAG pipeline.

## How It Works

The scanner operates in two main stages:

1.  **Knowledge Base:** The tool uses a pre-built knowledge base located in the `knowledge_base` directory. This knowledge base was created by processing the [SB Curated dataset](https://github.com/smartbugs/smartbugs-curated), which contains a collection of vulnerable smart contracts. Each JSON file in the knowledge base corresponds to a vulnerability category and contains a description and vulnerable code snippets.

2.  **Scanning (Retrieval):** When you scan a contract, the tool uses a set of regular expressions to find lines of code that match patterns of known vulnerabilities. This is a simplified form of "retrieval."

3.  **Reporting (Generation):** For each potential vulnerability found, the tool generates a report that includes the location of the issue, a description of the vulnerability, and relevant examples from the knowledge base to provide context.

## Features

-   **Pattern-Based Detection:** Uses regular expressions to find potential vulnerabilities.
-   **RAG-based Context:** Provides snippets from real-world vulnerabilities to help understand the findings.
-   **Command-Line Interface:** Easy-to-use CLI for scanning `.sol` files.

## Detectable Vulnerabilities

The scanner can currently detect patterns related to the following vulnerability categories:
- Access Control (e.g., `tx.origin` usage)
- Arithmetic (Integer Overflow/Underflow)
- Bad Randomness
- Denial of Service
- Front Running
- Reentrancy
- Time Manipulation
- Unchecked Low-Level Calls

## Installation

To set up the scanner, clone the repository and install the dependencies.

```bash
# No external dependencies are required for the scanner itself,
# but if you want to run the tests, you might need to install packages.
pip install -r requirements.txt
```

## Usage

To scan a smart contract, run the following command from the root of the project:

```bash
python3 -m smart_contract_scanner <path_to_your_solidity_file.sol>
```

### Example

```bash
python3 -m smart_contract_scanner path/to/MyContract.sol
```

## Disclaimer

This tool is a proof-of-concept and should **not** be used as a replacement for a comprehensive security audit. The detection mechanism is based on simple regular expressions and may produce false positives or miss more complex vulnerabilities. Always have your smart contracts professionally audited before deploying them to production.
