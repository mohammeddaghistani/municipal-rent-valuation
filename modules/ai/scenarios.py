def compare_scenarios(base_value: float) -> dict:
    return {
        "base": base_value,
        "scenario_up": base_value * 1.15,
        "scenario_down": base_value * 0.9,
        "note": "تحليل سيناريوهات لغرض الدعم فقط."
    }
