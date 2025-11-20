import unittest
from unittest.mock import MagicMock, patch
from shared import matching_engine

class TestMatchingEngine(unittest.TestCase):

    @patch('shared.matching_engine.table_service')
    @patch('shared.matching_engine.AOCClient')
    def test_duplicate_invoice(self, mock_aoc_client, mock_table_service):
        # Setup
        mock_table_service.check_duplicate_invoice.return_value = True
        extracted_data = {"vendor_tax_id": "123", "invoice_id": "INV-001", "amount": 100}

        # Execute
        result = matching_engine.find_match(extracted_data)

        # Verify
        self.assertEqual(result['status'], 'RED')
        self.assertEqual(result['reason'], 'Duplicate invoice detected')

    @patch('shared.matching_engine.table_service')
    @patch('shared.matching_engine.AOCClient')
    def test_hard_match_success(self, mock_aoc_client_cls, mock_table_service):
        # Setup
        mock_table_service.check_duplicate_invoice.return_value = False
        
        mock_aoc_instance = mock_aoc_client_cls.return_value
        mock_aoc_instance.get_open_items.return_value = [
            {"id": "NAV-001", "tax_id": "123", "amount": 100, "invoice_id": "INV-001"}
        ]

        extracted_data = {"vendor_tax_id": "123", "invoice_id": "INV-001", "amount": 100}

        # Execute
        result = matching_engine.find_match(extracted_data)

        # Verify
        self.assertEqual(result['status'], 'GREEN')
        self.assertEqual(result['match_id'], 'NAV-001')
        self.assertEqual(result['confidence'], 100)

    @patch('shared.matching_engine.table_service')
    @patch('shared.matching_engine.AOCClient')
    def test_soft_match_amount_tolerance(self, mock_aoc_client_cls, mock_table_service):
        # Setup
        mock_table_service.check_duplicate_invoice.return_value = False
        
        mock_aoc_instance = mock_aoc_client_cls.return_value
        mock_aoc_instance.get_open_items.return_value = [
            {"id": "NAV-002", "tax_id": "123", "amount": 105, "invoice_id": "INV-002"}
        ]

        extracted_data = {"vendor_tax_id": "123", "invoice_id": "INV-002", "amount": 100} # 5 HUF difference

        # Execute
        result = matching_engine.find_match(extracted_data)

        # Verify
        self.assertEqual(result['status'], 'YELLOW')
        self.assertEqual(result['match_id'], 'NAV-002')
        self.assertEqual(result['confidence'], 90)
        self.assertIn("Amount mismatch", result['reason'])

    @patch('shared.matching_engine.table_service')
    @patch('shared.matching_engine.AOCClient')
    def test_soft_match_fuzzy_invoice_id(self, mock_aoc_client_cls, mock_table_service):
        # Setup
        mock_table_service.check_duplicate_invoice.return_value = False
        
        mock_aoc_instance = mock_aoc_client_cls.return_value
        mock_aoc_instance.get_open_items.return_value = [
            {"id": "NAV-003", "tax_id": "123", "amount": 500, "invoice_id": "INV-2023/001"}
        ]

        # Amount matches exactly, but we want to test fuzzy ID match logic.
        # However, current Hard Match logic only checks TaxID + Amount.
        # So if Amount matches, it returns GREEN.
        # To test the fuzzy logic part, we need to make the Hard Match fail.
        # Let's make the amount slightly different (but > 5 difference to fail the first soft match check? 
        # No, the first soft match check is "Amount mismatch within tolerance".
        # If we want to reach the "Fuzzy match on Invoice Number" block, we need:
        # 1. Hard Match to fail (TaxID mismatch OR Amount mismatch)
        # 2. Soft Match loop:
        #    - TaxID must match.
        #    - Amount mismatch > 5 (otherwise it returns "Amount mismatch within tolerance")
        #    - Fuzzy ID match >= 80
        
        # So let's set amount to 600 (diff > 5).
        extracted_data = {"vendor_tax_id": "123", "invoice_id": "INV-2023-001", "amount": 600} 

        # Execute
        result = matching_engine.find_match(extracted_data)

        # Verify
        self.assertEqual(result['status'], 'YELLOW')
        self.assertEqual(result['match_id'], 'NAV-003')
        self.assertTrue(result['confidence'] >= 80)
        self.assertIn("Fuzzy match", result['reason'])

    @patch('shared.matching_engine.table_service')
    @patch('shared.matching_engine.AOCClient')
    def test_no_match(self, mock_aoc_client_cls, mock_table_service):
        # Setup
        mock_table_service.check_duplicate_invoice.return_value = False
        
        mock_aoc_instance = mock_aoc_client_cls.return_value
        mock_aoc_instance.get_open_items.return_value = [
            {"id": "NAV-004", "tax_id": "999", "amount": 1000, "invoice_id": "INV-999"}
        ]

        extracted_data = {"vendor_tax_id": "123", "invoice_id": "INV-001", "amount": 100}

        # Execute
        result = matching_engine.find_match(extracted_data)

        # Verify
        self.assertEqual(result['status'], 'RED')
        self.assertEqual(result['reason'], 'No matching open item found')

if __name__ == '__main__':
    unittest.main()
