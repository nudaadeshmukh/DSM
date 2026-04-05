def calculate_total_cost(demand, eoq, ordering_cost, holding_cost, transport_cost):
    """
    Total Cost = Ordering + Holding + Transportation
    """

    try:
        ordering = (demand / eoq) * ordering_cost
        holding = (eoq / 2) * holding_cost

        total = ordering + holding + transport_cost
        return round(total, 2)

    except Exception as e:
        print("Cost Error:", e)
        return None
