import json
import os
from collections import defaultdict

# Define paths
#The /tmp folder is a standard directory
#in the operating system used for temporary storage.
#The main scanner application doesn't use the
#/tmp directory at all; it relies only on the permanent knowledge_base that was created.
VULNERABILITIES_JSON_PATH = '/tmp/sb-curated/vulnerabilities.json'
CONTRACTS_DIR = '/tmp/sb-curated/'
KNOWLEDGE_BASE_DIR = 'smart_contract_scanner/knowledge_base'

def get_swc_description(swc_id):
    """
    Returns a brief description for a given SWC ID.
    In a real implementation, this could fetch from a live source.
    """
    # Source: https://swcregistry.io/
    swc_map = {
        "SWC-101": "Integer Overflow and Underflow",
        "SWC-102": "Outdated Compiler Version",
        "SWC-103": "Floating Pragmas",
        "SWC-104": "Unchecked Call Return Value",
        "SWC-105": "Unprotected Ether Withdrawal",
        "SWC-106": "Unprotected SELFDESTRUCT Instruction",
        "SWC-107": "Reentrancy",
        "SWC-112": "Delegatecall to Untrusted Callee",
        "SWC-118": "Incorrect Constructor Name",
        "SWC-124": "Write to Arbitrary Storage Location",
        # Add more as needed
    }
    return swc_map.get(swc_id, "No description available.")

def extract_vulnerable_lines(contract_path, line_numbers):
    """Extracts specific lines of code from a contract file."""
    try:
        with open(contract_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        vulnerable_code = ""
        for line_num in sorted(line_numbers):
            if 1 <= line_num <= len(lines):
                vulnerable_code += lines[line_num - 1]
        return vulnerable_code
    except FileNotFoundError:
        return f"// File not found: {contract_path}"
    except Exception as e:
        return f"// Error reading file: {e}"

def main():
    """
    Parses the vulnerabilities.json file and the dataset to build
    a structured knowledge base.
    """
    # Ensure the knowledge base directory exists
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        os.makedirs(KNOWLEDGE_BASE_DIR)

    # Read the main JSON file
    with open(VULNERABILITIES_JSON_PATH, 'r') as f:
        data = json.load(f)

    knowledge_base = defaultdict(lambda: {"description": "", "snippets": []})

    # Process each contract in the JSON file
    for contract_info in data:
        contract_path = os.path.join(CONTRACTS_DIR, contract_info['path'])

        for vuln in contract_info['vulnerabilities']:
            category = vuln['category']
            line_numbers = vuln['lines']

            # Extract the code snippet
            snippet = extract_vulnerable_lines(contract_path, line_numbers)

            # Add to our knowledge base
            knowledge_base[category]["snippets"].append({
                "file": contract_info['name'],
                "pragma": contract_info.get('pragma', 'N/A'),
                "code": snippet
            })

    # Add descriptions (this part can be improved with more sophisticated sources)
    # For now, we manually add some based on common knowledge
    descriptions = {
        "access_control": "Vulnerabilities related to improper management of permissions and authorizations.",
        "arithmetic": "Vulnerabilities related to integer overflows and underflows.",
        "bad_randomness": "Vulnerabilities arising from predictable or manipulable sources of randomness.",
        "denial_of_service": "Vulnerabilities that can lead to a contract being rendered inoperable.",
        "front_running": "Vulnerabilities related to the order of transactions in a block.",
        "reentrancy": "A vulnerability where a contract can be tricked into calling itself multiple times, often to drain funds.",
        "short_addresses": "A vulnerability where the EVM pads short addresses with zeros, which can be exploited in some cases.",
        "time_manipulation": "Vulnerabilities where a contract's logic depends on the block timestamp, which can be manipulated by miners.",
        "unchecked_low_level_calls": "Vulnerabilities from using low-level calls like call(), delegatecall(), or send() without checking the return value."
    }
    for category, desc in descriptions.items():
        if category in knowledge_base:
            knowledge_base[category]["description"] = desc

    # Write the structured knowledge base to JSON files
    for category, content in knowledge_base.items():
        output_path = os.path.join(KNOWLEDGE_BASE_DIR, f"{category}.json")
        with open(output_path, 'w') as f:
            json.dump(content, f, indent=4)
        print(f"Created knowledge base file: {output_path}")

if __name__ == '__main__':
    main()
