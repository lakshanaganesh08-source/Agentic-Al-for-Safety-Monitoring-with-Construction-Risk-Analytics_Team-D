import plotly.graph_objects as go
import numpy as np

class Visualization3D:
    """
    Renders an interactive 3D digital-twin layout of the optimized land plot,
    including house placements, pathways, gardens, parking zones, and trees.
    """
    
    @staticmethod
    def create_layout_figure(layout: dict, floor_pref: str) -> go.Figure:
        fig = go.Figure()
        
        # Dimensions
        pw, pl = layout["plot_w"], layout["plot_l"]
        hw, hl = layout["house_w"], layout["house_l"]
        hx, hy = layout["house_x"], layout["house_y"]
        
        # House height calculation based on floors
        floors = 1
        if "Duplex" in floor_pref or floor_pref == "Duplex":
            floors = 2
        elif floor_pref == "Triplex":
            floors = 3
        house_h = floors * 10.0 # 10 ft per floor
        
        # 1. LAND PLOT BOUNDARY (Base Plane)
        # Draw a semi-transparent base plane
        x_plot = [-pw/2, pw/2, pw/2, -pw/2, -pw/2]
        y_plot = [-pl/2, -pl/2, pl/2, pl/2, -pl/2]
        z_plot = [0, 0, 0, 0, 0]
        
        fig.add_trace(go.Scatter3d(
            x=x_plot, y=y_plot, z=z_plot,
            mode='lines',
            line=dict(color='#A0AEC0', width=4),
            name='Plot Boundary',
            hoverinfo='text',
            hovertext=f"Total Boundary: {pw:.0f}' x {pl:.0f}'"
        ))
        
        # Plot surface shading
        fig.add_trace(go.Mesh3d(
            x=[-pw/2, pw/2, pw/2, -pw/2],
            y=[-pl/2, -pl/2, pl/2, pl/2],
            z=[0, 0, 0, 0],
            color='rgba(255, 255, 255, 0.02)',
            opacity=0.3,
            hoverinfo='none'
        ))

        # 2. HOUSE PLACEMENT (3D Transparent Prism)
        # Vertices of the house box
        hx_min, hx_max = hx - hw/2, hx + hw/2
        hy_min, hy_max = hy - hl/2, hy + hl/2
        
        # 8 corners of the 3D box
        vertices_x = [hx_min, hx_max, hx_max, hx_min, hx_min, hx_max, hx_max, hx_min]
        vertices_y = [hy_min, hy_min, hy_max, hy_max, hy_min, hy_min, hy_max, hy_max]
        vertices_z = [0, 0, 0, 0, house_h, house_h, house_h, house_h]
        
        # Triangles indices for Mesh3d to build a solid cube
        i_indices = [0, 0, 0, 1, 1, 2, 2, 3, 4, 4, 5, 5]
        j_indices = [1, 2, 4, 2, 5, 3, 6, 7, 5, 6, 6, 7]
        k_indices = [2, 3, 5, 5, 6, 6, 7, 4, 6, 7, 7, 4]
        
        # Solid structure (semi-transparent purple glass)
        fig.add_trace(go.Mesh3d(
            x=vertices_x, y=vertices_y, z=vertices_z,
            i=i_indices, j=j_indices, k=k_indices,
            color='rgba(77, 57, 233, 0.35)',
            flatshading=True,
            name=f"House Structure ({floors} Floors)",
            hoverinfo='text',
            hovertext=f"Built-up footprint: {hw:.1f}' x {hl:.1f}', Height: {house_h}'"
        ))
        
        # Wireframe edges of the house (neon-purple outline)
        # Connect bottom square, top square, and 4 pillars
        house_wire_x = [
            hx_min, hx_max, hx_max, hx_min, hx_min, # bottom square
            hx_min, hx_min, hx_max, hx_max, hx_max, hx_max, hx_min, hx_min, # upper lines
            hx_max, hx_max, hx_min, hx_min, # vertical pillars
        ]
        house_wire_y = [
            hy_min, hy_min, hy_max, hy_max, hy_min,
            hy_min, hy_min, hy_min, hy_min, hy_max, hy_max, hy_max, hy_max,
            hy_max, hy_max, hy_max, hy_max
        ]
        house_wire_z = [
            0, 0, 0, 0, 0,
            house_h, 0, 0, house_h, house_h, 0, 0, house_h,
            house_h, 0, 0, house_h
        ]
        
        fig.add_trace(go.Scatter3d(
            x=house_wire_x, y=house_wire_y, z=house_wire_z,
            mode='lines',
            line=dict(color='#8A2BE2', width=3),
            name='Building Outline',
            hoverinfo='none'
        ))
        
        # Floor divisions indicators
        for f in range(1, floors):
            fz = f * 10.0
            fig.add_trace(go.Scatter3d(
                x=[hx_min, hx_max, hx_max, hx_min, hx_min],
                y=[hy_min, hy_min, hy_max, hy_max, hy_min],
                z=[fz, fz, fz, fz, fz],
                mode='lines',
                line=dict(color='rgba(138, 43, 226, 0.4)', width=1.5, dash='dash'),
                name=f'Floor {f} Slab',
                hoverinfo='none',
                showlegend=False
            ))

        # 3. GARDEN ZONE (Green Surface)
        if layout["garden_w"] > 0:
            gw, gl = layout["garden_w"], layout["garden_l"]
            gx, gy = layout["garden_x"], layout["garden_y"]
            gx_min, gx_max = gx - gw/2, gx + gw/2
            gy_min, gy_max = gy - gl/2, gy + gl/2
            
            fig.add_trace(go.Mesh3d(
                x=[gx_min, gx_max, gx_max, gx_min],
                y=[gy_min, gy_min, gy_max, gy_max],
                z=[0.05, 0.05, 0.05, 0.05], # slightly raised to avoid overlaps
                color='rgba(0, 245, 212, 0.45)',
                name='Landscape Garden',
                hoverinfo='text',
                hovertext=f"Garden Zone: {gw:.0f}' x {gl:.0f}'"
            ))
            # Outline
            fig.add_trace(go.Scatter3d(
                x=[gx_min, gx_max, gx_max, gx_min, gx_min],
                y=[gy_min, gy_min, gy_max, gy_max, gy_min],
                z=[0.05, 0.05, 0.05, 0.05, 0.05],
                mode='lines',
                line=dict(color='#00F5D4', width=2),
                name='Garden Outline',
                hoverinfo='none',
                showlegend=False
            ))

        # 4. PARKING ZONE (Cyan / Blue Surface)
        if layout["parking_w"] > 0:
            pw_k, pl_k = layout["parking_w"], layout["parking_l"]
            px, py = layout["parking_x"], layout["parking_y"]
            px_min, px_max = px - pw_k/2, px + pw_k/2
            py_min, py_max = py - pl_k/2, py + pl_k/2
            
            fig.add_trace(go.Mesh3d(
                x=[px_min, px_max, px_max, px_min],
                y=[py_min, py_min, py_max, py_max],
                z=[0.05, 0.05, 0.05, 0.05],
                color='rgba(0, 180, 216, 0.4)',
                name='Parking Driveway',
                hoverinfo='text',
                hovertext=f"Parking Footprint: {pw_k:.0f}' x {pl_k:.0f}'"
            ))
            # Outline
            fig.add_trace(go.Scatter3d(
                x=[px_min, px_max, px_max, px_min, px_min],
                y=[py_min, py_min, py_max, py_max, py_min],
                z=[0.05, 0.05, 0.05, 0.05, 0.05],
                mode='lines',
                line=dict(color='#00B4D8', width=2),
                name='Parking Outline',
                hoverinfo='none',
                showlegend=False
            ))
            
            # Simple 3D wireframe representing a parked car in the parking spot
            car_cx, car_cy = px, py
            car_w, car_l, car_h = pw_k * 0.6, pl_k * 0.7, 4.0
            ccx_min, ccx_max = car_cx - car_w/2, car_cx + car_w/2
            ccy_min, ccy_max = car_cy - car_l/2, car_cy + car_l/2
            
            fig.add_trace(go.Scatter3d(
                x=[ccx_min, ccx_max, ccx_max, ccx_min, ccx_min, ccx_min, ccx_max, ccx_max, ccx_max, ccx_max, ccx_min, ccx_min, ccx_min, ccx_max, ccx_max, ccx_min, ccx_min],
                y=[ccy_min, ccy_min, ccy_max, ccy_max, ccy_min, ccy_min, ccy_min, ccy_min, ccy_max, ccy_max, ccy_max, ccy_max, ccy_min, ccy_min, ccy_max, ccy_max, ccy_min],
                z=[0.05, 0.05, 0.05, 0.05, 0.05, car_h, car_h, 0.05, 0.05, car_h, car_h, 0.05, 0.05, car_h, car_h, car_h, car_h],
                mode='lines',
                line=dict(color='rgba(255,255,255,0.4)', width=1.5),
                name='Vehicle Envelope',
                hoverinfo='none'
            ))

        # 5. WALKING PATH (Stretched walkway strip)
        path_x = layout["path_x"]
        path_y_start = layout["path_y_start"]
        path_y_end = layout["path_y_end"]
        
        path_w = 4.0 # 4 ft wide path
        
        fig.add_trace(go.Mesh3d(
            x=[path_x - path_w/2, path_x + path_w/2, path_x + path_w/2, path_x - path_w/2],
            y=[path_y_start, path_y_start, path_y_end, path_y_end],
            z=[0.06, 0.06, 0.06, 0.06],
            color='rgba(255, 159, 28, 0.4)',
            name='Pedestrian Access Path',
            hoverinfo='text',
            hovertext="Walkway: Front Entrance to Door"
        ))

        # 6. TREES (Stems + Leaves)
        for idx, tree in enumerate(layout["trees"]):
            tx, ty, tr, th = tree["x"], tree["y"], tree["r"], tree["h"]
            
            # Draw trunk (vertical brown cylinder representation)
            fig.add_trace(go.Scatter3d(
                x=[tx, tx],
                y=[ty, ty],
                z=[0, th * 0.4],
                mode='lines',
                line=dict(color='#8B4513', width=5),
                hoverinfo='none',
                showlegend=False
            ))
            
            # Draw foliage (Green spherical canopy)
            fig.add_trace(go.Scatter3d(
                x=[tx],
                y=[ty],
                z=[th * 0.75],
                mode='markers',
                marker=dict(
                    size=tr * 8, # Scale marker size to represent canopy size
                    color='#00F5D4',
                    opacity=0.85
                ),
                name='Tree / Foliage' if idx == 0 else '',
                hoverinfo='text',
                hovertext=f"Mature Foliage (Radius: {tr} ft, Height: {th} ft)",
                showlegend=(idx == 0)
            ))

        # 7. COMPASS (North Indicator Arrow)
        arrow_x = [pw/2 - pw*0.1, pw/2 - pw*0.1]
        arrow_y = [pl/2 - pl*0.15, pl/2 - pl*0.05]
        arrow_z = [0.1, 0.1]
        
        fig.add_trace(go.Scatter3d(
            x=arrow_x, y=arrow_y, z=arrow_z,
            mode='lines+markers',
            marker=dict(symbol='diamond', size=6, color='#FF3B30'),
            line=dict(color='#FF3B30', width=3),
            name='North Arrow',
            hoverinfo='text',
            hovertext="North orientation guide"
        ))

        # Layout styling (Futuristic black/dark background, no borders)
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            scene=dict(
                xaxis=dict(
                    title="Width (Feet)",
                    backgroundcolor='rgba(0,0,0,0)',
                    gridcolor='rgba(255,255,255,0.05)',
                    showbackground=True,
                    zerolinecolor='rgba(255,255,255,0.1)',
                    color='#A0AEC0'
                ),
                yaxis=dict(
                    title="Length (Feet)",
                    backgroundcolor='rgba(0,0,0,0)',
                    gridcolor='rgba(255,255,255,0.05)',
                    showbackground=True,
                    zerolinecolor='rgba(255,255,255,0.1)',
                    color='#A0AEC0'
                ),
                zaxis=dict(
                    title="Height (Feet)",
                    backgroundcolor='rgba(0,0,0,0)',
                    gridcolor='rgba(255,255,255,0.05)',
                    showbackground=True,
                    zerolinecolor='rgba(255,255,255,0.1)',
                    color='#A0AEC0',
                    range=[0, max(house_h + 5, 20)]
                ),
                camera=dict(
                    eye=dict(x=1.5, y=-1.5, z=1.2),
                    up=dict(x=0, y=0, z=1)
                ),
                aspectmode='data'
            ),
            legend=dict(
                font=dict(color='#E2E8F0'),
                bgcolor='rgba(10, 12, 22, 0.6)',
                bordercolor='rgba(255,255,255,0.1)',
                borderwidth=1,
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            height=600
        )
        
        return fig
