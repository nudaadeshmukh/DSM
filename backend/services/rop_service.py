def calculate_rop(daily_demand, lead_time):
    """
    ROP = d * L
    """
    try:
        rop = daily_demand * lead_time
        return round(rop, 2)
    except Exception as e:
        print("ROP Error:", e)
        return None
