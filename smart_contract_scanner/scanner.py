import os
import json
import re

class Scanner:
    def __init__(self, kb_path='smart_contract_scanner/knowledge_base'):
        self.kb_path = kb_path
        self.knowledge_base = self._load_knowledge_base()
        self.vulnerability_patterns = self._compile_patterns()

    def _load_knowledge_base(self):
        """Loads all vulnerability data from the knowledge base directory."""
        kb = {}
        if not os.path.exists(self.kb_path):
            print(f"Knowledge base path not found: {self.kb_path}")
            return kb

        for file_name in os.listdir(self.kb_path):
            if file_name.endswith('.json'):
                category = file_name.replace('.json', '')
                file_path = os.path.join(self.kb_path, file_name)
                with open(file_path, 'r') as f:
                    kb[category] = json.load(f)
        return kb

    def _compile_patterns(self):
        """
        Compiles regex patterns for each vulnerability category.
        This is a simplified retrieval mechanism.
        """
        patterns = {
            'reentrancy': re.compile(r'\.call\.value'),
            'arithmetic': re.compile(r'\+\+|--|\+=|-=|\*=|/='), # Simple heuristic
            'time_manipulation': re.compile(r'block\.timestamp|now'),
            'access_control': re.compile(r'tx\.origin'),
            'unchecked_low_level_calls': re.compile(r'\.send|\.call'), # Matches .send and .call
            'bad_randomness': re.compile(r'block\.blockhash|block\.coinbase|block\.difficulty|block\.gaslimit|block\.number|block\.timestamp|now'),
            # More specific patterns can be added here
        }
        return patterns

    def scan_contract(self, contract_path):
        """
        Scans a single smart contract file for vulnerabilities.
        """
        findings = []
        try:
            with open(contract_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return [{"error": f"File not found: {contract_path}"}]
        except Exception as e:
            return [{"error": f"Error reading file: {e}"}]

        for i, line in enumerate(lines):
            line_num = i + 1
            for category, pattern in self.vulnerability_patterns.items():
                if pattern.search(line):
                    findings.append({
                        'line': line_num,
                        'code': line.strip(),
                        'category': category,
                        'description': self.knowledge_base.get(category, {}).get('description', 'N/A'),
                        'confidence': 'Low', # All findings are low confidence with this simple method
                        'evidence': self.knowledge_base.get(category, {}).get('snippets', [])[:3] # Show top 3 snippets
                    })

        return self._deduplicate_findings(findings)

    def _deduplicate_findings(self, findings):
        """Deduplicates findings based on line number and category."""
        unique_findings = {}
        for finding in findings:
            key = (finding['line'], finding['category'])
            if key not in unique_findings:
                unique_findings[key] = finding
        return list(unique_findings.values())

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

        report += f"Found {len(findings)} potential vulnerabilit(ies):\n\n"

        for finding in sorted(findings, key=lambda x: x['line']):
            report += f"--- Vulnerability: {finding['category'].replace('_', ' ').title()} ---\n"
            report += f"  Line {finding['line']}: {finding['code']}\n"
            report += f"  Description: {finding['description']}\n"
            report += f"  Confidence: {finding['confidence']}\n"

            if finding['evidence']:
                report += "  Similar vulnerable patterns from knowledge base:\n"
                for i, snippet in enumerate(finding['evidence']):
                    report += f"    Example {i+1} (from {snippet['file']}):\n"
                    report += "      ```solidity\n"
                    report += f"      {snippet['code'].strip()}\n"
                    report += "      ```\n"
            report += "\n"

        return report

if __name__ == '__main__':
    # Example Usage:
    # Create a dummy contract to test
    dummy_contract_path = 'dummy_contract.sol'
    with open(dummy_contract_path, 'w') as f:
        f.write("""pragma solidity ^0.4.24;

contract MyContract {
    function withdraw(uint amount) public {
        msg.sender.call.value(amount)();
    }

    function update() public {
        if (tx.origin == msg.sender) {
            // ...
        }
    }

    function guess(uint _guess) public {
        uint answer = uint(block.timestamp);
        if (_guess == answer) {
            // winner
        }
    }
}
""")

    scanner = Scanner()
    findings = scanner.scan_contract(dummy_contract_path)
    report = scanner.format_report(dummy_contract_path, findings)
    print(report)

    # Clean up the dummy file
    os.remove(dummy_contract_path)
