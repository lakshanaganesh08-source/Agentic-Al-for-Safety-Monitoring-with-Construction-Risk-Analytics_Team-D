"""
material_calculator.py
-----------------------
Rule-of-thumb material estimator for early-stage residential/commercial
construction budgeting, driven purely by built-up area (sq.ft).

These coefficients are widely used INDUSTRY THUMB RULES for quick estimation
in Indian/South-Asian residential construction (RCC framed structure).
They are NOT a substitute for a structural engineer's detailed BOQ
(Bill of Quantities) — always mention that in the UI.
"""

from dataclasses import dataclass


# Coefficients per sq.ft of built-up area, by construction quality tier.
# (cement in bags, steel in kg, sand in cft, aggregate in cft, bricks in nos,
#  paint in litres, tiles in sqft, labour in man-days)
TIER_COEFFICIENTS = {
    "Economy": dict(cement=0.35, steel=3.5, sand=1.4, aggregate=1.8, bricks=7,  paint=0.08, tiles=1.0, labour=0.9),
    "Standard": dict(cement=0.40, steel=4.2, sand=1.6, aggregate=2.0, bricks=8,  paint=0.10, tiles=1.0, labour=1.0),
    "Premium":  dict(cement=0.48, steel=5.0, sand=1.9, aggregate=2.3, bricks=9,  paint=0.14, tiles=1.0, labour=1.15),
}

# Approx market unit rates (INR) — editable defaults, user can override in UI.
DEFAULT_UNIT_RATES = dict(
    cement=400,      # per bag (50kg)
    steel=68,        # per kg
    sand=55,         # per cft
    aggregate=50,    # per cft
    bricks=8,        # per brick
    paint=280,       # per litre
    tiles=65,        # per sqft
    labour=900,      # per man-day
)


@dataclass
class MaterialEstimate:
    area_sqft: float
    tier: str
    cement_bags: float
    steel_kg: float
    sand_cft: float
    aggregate_cft: float
    bricks_nos: float
    paint_litres: float
    tiles_sqft: float
    labour_mandays: float
    total_cost: float
    cost_breakdown: dict


def estimate_materials(area_sqft: float, tier: str = "Standard", floors: int = 1,
                        unit_rates: dict = None) -> MaterialEstimate:
    """Compute material quantities & approximate cost for a given built-up area."""
    if area_sqft <= 0:
        raise ValueError("Area must be greater than 0 sq.ft")

    coeff = TIER_COEFFICIENTS.get(tier, TIER_COEFFICIENTS["Standard"])
    rates = unit_rates or DEFAULT_UNIT_RATES

    total_area = area_sqft * max(floors, 1)

    quantities = {k: round(total_area * v, 1) for k, v in coeff.items()}

    cost_breakdown = {
        material: round(quantities[material] * rates.get(material, 0), 2)
        for material in quantities
    }
    total_cost = round(sum(cost_breakdown.values()), 2)

    return MaterialEstimate(
        area_sqft=total_area,
        tier=tier,
        cement_bags=quantities["cement"],
        steel_kg=quantities["steel"],
        sand_cft=quantities["sand"],
        aggregate_cft=quantities["aggregate"],
        bricks_nos=quantities["bricks"],
        paint_litres=quantities["paint"],
        tiles_sqft=quantities["tiles"],
        labour_mandays=quantities["labour"],
        total_cost=total_cost,
        cost_breakdown=cost_breakdown,
    )
