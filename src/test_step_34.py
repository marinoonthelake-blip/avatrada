import unittest
from src.services.risk.monitors.exclusion_list import ExclusionListManager

class TestExclusionList(unittest.TestCase):

    def test_restriction_lookup(self):
        print("\nTesting Restricted Symbol Lookup...")
        # Point to the new location in src/
        manager = ExclusionListManager("src/restricted_symbols.json")

        # Test restricted symbols
        self.assertTrue(manager.is_restricted("AAPL"))
        self.assertTrue(manager.is_restricted("msft"))
        print("SUCCESS: Correctly identified restricted symbols.")

    def test_allowed_symbol(self):
        print("\nTesting Allowed Symbol Lookup...")
        manager = ExclusionListManager("src/restricted_symbols.json")

        # Test non-restricted symbol
        self.assertFalse(manager.is_restricted("SPY"))
        self.assertFalse(manager.is_restricted("TSLA"))
        print("SUCCESS: Correctly identified allowed symbols.")

if __name__ == '__main__':
    unittest.main()
