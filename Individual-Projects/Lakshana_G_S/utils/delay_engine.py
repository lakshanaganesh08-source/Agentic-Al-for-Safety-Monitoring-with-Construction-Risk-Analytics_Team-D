import pandas as pd


class DelayPredictor:

    def __init__(self, delay_df):
        self.delay_df = delay_df

    def predict(
        self,
        completion,
        weather,
        labour,
        material,
        budget
    ):

        score = 0

        # Completion
        if completion < 40:
            score += 30
        elif completion < 70:
            score += 15

        # Weather
        if weather == "High":
            score += 20
        elif weather == "Medium":
            score += 10

        # Labour
        if labour == "Low":
            score += 20
        elif labour == "Medium":
            score += 10

        # Material
        if material == "Low":
            score += 15
        elif material == "Medium":
            score += 8

        # Budget
        if budget > 80:
            score += 15
        elif budget > 60:
            score += 8

        probability = min(score, 100)

        if probability < 35:
            risk = "Low"
            days = 5

        elif probability < 65:
            risk = "Medium"
            days = 12

        else:
            risk = "High"
            days = 21

        return {

            "Probability": probability,

            "Risk": risk,

            "Expected Delay": days
        }