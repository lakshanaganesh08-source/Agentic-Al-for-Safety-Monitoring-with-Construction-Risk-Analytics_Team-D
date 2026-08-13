import io
import pandas as pd

class ExcelGenerator:
    """
    Utility class to generate professional multi-tab Excel files
    containing project parameters, costs, timelines, scores, and AI recommendations.
    """
    
    @staticmethod
    def generate_report(data: dict) -> bytes:
        # Create bytes buffer
        buffer = io.BytesIO()
        
        # Prepare Sheets Data
        raw = data['raw_inputs']
        
        cost_lakhs = round(data['estimated_cost'] / 100000, 1)
        budget_lakhs = round(raw['budget'] / 100000, 1)

        # Sheet 1: Project Summary
        metrics_df = pd.DataFrame([
            {"Detail": "Recommended House Type",       "Value": str(data['suitable_type'])},
            {"Detail": "AI Confidence",                "Value": f"{data['confidence']}%"},
            {"Detail": "Total Plot Size",              "Value": f"{raw['total_area']:.0f} sq ft"},
            {"Detail": "Plot Length",                  "Value": f"{raw['length']:.0f} ft"},
            {"Detail": "Plot Width",                   "Value": f"{raw['width']:.0f} ft"},
            {"Detail": "Location",                     "Value": str(raw['location'])},
            {"Detail": "Area to Build On",             "Value": f"{data['recommended_built_up']:.0f} sq ft"},
            {"Detail": "Open Space Left",              "Value": f"{data['remaining_open']:.0f} sq ft"},
            {"Detail": "Construction Style",           "Value": str(raw['construction_type'])},
            {"Detail": "Material Quality",             "Value": str(raw['material_quality'])},
            {"Detail": "Your Budget",                  "Value": f"₹{budget_lakhs} Lakhs"},
            {"Detail": "Estimated Build Cost",         "Value": f"₹{cost_lakhs} Lakhs (@ ₹3,500/sqft)"},
            {"Detail": "Time to Complete",             "Value": f"{data['construction_time']} months"},
            {"Detail": "Parking Included",             "Value": "Yes" if raw['parking_needed'] else "No"},
            {"Detail": "Garden Included",              "Value": "Yes" if raw['garden_needed'] else "No"},
            {"Detail": "Future Expansion Planned",     "Value": "Yes" if raw['future_expansion'] else "No"},
            {"Detail": "Number of Family Members",     "Value": raw['family_size']},
            {"Detail": "Floor Preference",             "Value": raw['floor_pref']}
        ])

        # Sheet 2: Scores
        scores_df = pd.DataFrame([
            {"Score Type": "Safety Rating",           "Result": f"{data['safety_score']}%"},
            {"Score Type": "Energy Efficiency",       "Result": f"{data['energy_efficiency']}%"},
            {"Score Type": "Sustainability (out of 5)","Result": f"{data['sustainability_rating']}"},
            {"Score Type": "Future Expansion Score",  "Result": f"{data['future_expansion_score']}%"}
        ])

        insights_df = pd.DataFrame([
            {"AI Tips & Suggestions": insight} for insight in data['insights']
        ])
        
        # Use pandas ExcelWriter to output in multiple sheets
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            metrics_df.to_excel(writer, sheet_name='Project Plan', index=False)
            scores_df.to_excel(writer, sheet_name='Safety & Eco Ratings', index=False)
            insights_df.to_excel(writer, sheet_name='AI Strategic Insights', index=False)
            
            # Retrieve sheet styling components
            workbook = writer.book
            
            # Simple column width adjustments for readability
            for sheetname in workbook.sheetnames:
                worksheet = workbook[sheetname]
                for col in worksheet.columns:
                    max_len = max(len(str(cell.value or '')) for cell in col)
                    col_letter = col[0].column_letter
                    worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
        
        # Get Excel bytes
        excel_bytes = buffer.getvalue()
        buffer.close()
        return excel_bytes
