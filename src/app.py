from pathlib import Path
import streamlit as st

from main import render
# value, min, max,
DEFAULT_CONFIG = {
    "water": {"status": True, "area": [-4, -50, 5, 1], "color": "#2185C5"},
    "sand": {"status": True, "area": [-4, -40, 5, 1], "color": "#FFFFA6"},
    "grass": {"status": True, "area": [-8, -40, 5, 1], "color": "#BDF271"},
    "gravel": {"status": True, "area": [-10, -20, 5, 1], "color": "#CFC291"},
}

# st.set_page_config(layout="wide")
st.title("Pirate Map")
sec1, sec2 = st.beta_columns([2, 1])
session = SessionState.get(
    run_id=0
)  # see https://gist.github.com/tvst/036da038ab3e999a64497f42de966a92

display_which = st.radio(
    "Display", options=["Sand", "Grass", "Gravel"], key="display_which"
)

sand, grass, gravel = {}, {}, {}

sand["area"] = st.slider(
    "Sand", value=-4, min_value=-50, max_value=10, step=1, key="sand_area"
)

grass["area"] = st.slider(
    "Grass", value=-8, min_value=-50, max_value=10, step=1, key="grass_area"
)

gravel["area"] = st.slider(
    "Gravel", value=-12, min_value=-10, max_value=10, step=1, key="gravel_area"
)
gravel["color"] = st.color_picker("Gravel Color", label="#CFC291")

for seed in range(2):
    print(seed)

    out_dir = Path.cwd().parent / "images"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_file = str(out_dir / f"out{seed}.png")

    surface = render(
        seed,
        size=512,
        scale=2,
        display_which=display_which,
        sand=sand,
        grass=grass,
        gravel=gravel,
    )
    surface.write_to_png(out_file)

    st.image(out_file, caption=seed, width=400)
