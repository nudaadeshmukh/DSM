import math

def calculate_eoq(demand, ordering_cost, holding_cost):
    """
    EOQ = sqrt((2 * D * S) / H)
    """
    try:
        eoq = math.sqrt((2 * demand * ordering_cost) / holding_cost)
        return round(eoq, 2)
    except Exception as e:
        print("EOQ Error:", e)
        return None
