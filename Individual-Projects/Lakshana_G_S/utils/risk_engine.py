class RiskPredictor:

    def predict(
        self,
        budget,
        schedule,
        safety,
        weather,
        material,
        labour
    ):

        score = (
            budget +
            schedule +
            safety +
            weather +
            material +
            labour
        ) / 6

        if score < 35:
            level = "Low"

        elif score < 70:
            level = "Medium"

        else:
            level = "High"

        return {

            "Score": round(score, 1),

            "Level": level

        }