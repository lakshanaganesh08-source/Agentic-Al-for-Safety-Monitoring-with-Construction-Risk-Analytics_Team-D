"""
Material, labour, equipment, and BOQ estimation for construction projects.

Uses industry-standard quantity formulas scaled by built-up area, floors,
and building type. All rates are configured in Indian Rupees (₹ INR).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


BUILDING_TYPES = {
    "Residential": {"material_factor": 1.0, "labour_factor": 1.0, "equipment_factor": 0.9},
    "Commercial": {"material_factor": 1.15, "labour_factor": 1.1, "equipment_factor": 1.2},
    "Industrial": {"material_factor": 1.25, "labour_factor": 1.15, "equipment_factor": 1.35},
    "Infrastructure": {"material_factor": 1.4, "labour_factor": 1.2, "equipment_factor": 1.5},
}

# Unit costs (INR ₹) — standard Indian construction market rates
UNIT_COSTS = {
    "Cement": 420.0,         # per bag (50 kg)
    "Steel (Rebar)": 72.0,   # per kg
    "Sand": 2200.0,          # per cubic meter
    "Aggregate": 1800.0,     # per cubic meter
    "Bricks": 9.0,           # per unit
    "Ready-Mix Concrete": 5200.0,  # per cubic meter
    "Formwork Plywood": 1500.0,    # per sheet
    "Waterproofing": 60.0,         # per sq ft
}

# Labour rates in India (daily wage in ₹)
LABOUR_RATES = {
    "Mason": 850.0,
    "Carpenter": 850.0,
    "Steel Fixer": 900.0,
    "Electrician": 800.0,
    "Plumber": 800.0,
    "General Labour": 550.0,
    "Supervisor": 1200.0,
}

# Equipment rates in India (daily rental in ₹)
EQUIPMENT_RATES = {
    "Concrete Mixer": 2500.0,   # per day
    "Tower Crane": 18000.0,
    "Excavator": 12000.0,
    "Scaffolding Set": 3500.0,
    "Vibrator": 800.0,
    "Water Pump": 1200.0,
}

DEFAULT_WASTE_PCT = {
    "Cement": 5.0,
    "Steel (Rebar)": 3.0,
    "Sand": 8.0,
    "Aggregate": 8.0,
    "Bricks": 5.0,
    "Ready-Mix Concrete": 4.0,
    "Formwork Plywood": 10.0,
    "Waterproofing": 7.0,
}


@dataclass
class MaterialLine:
    material: str
    quantity: float
    unit: str
    unit_cost: float
    waste_pct: float

    @property
    def gross_quantity(self) -> float:
        return self.quantity * (1 + self.waste_pct / 100)

    @property
    def total_cost(self) -> float:
        return self.gross_quantity * self.unit_cost


@dataclass
class EstimationResult:
    area_sqft: float
    floors: int
    building_type: str
    duration_days: int
    materials: list[MaterialLine] = field(default_factory=list)
    labour: list[dict[str, Any]] = field(default_factory=list)
    equipment: list[dict[str, Any]] = field(default_factory=list)

    @property
    def material_cost(self) -> float:
        return sum(m.total_cost for m in self.materials)

    @property
    def labour_cost(self) -> float:
        return sum(row["total_cost"] for row in self.labour)

    @property
    def equipment_cost(self) -> float:
        return sum(row["total_cost"] for row in self.equipment)

    @property
    def total_cost(self) -> float:
        return self.material_cost + self.labour_cost + self.equipment_cost

    @property
    def total_waste_cost(self) -> float:
        return sum(
            m.quantity * (m.waste_pct / 100) * m.unit_cost for m in self.materials
        )

    def boq_rows(self) -> list[dict[str, Any]]:
        """Bill of Quantities line items for export and display."""
        rows: list[dict[str, Any]] = []
        for m in self.materials:
            rows.append({
                "Category": "Material",
                "Item": m.material,
                "Quantity": round(m.quantity, 2),
                "Unit": m.unit,
                "Waste %": m.waste_pct,
                "Gross Qty": round(m.gross_quantity, 2),
                "Unit Rate (₹)": m.unit_cost,
                "Amount (₹)": round(m.total_cost, 2),
            })
        for row in self.labour:
            rows.append({
                "Category": "Labour",
                "Item": row["trade"],
                "Quantity": row["workers"],
                "Unit": "workers",
                "Waste %": 0,
                "Gross Qty": row["man_days"],
                "Unit Rate (₹)": row["daily_rate"],
                "Amount (₹)": round(row["total_cost"], 2),
            })
        for row in self.equipment:
            rows.append({
                "Category": "Equipment",
                "Item": row["equipment"],
                "Quantity": row["days"],
                "Unit": "days",
                "Waste %": 0,
                "Gross Qty": row["days"],
                "Unit Rate (₹)": row["daily_rate"],
                "Amount (₹)": round(row["total_cost"], 2),
            })
        return rows


def _compute_material_quantities(
    area_sqft: float,
    floors: int,
    building_type: str,
) -> list[MaterialLine]:
    """Derive material quantities from area and floors using standard ratios."""
    factors = BUILDING_TYPES.get(building_type, BUILDING_TYPES["Residential"])
    factor = factors["material_factor"]
    total_area = area_sqft * floors

    # Ratios per 1000 sq ft (single floor equivalent)
    base = total_area / 1000.0

    specs = [
        ("Cement", base * 180 * factor, "bags", UNIT_COSTS["Cement"], DEFAULT_WASTE_PCT["Cement"]),
        ("Steel (Rebar)", base * 2800 * factor, "kg", UNIT_COSTS["Steel (Rebar)"], DEFAULT_WASTE_PCT["Steel (Rebar)"]),
        ("Sand", base * 12 * factor, "m³", UNIT_COSTS["Sand"], DEFAULT_WASTE_PCT["Sand"]),
        ("Aggregate", base * 10 * factor, "m³", UNIT_COSTS["Aggregate"], DEFAULT_WASTE_PCT["Aggregate"]),
        ("Bricks", base * 4500 * factor, "units", UNIT_COSTS["Bricks"], DEFAULT_WASTE_PCT["Bricks"]),
        ("Ready-Mix Concrete", base * 8 * factor, "m³", UNIT_COSTS["Ready-Mix Concrete"], DEFAULT_WASTE_PCT["Ready-Mix Concrete"]),
        ("Formwork Plywood", base * 45 * factor, "sheets", UNIT_COSTS["Formwork Plywood"], DEFAULT_WASTE_PCT["Formwork Plywood"]),
        ("Waterproofing", total_area * 0.15 * factor, "sq ft", UNIT_COSTS["Waterproofing"], DEFAULT_WASTE_PCT["Waterproofing"]),
    ]

    return [
        MaterialLine(material=name, quantity=qty, unit=unit, unit_cost=cost, waste_pct=waste)
        for name, qty, unit, cost, waste in specs
    ]


def _compute_labour(
    area_sqft: float,
    floors: int,
    building_type: str,
    duration_days: int,
) -> list[dict[str, Any]]:
    factors = BUILDING_TYPES.get(building_type, BUILDING_TYPES["Residential"])
    labour_factor = factors["labour_factor"]
    total_area = area_sqft * floors
    scale = max(1.0, total_area / 5000.0) * labour_factor

    crew = [
        ("Mason", max(2, int(4 * scale)), 0.25),
        ("Carpenter", max(2, int(3 * scale)), 0.20),
        ("Steel Fixer", max(1, int(3 * scale)), 0.22),
        ("Electrician", max(1, int(2 * scale)), 0.15),
        ("Plumber", max(1, int(2 * scale)), 0.12),
        ("General Labour", max(4, int(8 * scale)), 0.35),
        ("Supervisor", max(1, int(2 * scale)), 0.08),
    ]

    rows: list[dict[str, Any]] = []
    for trade, workers, time_share in crew:
        man_days = workers * duration_days * time_share
        daily_rate = LABOUR_RATES[trade]
        rows.append({
            "trade": trade,
            "workers": workers,
            "man_days": round(man_days, 1),
            "daily_rate": daily_rate,
            "total_cost": round(man_days * daily_rate, 2),
        })
    return rows


def _compute_equipment(
    area_sqft: float,
    floors: int,
    building_type: str,
    duration_days: int,
) -> list[dict[str, Any]]:
    factors = BUILDING_TYPES.get(building_type, BUILDING_TYPES["Residential"])
    equip_factor = factors["equipment_factor"]
    total_area = area_sqft * floors
    scale = max(1.0, total_area / 8000.0) * equip_factor

    needs = [
        ("Concrete Mixer", min(duration_days, int(duration_days * 0.4))),
        ("Tower Crane", duration_days if floors > 2 else int(duration_days * 0.3)),
        ("Excavator", min(30, int(duration_days * 0.15 * scale))),
        ("Scaffolding Set", int(duration_days * 0.6)),
        ("Vibrator", min(duration_days, int(duration_days * 0.25))),
        ("Water Pump", min(duration_days, int(duration_days * 0.2))),
    ]

    rows: list[dict[str, Any]] = []
    for name, days in needs:
        days = max(1, days)
        rate = EQUIPMENT_RATES[name]
        rows.append({
            "equipment": name,
            "days": days,
            "daily_rate": rate,
            "total_cost": round(days * rate, 2),
        })
    return rows


def estimate_materials(
    area_sqft: float,
    floors: int,
    building_type: str = "Residential",
    duration_days: int = 90,
) -> EstimationResult:
    """
    Run full material, labour, and equipment estimation.

    Args:
        area_sqft: Built-up area per floor in square feet.
        floors: Number of floors.
        building_type: One of Residential, Commercial, Industrial, Infrastructure.
        duration_days: Expected project duration for labour/equipment scaling.

    Returns:
        EstimationResult with BOQ-ready breakdown.
    """
    if area_sqft <= 0 or floors <= 0 or duration_days <= 0:
        raise ValueError("Area, floors, and duration must be positive.")

    materials = _compute_material_quantities(area_sqft, floors, building_type)
    labour = _compute_labour(area_sqft, floors, building_type, duration_days)
    equipment = _compute_equipment(area_sqft, floors, building_type, duration_days)

    return EstimationResult(
        area_sqft=area_sqft,
        floors=floors,
        building_type=building_type,
        duration_days=duration_days,
        materials=materials,
        labour=labour,
        equipment=equipment,
    )
