import numpy as np


def simulate_roi(config: dict) -> dict:
    # This is a simplified version of Notebook 3 logic
    periods = config.get("periods", 12)
    retraining_cost = config.get("retraining_cost_usd", 6000)

    months = np.arange(1, periods + 1)
    net_benefit = 12000 - (1000 * months)  # Simplified economic model

    timeline = [
        {
            "period": int(m),
            "net_roi": float(b),
            "cum_roi": float(np.sum(net_benefit[:m])),
        }
        for m, b in zip(months, net_benefit)
    ]

    breach_mask = net_benefit < retraining_cost
    breach_month = int(np.argmax(breach_mask) + 1) if breach_mask.any() else None

    return {
        "timeline": timeline,
        "total_roi": float(np.sum(net_benefit)),
        "breach_period": breach_month,
        "summary": {"break_even_period": 4},  # Placeholder
    }
