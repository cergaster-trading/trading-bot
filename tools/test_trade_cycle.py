import unittest
from unittest.mock import patch, MagicMock
from trade_cycle import run_trade_cycle

class TestTradeCycle(unittest.TestCase):

    @patch('trade_cycle.get_portfolio_status')
    @patch('trade_cycle.is_market_open')
    @patch('trade_cycle.load_symbol_data')
    @patch('trade_cycle.get_ensemble_score')
    @patch('trade_cycle.submit_order')
    def test_trade_cycle_runs_without_crashing(self, mock_submit_order, mock_get_score, mock_load_data, mock_market_open, mock_get_status):
        # Setup mocks
        mock_get_status.return_value = {
            "equity": 100000,
            "cash": 5000,
            "positions": [
                {"symbol": "TSLA", "qty": 5, "market_value": 6000},
                {"symbol": "NVDA", "qty": 10, "market_value": 8000}
            ]
        }
        mock_market_open.return_value = True

        import pandas as pd
        mock_df = pd.DataFrame({"close": [100, 102, 105, 103, 107]})
        mock_load_data.return_value = mock_df
        mock_get_score.return_value = 0.6  # Triggers buy logic

        # Run
        run_trade_cycle(api=MagicMock(), ensemble_params={})

        # Assert
        self.assertTrue(mock_submit_order.called)
        self.assertEqual(mock_submit_order.call_args[1]['side'], 'buy')

    @patch('trade_cycle.get_portfolio_status')
    @patch('trade_cycle.is_market_open')
    def test_skips_when_market_closed(self, mock_market_open, mock_get_status):
        mock_get_status.return_value = {"equity": 100000, "cash": 5000, "positions": []}
        mock_market_open.return_value = False

        # Should exit early without crashing
        run_trade_cycle(api=MagicMock(), ensemble_params={})

if __name__ == '__main__':
    unittest.main()
