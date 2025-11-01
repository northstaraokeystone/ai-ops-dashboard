import pandas as pd


def analyze_gpu_efficiency(experiments: list[dict]) -> dict:
    df = pd.DataFrame(experiments)
    if df.empty or "batch_size" not in df.columns or "gpu_time_ms" not in df.columns:
        return {
            "potential_savings_pct": 0.0,
            "recommendations": ["Insufficient data for analysis."],
            "total_experiments": 0,
            "avg_gpu_time": 0,
            "batch_size_impact": {},
            "epochs_impact": {},
            "model_type_impact": {},
        }

    batch_analysis = df.groupby("batch_size")["gpu_time_ms"].mean().to_dict()
    epochs_analysis = df.groupby("epochs")["gpu_time_ms"].mean().to_dict()
    model_analysis = df.groupby("model_type")["gpu_time_ms"].mean().to_dict()

    optimal_batch = min(batch_analysis, key=batch_analysis.get)
    savings_pct = 0.0
    if batch_analysis:
        worst_batch_time = max(batch_analysis.values())
        best_batch_time = min(batch_analysis.values())
        if worst_batch_time > 0:
            savings_pct = ((worst_batch_time - best_batch_time) / worst_batch_time) * 100

    return {
        "total_experiments": len(df),
        "avg_gpu_time": float(df["gpu_time_ms"].mean()),
        "batch_size_impact": {int(k): float(v) for k, v in batch_analysis.items()},
        "epochs_impact": {int(k): float(v) for k, v in epochs_analysis.items()},
        "model_type_impact": model_analysis,
        "potential_savings_pct": savings_pct,
        "recommendations": [
            f"Optimal batch_size found: {optimal_batch}",
            f"Potential {savings_pct:.0f}% savings detected",
        ],
    }
