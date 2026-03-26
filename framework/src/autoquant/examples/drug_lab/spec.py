from autoquant.core.specs import ObjectiveSpec, ParameterSpec, ScenarioSpec


DRUG_LAB_SCENARIO = ScenarioSpec(
    name="drug_lab_demo",
    parameters=[
        ParameterSpec("temperature", 20.0, 80.0, "°C", "reaction temperature"),
        ParameterSpec("humidity", 40.0, 80.0, "%", "ambient humidity"),
        ParameterSpec("aux1_ratio", 0.5, 5.0, "%", "surfactant ratio"),
        ParameterSpec("aux2_ratio", 0.0, 3.0, "%", "stabilizer ratio"),
        ParameterSpec("duration", 60.0, 300.0, "min", "reaction duration"),
        ParameterSpec("stirring_speed", 100.0, 1000.0, "rpm", "stirring speed"),
        ParameterSpec("pH", 4.0, 9.0, "", "solution pH"),
        ParameterSpec("solvent_concentration", 10.0, 50.0, "%", "solvent concentration"),
    ],
    objectives=[
        ObjectiveSpec("half_life", mode="match_bell", target=12.0, weight=0.6, unit="h", tolerance=0.5),
        ObjectiveSpec(
            "stability_index",
            mode="maximize",
            weight=0.3,
            unit="score",
            metadata={"lower_bound": 40.0, "upper_bound": 100.0},
        ),
        ObjectiveSpec(
            "solubility",
            mode="maximize",
            weight=0.1,
            unit="mg/mL",
            metadata={"lower_bound": 2.0, "upper_bound": 35.0},
        ),
    ],
    fixed_components={
        "primary_api_ratio": 20.0,
        "primary_solvent": "default-buffer",
    },
)
