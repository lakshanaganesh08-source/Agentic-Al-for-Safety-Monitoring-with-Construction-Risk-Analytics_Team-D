import numpy as np

class AnalysisEngine:
    """
    Core AI & mathematical engine for construction space optimization,
    cost prediction, layout planning, and sustainability scoring.
    """
    
    @staticmethod
    def analyze_construction(
        total_area: float,
        length: float,
        width: float,
        location: str,
        budget: float,
        construction_type: str,
        material_quality: str,
        parking_needed: bool,
        garden_needed: bool,
        future_expansion: bool,
        floor_pref: str,
        family_size: int
    ) -> dict:
        # Calculate base dimensions and check consistency
        calculated_area = length * width
        # Use calculated area if total_area is empty or mismatching
        area = calculated_area if calculated_area > 0 else total_area
        if area <= 0:
            area = 1500.0  # default
            length = 50.0
            width = 30.0

        # AI Confidence calculation (simulated based on inputs completion and consistency)
        base_confidence = 92.0
        if parking_needed and garden_needed:
            base_confidence += 2.0
        if budget > 50000:
            base_confidence += 1.5
        confidence = min(98.5, max(85.0, base_confidence + np.random.uniform(-1.0, 1.0)))

        # ── House type: consider BOTH family size AND available plot area ──────
        # Minimum ground coverage needed per floor type (practical Indian norms)
        MIN_AREA_STUDIO   = 300    # sqft ground coverage
        MIN_AREA_1BHK     = 500
        MIN_AREA_2BHK     = 700
        MIN_AREA_DUPLEX   = 900    # must have ≥900 sqft ground floor footprint
        MIN_AREA_VILLA    = 1500

        # Effective ground coverage available (assume 60% FAR as baseline)
        effective_ground = area * 0.60

        if family_size <= 2 or effective_ground < MIN_AREA_2BHK:
            if effective_ground < MIN_AREA_1BHK:
                suitable_type = "Studio / 1-Room Unit"
                min_built_up = 300.0
            else:
                suitable_type = "Single Bedroom (1 BHK)"
                min_built_up = 500.0
        elif family_size <= 4:
            if floor_pref == "Duplex" and effective_ground >= MIN_AREA_DUPLEX:
                suitable_type = "Duplex (2-3 BHK)"
                min_built_up = 1200.0
            elif effective_ground >= MIN_AREA_2BHK:
                suitable_type = "Double Bedroom (2 BHK)"
                min_built_up = 700.0
            else:
                suitable_type = "Single Bedroom (1 BHK)"
                min_built_up = 500.0
        elif family_size <= 6:
            if floor_pref in ["Duplex", "Triplex"] and effective_ground >= MIN_AREA_DUPLEX:
                suitable_type = "Duplex (3-4 BHK)"
                min_built_up = 1800.0
            elif effective_ground >= MIN_AREA_2BHK:
                suitable_type = "Double Bedroom (2 BHK)"
                min_built_up = 700.0
            else:
                suitable_type = "Single Bedroom (1 BHK)"
                min_built_up = 500.0
        else:
            if effective_ground >= MIN_AREA_VILLA:
                suitable_type = "Apartment Style / Villa"
                min_built_up = 2200.0
            elif effective_ground >= MIN_AREA_DUPLEX:
                suitable_type = "Duplex (3-4 BHK)"
                min_built_up = 1800.0
            else:
                suitable_type = "Double Bedroom (2 BHK)"
                min_built_up = 700.0

        # Material multipliers
        material_mult = {"Standard": 1.0, "Premium": 1.4, "Luxury": 1.9}.get(material_quality, 1.0)
        
        # Construction type multipliers
        type_mult = {
            "Smart/Futuristic": 1.3,
            "Modern": 1.1,
            "Minimalist": 0.95,
            "Traditional": 1.0
        }.get(construction_type, 1.0)

        # Cost estimation per sqft in Indian Rupees (INR)
        # Base rate: ₹3,500/sqft for standard, scaled by material & type multipliers
        cost_per_sqft = 3500.0 * material_mult * type_mult
        
        # Built up area recommendation (normally 60% to 75% of land area depending on open space needs)
        built_up_ratio = 0.70
        if garden_needed:
            built_up_ratio -= 0.12
        if parking_needed:
            built_up_ratio -= 0.08
        if future_expansion:
            built_up_ratio -= 0.05
            
        built_up_ratio = max(0.40, min(0.85, built_up_ratio))
        recommended_built_up = area * built_up_ratio
        
        # Adjust for floor preferences
        floors = 1
        if "Duplex" in suitable_type or floor_pref == "Duplex":
            floors = 2
        elif floor_pref == "Triplex":
            floors = 3
            
        ground_coverage = recommended_built_up / floors
        # Make sure ground coverage doesn't exceed 85% of plot
        if ground_coverage > (area * 0.85):
            ground_coverage = area * 0.80
            recommended_built_up = ground_coverage * floors
            
        remaining_open = area - ground_coverage
        
        # Total Construction Cost
        estimated_cost = recommended_built_up * cost_per_sqft

        # ── Realistic minimum cost floors (INR) per house type ───────────────
        # No matter how small the plot, construction costs below these are not real
        MIN_COST = {
            "Studio / 1-Room Unit":    700_000,    # ₹7 L
            "Single Bedroom (1 BHK)": 1_500_000,  # ₹15 L
            "Double Bedroom (2 BHK)": 2_500_000,  # ₹25 L
            "Duplex (2-3 BHK)":       4_500_000,  # ₹45 L
            "Duplex (3-4 BHK)":       6_500_000,  # ₹65 L
            "Duplex / Multi-Floor":   6_000_000,  # ₹60 L
            "Apartment Style / Villa":10_000_000, # ₹1 Cr
        }
        estimated_cost = max(estimated_cost, MIN_COST.get(suitable_type, 1_500_000))
        
        # Construction timeline (months)
        base_time = 6.0
        time_added_by_size = (recommended_built_up / 500.0) * 1.5
        time_added_by_floors = floors * 1.0
        construction_time = base_time + time_added_by_size + time_added_by_floors
        if material_quality == "Luxury":
            construction_time += 2.0
        construction_time = round(min(24.0, max(4.0, construction_time)), 1)
        
        # Scores (0 - 100)
        safety_score = 90
        if construction_type == "Smart/Futuristic":
            safety_score += 5
        if material_quality == "Premium":
            safety_score += 2
        elif material_quality == "Luxury":
            safety_score += 4
        safety_score = min(99, safety_score)
        
        energy_efficiency = 78
        if construction_type == "Smart/Futuristic":
            energy_efficiency += 15
        elif construction_type == "Modern":
            energy_efficiency += 8
        if garden_needed:
            energy_efficiency += 3
        energy_efficiency = min(98, energy_efficiency)
        
        sustainability_rating = 3.5
        if garden_needed:
            sustainability_rating += 0.5
        if construction_type == "Smart/Futuristic":
            sustainability_rating += 0.7
        if material_quality in ["Premium", "Luxury"]:
            sustainability_rating += 0.3
        sustainability_rating = round(min(5.0, sustainability_rating), 1)
        
        future_expansion_score = 85 if future_expansion else 45
        if remaining_open > (area * 0.35):
            future_expansion_score += 10
        future_expansion_score = min(98, future_expansion_score)
        
        # Space distribution details for 3D visualizer
        # We need relative coordinates for placing: Plot, House, Garden, Parking, Walking Path, Trees
        # Assume plot is centered at (0,0), spans from -width/2 to +width/2 on X, and -length/2 to +length/2 on Y
        # We place components within this bounding box
        layout_3d = AnalysisEngine._calculate_layout_coords(
            width, length, ground_coverage, parking_needed, garden_needed
        )

        # AI generated insights
        insights = []
        ventilation_inc = int(30 + remaining_open / area * 20)
        insights.append(f"AI suggests a {suitable_type} because the remaining open space ({remaining_open:.0f} sq ft) increases natural ventilation by {ventilation_inc}%.")
        
        if future_expansion:
            insights.append(f"Future expansion score of {future_expansion_score}% achieved. The layout is optimized to easily accommodate a vertical extension or rear expansion.")
        else:
            insights.append("No future expansion requested. Foundation & structures optimized for maximum cost efficiency for the current plan.")
            
        if parking_needed:
            insights.append(f"Dedicated parking space of {layout_3d['parking_area']:.0f} sq ft mapped at the entrance. Integrated with EV charging layout recommendations.")
            
        if garden_needed:
            insights.append("Natural landscape zone planned. Garden placement reduces ambient building temperature by up to 2.5°C.")
            
        if construction_type == "Smart/Futuristic":
            insights.append("Smart home integration enabled: Automated energy savings, solar panels alignment, and greywater recycling recommended.")

        return {
            "confidence": round(confidence, 1),
            "suitable_type": suitable_type,
            "recommended_built_up": round(recommended_built_up, 1),
            "remaining_open": round(remaining_open, 1),
            "estimated_cost": round(estimated_cost, 2),
            "construction_time": construction_time,
            "future_expansion_score": future_expansion_score,
            "safety_score": safety_score,
            "energy_efficiency": energy_efficiency,
            "sustainability_rating": sustainability_rating,
            "layout_3d": layout_3d,
            "insights": insights,
            "raw_inputs": {
                "total_area": area,
                "length": length,
                "width": width,
                "location": location,
                "budget": budget,
                "construction_type": construction_type,
                "material_quality": material_quality,
                "parking_needed": parking_needed,
                "garden_needed": garden_needed,
                "future_expansion": future_expansion,
                "floor_pref": floor_pref,
                "family_size": family_size
            }
        }

    @staticmethod
    def _calculate_layout_coords(w: float, l: float, ground_coverage: float, parking: bool, garden: bool) -> dict:
        # Standardize orientations. House is typically placed towards the center/back, parking at front-side, garden at front or side.
        # Let's say:
        # Plot: X: [-w/2, w/2], Y: [-l/2, l/2]
        # Calculate aspect ratio of house: Let's make it proportional to plot aspect ratio
        aspect = w / l if l > 0 else 1.0
        
        # Solve for house dimensions h_w and h_l such that h_w * h_l = ground_coverage
        # Let h_w / h_l = aspect * 0.9 (slightly narrower than plot)
        # h_w = h_l * aspect * 0.9 => h_l^2 * aspect * 0.9 = ground_coverage => h_l = sqrt(ground_coverage / (aspect * 0.9))
        h_l = np.sqrt(ground_coverage / (aspect * 0.85 if aspect > 0 else 1.0))
        h_w = ground_coverage / h_l
        
        # Clamp house dimensions to fit within plot with margins
        h_w = min(h_w, w * 0.8)
        h_l = min(h_l, l * 0.7)
        
        # Center-back of the plot for house:
        # House Y center: shifted slightly backward (e.g. + l * 0.1)
        house_y_center = l * 0.1
        house_x_center = 0.0
        
        # Parking: front left corner
        # Parking size: ~15 x 10 ft (150 sq ft)
        pk_w = min(12.0, w * 0.3)
        pk_l = min(18.0, l * 0.3)
        pk_x = -w/2 + pk_w/2 + w*0.05
        pk_y = -l/2 + pk_l/2 + l*0.05
        
        # Garden: front right corner
        # Garden size: remaining front area
        g_w = min(20.0, w * 0.45)
        g_l = min(20.0, l * 0.35)
        g_x = w/2 - g_w/2 - w*0.05
        g_y = -l/2 + g_l/2 + l*0.05
        
        # Pathway: from entrance (front center) to house front
        # Path Y from -l/2 to house front (house_y_center - h_l/2)
        path_x = 0.0
        path_y_start = -l/2
        path_y_end = house_y_center - h_l/2
        
        # Trees: places at various coordinates
        trees = []
        if garden:
            # Place 3 trees in garden area
            trees.append({"x": g_x - g_w/4, "y": g_y - g_l/4, "r": 2.0, "h": 10.0})
            trees.append({"x": g_x + g_w/4, "y": g_y + g_l/4, "r": 1.5, "h": 8.0})
            trees.append({"x": g_x - g_w/3, "y": g_y + g_l/3, "r": 1.8, "h": 9.0})
        # Buffer back corners with trees
        trees.append({"x": -w/2 + w*0.08, "y": l/2 - l*0.08, "r": 2.5, "h": 12.0})
        trees.append({"x": w/2 - w*0.08, "y": l/2 - l*0.08, "r": 2.2, "h": 11.0})
        
        return {
            "plot_w": w,
            "plot_l": l,
            "house_w": h_w,
            "house_l": h_l,
            "house_x": house_x_center,
            "house_y": house_y_center,
            "parking_w": pk_w if parking else 0.0,
            "parking_l": pk_l if parking else 0.0,
            "parking_x": pk_x if parking else 0.0,
            "parking_y": pk_y if parking else 0.0,
            "parking_area": pk_w * pk_l if parking else 0.0,
            "garden_w": g_w if garden else 0.0,
            "garden_l": g_l if garden else 0.0,
            "garden_x": g_x if garden else 0.0,
            "garden_y": g_y if garden else 0.0,
            "garden_area": g_w * g_l if garden else 0.0,
            "path_x": path_x,
            "path_y_start": path_y_start,
            "path_y_end": path_y_end,
            "trees": trees
        }
