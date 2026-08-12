import pandas as pd


class MaterialEstimator:

    def __init__(self, materials_df):
        self.materials = materials_df

    def estimate(self, area):

        # Approximate consumption factors per sq.ft
        factors = {
            "Cement": 0.18,
            "TMT Bars": 4.5,
            "River Sand": 0.015,
            "Aggregate 20mm": 0.020,
            "Fly Ash Bricks": 20,
            "Weatherproof Paint": 0.16,
        }

        result = []

        total_cost = 0

        for _, row in self.materials.iterrows():

            material = row["Material"]

            if material not in factors:
                continue

            quantity = area * factors[material]

            cost = quantity * row["Rate"]

            total_cost += cost

            result.append({
                "Material": material,
                "Unit": row["Unit"],
                "Quantity": round(quantity, 2),
                "Rate": row["Rate"],
                "Cost": round(cost, 2),
                "Availability": row["Availability"]
            })

        df = pd.DataFrame(result)

        return df, total_cost