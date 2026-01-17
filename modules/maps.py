import folium
from modules.utils import haversine_km

def build_map(center_lat=24.7136, center_lon=46.6753, zoom=6, clicked=None, deal_points=None):
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, control_scale=True)

    if clicked:
        folium.Marker([clicked[0], clicked[1]], tooltip="موقع التقييم", icon=folium.Icon(color="red")).add_to(m)

    if deal_points:
        for d in deal_points:
            if d.get("lat") is None or d.get("lon") is None:
                continue
            tip = f"صفقة: {d.get('annual_rent',0):,.0f} ريال | {d.get('area_m2',0):,.0f} م² | {d.get('year','')}"
            folium.CircleMarker(
                [d["lat"], d["lon"]],
                radius=6,
                tooltip=tip,
                fill=True
            ).add_to(m)

    return m
