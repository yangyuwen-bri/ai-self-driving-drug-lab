from autoquant.core.specs import ObjectiveSpec, ParameterSpec, ScenarioSpec


COATING_LINE_SCENARIO = ScenarioSpec(
    name="coating_line_demo",
    parameters=[
        ParameterSpec("oven_temperature", 140.0, 240.0, "°C", "oven zone temperature"),
        ParameterSpec("line_speed", 5.0, 25.0, "m/min", "production line speed"),
        ParameterSpec("catalyst_ratio", 0.1, 1.5, "%", "catalyst additive ratio"),
        ParameterSpec("dryer_flow", 20.0, 90.0, "%", "dryer flow rate"),
        ParameterSpec("pressure", 1.0, 6.0, "bar", "roller pressure"),
    ],
    objectives=[
        ObjectiveSpec("coating_thickness", mode="match_bell", target=85.0, weight=0.6, unit="μm", tolerance=3.0),
        ObjectiveSpec(
            "adhesion_index",
            mode="maximize",
            weight=0.25,
            unit="score",
            metadata={"lower_bound": 50.0, "upper_bound": 100.0},
        ),
        ObjectiveSpec(
            "throughput",
            mode="maximize",
            weight=0.15,
            unit="m²/h",
            metadata={"lower_bound": 20.0, "upper_bound": 120.0},
        ),
    ],
)
