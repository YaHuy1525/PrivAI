import unittest
import os
import json
from smart_contract_scanner.scanner import Scanner

class TestScanner(unittest.TestCase):

    def setUp(self):
        """Set up a dummy knowledge base and a scanner instance."""
        self.kb_dir = 'smart_contract_scanner/tests/dummy_kb'
        os.makedirs(self.kb_dir, exist_ok=True)

        # Create a dummy KB file for reentrancy
        reentrancy_data = {
            "description": "Test reentrancy description.",
            "snippets": [{"file": "example.sol", "code": "call.value()"}]
        }
        with open(os.path.join(self.kb_dir, 'reentrancy.json'), 'w') as f:
            json.dump(reentrancy_data, f)

        # Create a dummy KB file for time manipulation
        time_data = {
            "description": "Test time manipulation description.",
            "snippets": [{"file": "example.sol", "code": "block.timestamp"}]
        }
        with open(os.path.join(self.kb_dir, 'time_manipulation.json'), 'w') as f:
            json.dump(time_data, f)

        # Create dummy KB for other expected categories
        unchecked_calls_data = {"description": "Test unchecked calls."}
        with open(os.path.join(self.kb_dir, 'unchecked_low_level_calls.json'), 'w') as f:
            json.dump(unchecked_calls_data, f)

        bad_randomness_data = {"description": "Test bad randomness."}
        with open(os.path.join(self.kb_dir, 'bad_randomness.json'), 'w') as f:
            json.dump(bad_randomness_data, f)

        self.scanner = Scanner(kb_path=self.kb_dir)

    def tearDown(self):
        """Clean up dummy files and directories."""
        for root, dirs, files in os.walk(self.kb_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.kb_dir)
        if os.path.exists('test_contract.sol'):
            os.remove('test_contract.sol')

    def test_knowledge_base_loading(self):
        """Test that the knowledge base is loaded correctly."""
        self.assertIn('reentrancy', self.scanner.knowledge_base)
        self.assertIn('time_manipulation', self.scanner.knowledge_base)
        self.assertEqual(self.scanner.knowledge_base['reentrancy']['description'], "Test reentrancy description.")

    def test_scan_vulnerable_contract(self):
        """Test scanning a contract with known vulnerabilities."""
        contract_content = """
        contract Vulnerable {
            function withdraw() public {
                msg.sender.call.value(1 ether)();
            }
            function getTime() public view returns (uint) {
                return block.timestamp;
            }
        }
        """
        with open('test_contract.sol', 'w') as f:
            f.write(contract_content)

        findings = self.scanner.scan_contract('test_contract.sol')

        categories_found = {f['category'] for f in findings}
        # The patterns are simple, so they overlap. This is expected.
        # .call.value() is both reentrancy and unchecked_low_level_calls
        # block.timestamp is both time_manipulation and bad_randomness
        self.assertIn('reentrancy', categories_found)
        self.assertIn('unchecked_low_level_calls', categories_found)
        self.assertIn('time_manipulation', categories_found)
        self.assertIn('bad_randomness', categories_found)
        self.assertEqual(len(findings), 4)

    def test_scan_safe_contract(self):
        """Test scanning a contract with no obvious vulnerabilities."""
        contract_content = """
        contract Safe {
            uint public myNumber;
            function setNumber(uint n) public {
                myNumber = n;
            }
        }
        """
        with open('test_contract.sol', 'w') as f:
            f.write(contract_content)

        findings = self.scanner.scan_contract('test_contract.sol')
        self.assertEqual(len(findings), 0)

if __name__ == '__main__':
    unittest.main()
