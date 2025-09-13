from app.utils.logger import logger
def calc_market(supply: float, demand: float, cost: float, price: float):
    try:
        profit = (price - cost) * min(supply, demand)
        supply_status = (
            "excess" if supply > demand else
            "shortage" if supply < demand else
            "balanced"
        )
        logger.info( #Whenever a calculation succeeds, logs the profit, supply/demand status, and all input values.
            "Market calculation successful: profit=%s, status=%s (supply=%s, demand=%s, cost=%s, price=%s)",
            profit, supply_status, supply, demand, cost, price
        )
        return profit, supply_status
    except Exception as e:
        logger.exception("Market calculation failed: %s", e)
        raise
