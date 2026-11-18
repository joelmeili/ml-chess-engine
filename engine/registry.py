from engine.evaluation import material_score, evaluate

ENGINES = {
    "material": {"name": "Material only", "evaluate_fn": material_score},
    "pst": {"name": "Material and piece-square tables", "evaluate_fn": evaluate}
}