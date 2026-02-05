
import unittest
from enhanced_analyzer import RegexSieve

class TestRegexSieve(unittest.TestCase):
    def setUp(self):
        self.sieve = RegexSieve()
        self.sample_text = """
### 3.28.6 County Expenditure Review
Data: The County spent a total of Kshs.13.52 billion on development and recurrent programs during the reporting period.

### 3.28.2 Revenue Performance
Data: The total revenue received to fund activities was Kshs.17.22 billion, consisting of equitable share, additional allocations, OSR, and cash balances.
Own source revenue collected was Kshs.1.5 billion.

### 3.28.7 Settlement of Pending Bills
Data: As of 30 June 2024, the County reported total pending bills of Kshs.4.47 billion. Note: The report also provides an updated figure of Kshs.3.80 billion as of 30 June 2025 in the same section.

### 3.28.6 County Expenditure Review
Data: The expenditure on development programs specifically amounted to Kshs.3.34 billion.
"""

    def test_extraction(self):
        metrics = self.sieve.extract_metrics(self.sample_text)
        print("\nExtracted Metrics:", metrics)
        
        # 13.52 billion = 13,520,000,000
        self.assertEqual(metrics["total_expenditure"], 13_520_000_000)
        
        # 17.22 billion = 17,220,000,000
        self.assertEqual(metrics["total_revenue"], 17_220_000_000)
        
        # 4.47 billion = 4,470,000,000
        self.assertEqual(metrics["pending_bills"], 4_470_000_000)
        
        # 3.34 billion = 3,340,000,000
        self.assertEqual(metrics["development_expenditure"], 3_340_000_000)

if __name__ == "__main__":
    unittest.main()
