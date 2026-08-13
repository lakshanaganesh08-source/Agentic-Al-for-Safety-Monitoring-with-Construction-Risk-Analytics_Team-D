import streamlit as st
import plotly.graph_objects as go
import numpy as np
from ui_components import UIComponents

class HomePage:
    """
    Renders the Home/Hero section of the Construction Intelligence Hub,
    complete with interactive 3D skyscrapers, subtitles, and CTA triggers.
    """
    
    @staticmethod
    def render():
        # Inject standard style components
        UIComponents.get_hero_section()
        
        # Grid layout for 3D model and descriptive cards
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
            UIComponents.render_glass_card(
                """
                <div style='font-size: 1.15rem; line-height: 1.6;'>
                    Welcome to the next generation of civil engineering design and space planning. 
                    The <b>Construction Intelligence Hub</b> harnesses custom deep learning models 
                    and spatial packing algorithms to maximize the utility of your land parcel.
                </div>
                <br>
                <ul style='list-style-type: none; padding-left: 0; line-height: 2;'>
                    <li>🔮 <b>Deep Space Optimization:</b> Automatic zoning of parking, paths, and gardens.</li>
                    <li>📊 <b>Interactive 3D Twins:</b> Render layouts in interactive real-time Plotly models.</li>
                    <li>💰 <b>Predictive Financials:</b> Precision costing models with up to 98% accuracy.</li>
                    <li>🌱 <b>Green Metrics:</b> Sustainability score calculations and eco-friendly recommendations.</li>
                </ul>
                """,
                title="⚡ Next-Gen Spatial Intelligence",
                card_type="purple"
            )
            
            # Big Glowing Start Analysis button
            st.write("")
            if st.button("🚀 Start Spatial Analysis"):
                st.session_state.current_page = "📐 Space Analysis"
                st.rerun()
                
        with col2:
            st.markdown("<h4 style='text-align: center; margin-bottom: 10px; color: #00B4D8 !important;'>📡 Cyber-Physical Building Twin (Interactive)</h4>", unsafe_allow_html=True)
            # Create rotating 3D Building wireframe
            fig = HomePage._create_3d_skyscraper()
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    @staticmethod
    def _create_3d_skyscraper() -> go.Figure:
        """
        Generates a 3D wireframe futuristic skyscraper with surrounding particles
        using Plotly Scatter3d.
        """
        # Define levels for the skyscraper
        levels = 15
        points_per_level = 4
        height_per_level = 2.0
        
        x_lines = []
        y_lines = []
        z_lines = []
        
        # Generate wireframe points
        for i in range(levels):
            # Scale down as we go up (tapered spire look)
            scale = 1.0 - (i / (levels + 5))
            z = i * height_per_level
            
            # Corners of square floor
            corners = [
                (-1 * scale, -1 * scale),
                (1 * scale, -1 * scale),
                (1 * scale, 1 * scale),
                (-1 * scale, 1 * scale),
                (-1 * scale, -1 * scale) # Close loop
            ]
            
            # Add floor lines
            for j in range(len(corners) - 1):
                x_lines.extend([corners[j][0], corners[j+1][0], None])
                y_lines.extend([corners[j][1], corners[j+1][1], None])
                z_lines.extend([z, z, None])
                
            # Vertical column lines connecting to previous level
            if i > 0:
                prev_scale = 1.0 - ((i - 1) / (levels + 5))
                prev_z = (i - 1) * height_per_level
                prev_corners = [
                    (-1 * prev_scale, -1 * prev_scale),
                    (1 * prev_scale, -1 * prev_scale),
                    (1 * prev_scale, 1 * prev_scale),
                    (-1 * prev_scale, 1 * prev_scale)
                ]
                for j in range(4):
                    x_lines.extend([prev_corners[j][0], corners[j][0], None])
                    y_lines.extend([prev_corners[j][1], corners[j][1], None])
                    z_lines.extend([prev_z, z, None])
        
        # Add a high-tech Spire at the top
        top_z = levels * height_per_level
        spire_z = top_z + 8.0
        x_lines.extend([0, 0, None])
        y_lines.extend([0, 0, None])
        z_lines.extend([top_z, spire_z, None])
        
        # Connect spire to top floor corners
        top_scale = 1.0 - ((levels - 1) / (levels + 5))
        top_corners = [
            (-1 * top_scale, -1 * top_scale),
            (1 * top_scale, -1 * top_scale),
            (1 * top_scale, 1 * top_scale),
            (-1 * top_scale, 1 * top_scale)
        ]
        for j in range(4):
            x_lines.extend([top_corners[j][0], 0, None])
            y_lines.extend([top_corners[j][1], 0, None])
            z_lines.extend([top_z, spire_z, None])
            
        # Draw wireframe lines
        wireframe = go.Scatter3d(
            x=x_lines,
            y=y_lines,
            z=z_lines,
            mode='lines',
            line=dict(color='#00B4D8', width=2),
            name='Structural Frame',
            hoverinfo='none'
        )
        
        # Draw core elevator shaft (glowing center column)
        shaft_z = np.linspace(0, top_z, 50)
        shaft_x = np.zeros(50)
        shaft_y = np.zeros(50)
        
        shaft = go.Scatter3d(
            x=shaft_x,
            y=shaft_y,
            z=shaft_z,
            mode='lines',
            line=dict(color='#4D39E9', width=6),
            name='Core Energy Conduit',
            hoverinfo='none'
        )
        
        # Generate floating nodes (particles) around the building
        np.random.seed(42)
        n_particles = 120
        p_theta = np.random.uniform(0, 2*np.pi, n_particles)
        p_r = np.random.uniform(1.5, 4.0, n_particles)
        p_x = p_r * np.cos(p_theta)
        p_y = p_r * np.sin(p_theta)
        p_z = np.random.uniform(0, spire_z, n_particles)
        
        particles = go.Scatter3d(
            x=p_x,
            y=p_y,
            z=p_z,
            mode='markers',
            marker=dict(
                size=np.random.uniform(2, 5, n_particles),
                color=p_z, # Color by height
                colorscale=['#4D39E9', '#00B4D8', '#00F5D4'],
                opacity=0.6
            ),
            name='Sensor Network Nodes',
            hoverinfo='text',
            hovertext=['Telemetry Point' for _ in range(n_particles)]
        )
        
        fig = go.Figure(data=[wireframe, shaft, particles])
        
        # Update layout to be dark themed and transparent background
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            scene=dict(
                xaxis=dict(showbackground=False, visible=False),
                yaxis=dict(showbackground=False, visible=False),
                zaxis=dict(showbackground=False, visible=False),
                camera=dict(
                    eye=dict(x=2.2, y=2.2, z=1.2),
                    up=dict(x=0, y=0, z=1)
                ),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=1.8)
            ),
            showlegend=False,
            height=500
        )
        
        return fig
