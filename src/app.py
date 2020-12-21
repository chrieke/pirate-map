from pathlib import Path
import random
import time

import streamlit as st

from main import render
import SessionState

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

# Buttons
if sec2.button("New Random Map"):
    session.run_id += 1
if sec2.button("Random Settings"):
    t = 1000 * time.time()
    random.seed(int(t))

    random_colors = ["#%06x" % random.randint(0, 0xFFFFFF) for i in range(4)]
    for name, color in zip(DEFAULT_CONFIG.keys(), random_colors):
        DEFAULT_CONFIG[name]["color"] = color

    for name in DEFAULT_CONFIG.keys():
        min = DEFAULT_CONFIG[name]["area"][1]
        max = DEFAULT_CONFIG[name]["area"][2]
        DEFAULT_CONFIG[name]["area"][0] = random.randint(min, max)  # .astype('uint8')


if sec2.button("Reset Settings"):
    pass
seed = session.run_id

# User configuration
layer_config = DEFAULT_CONFIG.copy()
for name, config in DEFAULT_CONFIG.items():
    col1, col2, col3, col4 = st.beta_columns([1, 1, 4, 1])

    # Status
    layer_config[name]["status"] = col1.checkbox(
        name.upper(), value=config["status"], key=name + str(session.run_id)
    )
    # Color
    layer_config[name]["color"] = col2.color_picker(
        label=" ", value=config["color"], key=name + str(session.run_id)
    )
    # Area
    value, min_value, max_value, step = config["area"]
    layer_config[name]["area"] = col3.slider(
        label=" ",
        value=value,
        min_value=min_value,
        max_value=max_value,
        step=step,
        key=name + str(session.run_id),
    )

# Render image
out_dir = Path.cwd().parent / "images"
out_dir.mkdir(parents=True, exist_ok=True)
out_file = str(out_dir / f"out.png")
surface = render(
    layer_config=layer_config,
    seed=seed,
    size=512,
    scale=2,
)
surface.write_to_png(out_file)
sec1.image(out_file, caption="a", use_column_width=True)
