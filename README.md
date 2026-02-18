# 🔥 PixelForge — Image Art Studio

**Transform any photo into stunning art styles — powered entirely by Python open-source packages.**

> *No AI APIs. No accounts. No cost. Pure Python open-source.*

Created by **[Economic Integrity LLC](https://github.com/EconomicIntegrityLLC)**

---

## What Is PixelForge?

PixelForge is a free, browser-based image art studio built with [Streamlit](https://streamlit.io). Upload any photo — or snap a selfie right in the browser — and instantly transform it into six distinct art styles. Every effect is generated with pure Python math (no ML models, no GPU, no API keys), so it runs fast on any machine and deploys free on Streamlit Community Cloud.

The project was inspired by the incredible ecosystem catalogued in [Awesome Python](https://github.com/vinta/awesome-python), and deliberately combines packages from **five different categories** to demonstrate the power of open-source convergence.

---

## Art Styles

| Style | What It Does | Key Tech |
|---|---|---|
| 🟩 **Pixel Art** | Retro game-style pixelation with adjustable block size and colour quantisation | Pillow colour quantise + nearest-neighbour upscale |
| 📝 **ASCII Art** | Renders your image entirely in text characters (4 character sets including Unicode blocks) | NumPy brightness mapping to character arrays |
| ✏️ **Sketch** | Pencil-drawing effect with tunable smoothing | scikit-image Canny edge detection |
| 🔲 **Quadtree** | Recursive geometric decomposition — low-detail areas become large blocks, high-detail areas split finer | Custom recursive subdivision with variance thresholding |
| 🎨 **Pop Art** | Bold posterised colours with saturation boost — Andy Warhol vibes | NumPy colour-depth reduction + Pillow `ImageEnhance` |
| 🎯 **Colour Palette** | Extracts dominant colours, displays swatches with hex codes, and charts the distribution | Pillow median-cut quantisation + Plotly bar chart |

---

## Features

- **Camera selfie input** — snap a photo directly in the browser via `st.camera_input()`
- **Interactive controls** — every effect has sliders and toggles for real-time parameter tuning
- **Instant download** — every output is downloadable as PNG or TXT with one click
- **Responsive layout** — adapts to desktop, tablet, and mobile screen sizes
- **Lightweight** — no GPU, no ML models, runs fast on Streamlit Community Cloud free tier
- **No external APIs** — zero network calls, zero API keys, 100% self-contained

---

## Powered By

Built with tools from [Awesome Python](https://github.com/vinta/awesome-python) spanning **5 different categories**:

| Package | Awesome Python Category | Role in PixelForge |
|---|---|---|
| [Streamlit](https://streamlit.io) | Admin Panels | App framework, UI, camera input |
| [Pillow](https://python-pillow.org/) | Image Processing | Core image manipulation, colour quantisation |
| [scikit-image](https://scikit-image.org/) | Image Processing | Canny edge detection for sketch effects |
| [NumPy](https://numpy.org/) | Science | Fast array math powering all transforms |
| [Plotly](https://plotly.com/python/) | Data Visualization | Interactive colour palette distribution charts |
| [pyfiglet](https://github.com/pwaller/pyfiglet) | Text Processing | ASCII banner text on the landing page |

---

## Quick Start

### Run Locally

```bash
# Clone the repo
git clone https://github.com/EconomicIntegrityLLC/pixelforge.git
cd pixelforge

# Install dependencies
pip install -r requirements.txt

# Launch
streamlit run app.py
```

The app opens at [http://localhost:8501](http://localhost:8501).

### Deploy to Streamlit Community Cloud

1. Fork or clone this repo to your own **public** GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"** → select your repo → set main file to `app.py`
4. Click **Deploy** — your app will be live in minutes

---

## Project Structure

```
pixelforge/
├── app.py              # Streamlit UI — branding, sidebar, tabs, controls, downloads
├── transforms.py       # Image transformation engine (6 effects)
├── requirements.txt    # Python dependencies
├── assets/
│   └── logo.png        # Economic Integrity LLC logo
└── README.md           # You are here
```

---

## Usage & Attribution

### Free to Use

This project is **free and open-source** under the MIT License. You are welcome to:

- Use it for personal or commercial projects
- Fork it and build on top of it
- Deploy your own instance
- Learn from the code and adapt techniques

### Please Credit Us

If you use PixelForge or any of its code in your own project, we kindly ask that you **include an attribution** to:

> **Economic Integrity LLC**
> [https://github.com/EconomicIntegrityLLC](https://github.com/EconomicIntegrityLLC)

A simple mention in your README, about page, or footer is all we ask. For example:

```
Based on PixelForge by Economic Integrity LLC
https://github.com/EconomicIntegrityLLC/pixelforge
```

---

## Requirements

- Python 3.10+
- See `requirements.txt` for the full dependency list:
  - `streamlit`
  - `Pillow`
  - `numpy`
  - `scikit-image`
  - `plotly`
  - `pyfiglet`

---

## Contributing

Contributions are welcome! If you'd like to add a new art style, improve the UI, or fix a bug:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-new-effect`)
3. Commit your changes
4. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

**TL;DR:** Do whatever you want with it, but please reference **Economic Integrity LLC**.

---

<p align="center">
  <b>Built with ❤️ by <a href="https://github.com/EconomicIntegrityLLC">Economic Integrity LLC</a></b><br>
  Powered by the <a href="https://github.com/vinta/awesome-python">Awesome Python</a> open-source ecosystem
</p>
