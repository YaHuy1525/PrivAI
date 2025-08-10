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
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.6,
        help="The similarity score threshold for reporting vulnerabilities (0.0 to 1.0)."
    )
    args = parser.parse_args()

    # Initialize the scanner with the specified threshold
    scanner = Scanner(similarity_threshold=args.threshold)

    # Scan the contract and get the findings
    findings = scanner.scan_contract(args.contract_path)

    # Format and print the report
    report = scanner.format_report(args.contract_path, findings)
    print(report)

if __name__ == "__main__":
    main()
