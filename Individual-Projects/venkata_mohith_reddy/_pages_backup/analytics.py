import streamlit as st
import plotly.graph_objects as go
import pydeck as pdk
import pandas as pd
import numpy as np
from ui_components import UIComponents

class AnalyticsPage:
    """
    Renders deep-dive analytical charts (radar material usage, cost breakdown bar,
    space allocation pie, floor utilization line) and interactive geographical mapping
    with nearby facilities plotting.
    """
    
    @staticmethod
    def render():
        if "analysis_results" not in st.session_state or st.session_state.analysis_results is None:
            st.warning("⚠️ No simulation data found. Please run the analysis first in the Space Analysis tab.")
            if st.button("📐 Go to Space Analysis"):
                st.session_state.current_page = "📐 Space Analysis"
                st.rerun()
            return
            
        data = st.session_state.analysis_results
        raw = data['raw_inputs']
        layout = data['layout_3d']
        
        st.markdown("<h2 style='margin-bottom: 20px; color: #00F5D4 !important;'>📊 Project Space & Cost Analytics</h2>", unsafe_allow_html=True)
        
        # TABBED CHART DESIGN
        tab1, tab2, tab3 = st.tabs(["📊 Resource & Cost Charts", "🗺️ Geographic GIS Mapping", "📈 Future Extension Metrics"])
        
        with tab1:
            col_c1, col_c2 = st.columns(2, gap="large")
            
            with col_c1:
                # 1. Area Distribution Pie Chart
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>📐 Plot Area Distribution</h4>", unsafe_allow_html=True)
                fig_pie = AnalyticsPage._create_area_pie(data, raw, layout)
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 2. Material Profile Radar Chart
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>💎 Structural Material Radar Profile</h4>", unsafe_allow_html=True)
                fig_radar = AnalyticsPage._create_material_radar(raw['construction_type'])
                st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_c2:
                # 3. Cost Breakdown Bar Chart
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>💰 Capital Cost Allocation</h4>", unsafe_allow_html=True)
                fig_bar = AnalyticsPage._create_cost_bar(data['estimated_cost'])
                st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 4. Floor Utilization Line Chart
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>🏢 Floor-by-Floor Load Distribution</h4>", unsafe_allow_html=True)
                fig_line = AnalyticsPage._create_floor_line(raw['floor_pref'], data['recommended_built_up'])
                st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
        with tab2:
            st.markdown('<div class="glass-card neon-card-blue">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>🗺️ GIS Geographic Mapping (Telemetry)</h4>", unsafe_allow_html=True)
            
            # Map parameters based on Location Zone
            lat, lon, zone_desc = AnalyticsPage._get_zone_coordinates(raw['location'])
            
            st.write(f"**Current Center Coordinate:** `{lat:.4f}, {lon:.4f}` ({raw['location']} Zone - {zone_desc})")
            
            # Add option for Map styles
            map_style = st.selectbox(
                "Map Layer Visual Style",
                ["Satellite View", "Road View (Futuristic Dark)"],
                index=1
            )
            
            # Generate simulated nearby amenities
            map_data = AnalyticsPage._generate_map_markers(lat, lon)
            
            # Render deckGL Map
            deck_fig = AnalyticsPage._create_pydeck_map(lat, lon, map_data, map_style)
            st.pydeck_chart(deck_fig)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with tab3:
            st.markdown('<div class="glass-card neon-card-purple">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>📈 Foundation Load & Vertical Expansion Capability</h4>", unsafe_allow_html=True)
            
            # Future expansion scoring breakdown
            col_x1, col_x2 = st.columns(2)
            with col_x1:
                st.write("")
                st.write(f"**Structural Expansion Safety Score:** `{data['future_expansion_score']}%`")
                st.progress(data['future_expansion_score'])
                
                st.write(f"**Zoning Limit Compliance:** `92%` (Max floor heights standard)")
                st.progress(92)
                
                st.write(f"**Foundation Reserve Strength:** `+45%` (Safe for vertical additions)")
                st.progress(45)
            
            with col_x2:
                # Add bar chart for loading metrics
                fig_exp = go.Figure()
                fig_exp.add_trace(go.Bar(
                    name='Current Design Load',
                    x=['Foundation', 'Collar Pillars', 'Slab Load'],
                    y=[100, 100, 100],
                    marker_color='#4D39E9'
                ))
                fig_exp.add_trace(go.Bar(
                    name='Reserve Ultimate Capacity',
                    x=['Foundation', 'Collar Pillars', 'Slab Load'],
                    y=[160, 145, 130],
                    marker_color='#00F5D4'
                ))
                fig_exp.update_layout(
                    barmode='group',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': "#E2E8F0"},
                    height=200,
                    margin=dict(l=20, r=20, t=10, b=20)
                )
                st.plotly_chart(fig_exp, use_container_width=True)
                
            st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def _create_area_pie(data: dict, raw: dict, layout: dict) -> go.Figure:
        labels = ['Built-up Footprint', 'Landscape Garden', 'Parking Garage', 'Remaining Setbacks']
        
        # Values in sq ft
        built_footprint = layout['house_w'] * layout['house_l']
        garden_sqft = layout['garden_area']
        parking_sqft = layout['parking_area']
        remaining = raw['total_area'] - (built_footprint + garden_sqft + parking_sqft)
        
        values = [built_footprint, garden_sqft, parking_sqft, max(0.0, remaining)]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.4,
            marker=dict(colors=['#4D39E9', '#00F5D4', '#00B4D8', 'rgba(255,255,255,0.08)']),
            textinfo='percent'
        )])
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "#E2E8F0"},
            height=200,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(orientation="h", y=-0.1)
        )
        return fig

    @staticmethod
    def _create_material_radar(style: str) -> go.Figure:
        categories = ['Concrete', 'Structural Steel', 'Aesthetic Glass', 'Masonry/Brick', 'Timber Trim', 'Eco-Composite']
        
        # Profile maps based on style style
        profiles = {
            "Smart/Futuristic": [8, 9, 8, 3, 5, 10],
            "Modern": [9, 8, 9, 4, 6, 7],
            "Minimalist": [7, 7, 7, 5, 4, 8],
            "Traditional": [6, 4, 4, 9, 8, 5]
        }
        
        r_values = profiles.get(style, [7, 7, 7, 7, 7, 7])
        # Close the loop for the radar plot
        categories.append(categories[0])
        r_values.append(r_values[0])
        
        fig = go.Figure(data=go.Scatterpolar(
            r=r_values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(0, 180, 216, 0.15)',
            line=dict(color='#00B4D8', width=2),
            name='Material Strength Index'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10], color='rgba(255,255,255,0.3)', gridcolor='rgba(255,255,255,0.05)'),
                angularaxis=dict(color='#A0AEC0', gridcolor='rgba(255,255,255,0.05)')
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "#E2E8F0"},
            height=200,
            margin=dict(l=40, r=40, t=10, b=10),
            showlegend=False
        )
        return fig

    @staticmethod
    def _create_cost_bar(total_cost: float) -> go.Figure:
        stages = ['Excavation', 'Structure', 'MEP/Smart', 'Finishes', 'Landscaping', 'Contingency']
        splits = [0.10, 0.35, 0.20, 0.23, 0.07, 0.05]
        costs = [total_cost * pct for pct in splits]
        
        fig = go.Figure(data=[go.Bar(
            x=stages,
            y=costs,
            marker_color=['#8A2BE2', '#4D39E9', '#00B4D8', '#00F5D4', '#FF9F1C', 'rgba(255,255,255,0.3)'],
            hoverinfo='y+x'
        )])
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "#E2E8F0"},
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#A0AEC0'),
            xaxis=dict(color='#A0AEC0'),
            height=200,
            margin=dict(l=20, r=20, t=10, b=10)
        )
        return fig

    @staticmethod
    def _create_floor_line(floor_pref: str, recommended_built_up: float) -> go.Figure:
        if floor_pref == "Single Floor":
            levels = ["Ground Floor"]
            loads = [recommended_built_up]
        elif floor_pref == "Duplex":
            levels = ["Ground Floor", "Level 1"]
            loads = [recommended_built_up * 0.6, recommended_built_up * 0.4]
        else: # Triplex
            levels = ["Ground Floor", "Level 1", "Level 2"]
            loads = [recommended_built_up * 0.5, recommended_built_up * 0.3, recommended_built_up * 0.2]
            
        fig = go.Figure(data=go.Scatter(
            x=levels,
            y=loads,
            mode='lines+markers',
            line=dict(color='#00F5D4', width=3),
            marker=dict(size=8, color='#FFFFFF', line=dict(width=2, color='#00F5D4')),
            fill='tozeroy',
            fillcolor='rgba(0, 245, 212, 0.07)'
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "#E2E8F0"},
            yaxis=dict(title="Slab Footprint (sq ft)", gridcolor='rgba(255,255,255,0.05)', color='#A0AEC0'),
            xaxis=dict(color='#A0AEC0'),
            height=200,
            margin=dict(l=20, r=20, t=10, b=10)
        )
        return fig

    @staticmethod
    def _get_zone_coordinates(zone: str) -> tuple:
        """
        Returns (latitude, longitude, description) centered around Visakhapatnam region.
        """
        zones = {
            "Urban Core": (17.7231, 83.3013, "Visakhapatnam Metropolitan Hub"),
            "Suburban Sector": (17.8184, 83.3481, "Madhurawada Sub-core expansion"),
            "Coastal District": (17.6801, 83.2323, "Beachfront residential zone"),
            "Mountain Terrain": (18.2713, 82.8724, "Araku Valley green slopes"),
            "Industrial Extension": (17.6183, 83.1517, "Gajuwaka Industrial & Logistical corridor")
        }
        return zones.get(zone, (17.7231, 83.3013, "Standard Central Sector"))

    @staticmethod
    def _generate_map_markers(lat: float, lon: float) -> pd.DataFrame:
        """
        Creates coordinates for construction site + 4 nearby amenities.
        """
        data = [
            {"name": "CONSTRUCTION SITE TWIN", "lat": lat, "lon": lon, "type": "site", "color": [255, 59, 48]},
            {"name": "Metro Transit Hub", "lat": lat + 0.004, "lon": lon - 0.003, "type": "transit", "color": [0, 180, 216]},
            {"name": "Primary Smart School", "lat": lat - 0.003, "lon": lon + 0.004, "type": "school", "color": [0, 245, 212]},
            {"name": "Super-specialty Hospital", "lat": lat + 0.005, "lon": lon + 0.002, "type": "health", "color": [138, 43, 226]},
            {"name": "Green Eco-Park", "lat": lat - 0.004, "lon": lon - 0.005, "type": "leisure", "color": [77, 233, 57]}
        ]
        return pd.DataFrame(data)

    @staticmethod
    def _create_pydeck_map(lat: float, lon: float, df: pd.DataFrame, style: str) -> pdk.Deck:
        # Determine map box visual theme style
        map_style = "mapbox://styles/mapbox/satellite-v9" if "Satellite" in style else "mapbox://styles/mapbox/dark-v11"
        
        # Icon layer mapping
        site_layer = pdk.Layer(
            "ScatterplotLayer",
            df,
            pickable=True,
            opacity=0.9,
            stroked=True,
            filled=True,
            radius_scale=6,
            radius_min_pixels=10,
            radius_max_pixels=100,
            line_width_min_pixels=2,
            get_position="[lon, lat]",
            get_radius=15,
            get_fill_color="color",
            get_line_color=[255, 255, 255]
        )
        
        # Text layer showing labels
        text_layer = pdk.Layer(
            "TextLayer",
            df,
            pickable=False,
            get_position="[lon, lat]",
            get_text="name",
            get_size=12,
            get_color=[255, 255, 255],
            get_alignment_baseline="'bottom'",
            get_pixel_offset="[0, -15]"
        )
        
        view_state = pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=14,
            pitch=45
        )
        
        return pdk.Deck(
            layers=[site_layer, text_layer],
            initial_view_state=view_state,
            map_style=map_style,
            tooltip={"text": "{name}"}
        )
