import pandas as pd


class CostEstimator:

    def __init__(self, rate_data):
        self.rate_data = rate_data

    def estimate(
        self,
        project_type,
        material_quality,
        area,
        floors,
        contingency,
        inflation
    ):

        df = self.rate_data.copy()

        df["Project_Type"] = (
            df["Project_Type"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        df["Material_Quality"] = (
            df["Material_Quality"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        project_type = project_type.strip().lower()
        material_quality = material_quality.strip().lower()

        filtered = df[
            (df["Project_Type"] == project_type) &
            (df["Material_Quality"] == material_quality)
        ]

        if filtered.empty:
            raise ValueError(
                f"No estimation rate found for Project Type '{project_type}' "
                f"and Material Quality '{material_quality}'."
            )

        row = filtered.iloc[0]

        cost_per_sqft = row["Cost_Per_Sqft"]
        labour_percentage = row["Labour_Percentage"]
        equipment_percentage = row["Equipment_Percentage"]
        duration_factor = row["Duration_Per_1000_Sqft_Months"]

        # Base Cost
        base_cost = area * cost_per_sqft

        # Floor Multiplier
        floor_multiplier = 1 + ((floors - 1) * 0.12)
        base_cost *= floor_multiplier

        # Inflation
        inflation_amount = base_cost * inflation / 100

        # Contingency
        contingency_amount = base_cost * contingency / 100

        total_cost = (
            base_cost
            + inflation_amount
            + contingency_amount
        )

        material_cost = total_cost * 0.40
        labour_cost = total_cost * labour_percentage / 100
        equipment_cost = total_cost * equipment_percentage / 100

        misc_cost = (
            total_cost
            - material_cost
            - labour_cost
            - equipment_cost
        )

        duration = (area / 1000) * duration_factor
        duration *= floor_multiplier

        return {

            "Total Cost": total_cost,

            "Material": material_cost,

            "Labour": labour_cost,

            "Equipment": equipment_cost,

            "Misc": misc_cost,

            "Duration": round(duration, 1)

        }