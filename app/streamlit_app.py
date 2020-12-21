from pathlib import Path
import random
import time

import streamlit as st

from PirateMap.main import render
import SessionState


SKULL_EMOJI_URL = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/twitter/259/pirate-flag_1f3f4-200d-2620-fe0f.png"
# value, min, max, step
DEFAULT_CONFIG = {
    "sand": {"area": [-4, -30, 5, 1], "color": "#FFFFA6"},
    "grass": {"area": [-8, -40, 5, 1], "color": "#BDF271"},
    "gravel": {"area": [-10, -20, 0, 1], "color": "#CFC291"},
}

# PAGE
st.set_page_config(
    page_title="Pirate Map", page_icon=SKULL_EMOJI_URL, initial_sidebar_state="auto"
)
st.title("🏴‍☠️ Pirate Map")
st.write("Generate random treasure maps. Customize layer settings in the sidebar.")
st.markdown("<br>", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.markdown(
    """
# Map Settings
<br>

""",
    unsafe_allow_html=True,
)

# PAGE BUTTONS
session = SessionState.get(
    run_id=0
)  # see https://gist.github.com/tvst/036da038ab3e999a64497f42de966a92
if st.button("🔄 New Random Map"):
    session.run_id += 1
container1 = st.beta_container()

# SIDEBAR BUTTONS
col_reset, col_random = st.sidebar.beta_columns([2, 3])
if col_random.button("⚙️ Random Size"):
    t = 1000 * time.time()
    random.seed(int(t))
    for name in DEFAULT_CONFIG.keys():
        min = DEFAULT_CONFIG[name]["area"][1]
        max = DEFAULT_CONFIG[name]["area"][2]
        DEFAULT_CONFIG[name]["area"][0] = random.randint(min, max)
if col_reset.button("❎ Reset"):
    layer_config = DEFAULT_CONFIG.copy()
seed = session.run_id

# SIDEBAR SETTINGS
st.sidebar.markdown("-----------------")
layer_config = DEFAULT_CONFIG.copy()
for name, config in DEFAULT_CONFIG.items():
    col1, col2, col3 = st.sidebar.beta_columns([2, 2, 3])
    # Name
    col1.write(name.capitalize(), key=name + str(session.run_id))
    # Color
    layer_config[name]["color"] = col2.color_picker(
        label=" ", value=config["color"], key=name + str(session.run_id)
    )
    # Area size
    value, min_value, max_value, step = config["area"]
    layer_config[name]["area"] = value
    layer_config[name]["area"] = col3.slider(
        label=" ",
        value=value,
        min_value=min_value,
        max_value=max_value,
        step=step,
        key=name + str(session.run_id),
    )

st.sidebar.markdown(
    """
------------
The map visualization is using [PirateMap](https://github.com/fogleman/PirateMap) by [fogleman](https://github.com/fogleman).

Explore the streamlit app code in [pirate-map](https://github.com/chrieke/pirate-map) by [chrieke](https://github.com/chrieke).

[![Star](https://img.shields.io/github/stars/chrieke/pirate-map.svg?label=Star&logo=github&style=social)](https://gitHub.com/jrieke/traingenerator/stargazers)
&nbsp[![Follow](https://img.shields.io/twitter/follow/chrieke?style=social)](https://www.twitter.com/chrieke)
""",
    unsafe_allow_html=True,
)

# RENDER IMAGE
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
container1.image(out_file, caption=" ", width=650)
