# backtest_utils.py
import config

def simulate_fill(price, shares, side="buy", slippage_pct=0.001, slippage_abs=0.005, commission=0.01):
    """
    Simulate slippage, commission, and market impact for a trade.

    Parameters:
    - price: float — the base market price
    - shares: int — number of shares to trade
    - side: str — "buy" or "sell"
    - slippage_pct: float — percent-based slippage (e.g. 0.001 = 0.1%)
    - slippage_abs: float — fixed per-share slippage (e.g. $0.005 per share)
    - commission: float — flat commission per trade

    Returns:
    - fill_price: float — adjusted trade price
    - total_cost: float — total cash required or received (with commission)
    """

    # Simulate base slippage
    slippage = price * slippage_pct + slippage_abs

    # Market impact = price impact from order size (linear model)
    # Adjust the multiplier to tune impact severity
    impact_factor = 0.00002  # e.g. 0.002 per 100 shares
    market_impact = price * impact_factor * abs(shares)

    # Adjust fill price worse depending on direction
    if side == "buy":
        fill_price = price + slippage + market_impact
    elif side == "sell":
        fill_price = price - slippage - market_impact
    else:
        raise ValueError(f"Invalid side: {side}")

    # Total cash cost (or proceeds), including commission
    total_cost = fill_price * shares + commission if side == "buy" else fill_price * shares - commission
    return fill_price, total_cost

    """
    Simulate a trade fill incorporating slippage and commission.
    """
    base_price = intended_price

    # Determine slippage amount
    if config.SLIPPAGE_PCT is not None:
        slip_amount = base_price * config.SLIPPAGE_PCT
    else:
        slip_amount = config.SLIPPAGE_PER_SHARE

    # Apply slippage against the trader
    if qty > 0:
        fill_price = base_price + slip_amount  # buys at a worse price
    else:
        fill_price = base_price - slip_amount  # sells at a lower price

    # Commission per trade
    commission = config.COMMISSION_PER_TRADE

    # Compute trade value
    trade_value = fill_price * abs(qty)

    # Net cash effect: outflow for buys, inflow for sells
    if qty > 0:
        net_cash_effect = trade_value + commission
    else:
        net_cash_effect = trade_value - commission

    return fill_price, net_cash_effect
