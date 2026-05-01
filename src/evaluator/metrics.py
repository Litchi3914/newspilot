def bool_rate(vals: list[bool]) -> float:
    return round((sum(1 for x in vals if x) / max(len(vals),1))*100, 2)
