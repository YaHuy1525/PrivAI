import argparse
from smart_contract_scanner.scanner import Scanner

def main():
    """
    Main function to run the smart contract vulnerability scanner from the command line.
    """
    parser = argparse.ArgumentParser(
        description="A RAG-based vulnerability scanner for Solidity smart contracts."
    )
    parser.add_argument(
        "contract_path",
        help="The path to the Solidity (.sol) file to scan."
    )
    args = parser.parse_args()

    # Initialize the scanner
    # The scanner will automatically load the knowledge base from the default path
    scanner = Scanner()

    # Scan the contract and get the findings
    findings = scanner.scan_contract(args.contract_path)

    # Format and print the report
    report = scanner.format_report(args.contract_path, findings)
    print(report)

if __name__ == "__main__":
    main()
