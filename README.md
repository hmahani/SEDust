# SEDust  

**SEDust** is a Python pipeline for fitting spectral energy distributions (SEDs) of evolved stars using the **DUSTY** radiative transfer code.  
It is designed to estimate **luminosities**, **optical depths**, and **mass-loss rates** for AGB and LPV stars, based on multi-band photometric data.  

---

## ✨ Features
- Fits observed stellar photometry with a pre-computed grid of **60,000 DUSTY models**.  
- Handles both **carbon-rich** and **oxygen-rich** stars.  
- Returns best-fit **SEDs**, **luminosities**, and **mass-loss rates**.  
- Automated pipeline: no trial-and-error fitting required.  
- Higher resolution compared to DESK code.  

---

## 📂 Repository Structure
SEDust/
│── SEDust.py # main pipeline script
│── requirements.txt # Python dependencies
│── README.md # documentation
│── LICENSE # open-source license
│
├── Codes/ # supporting scripts and utilities
├── Grids/ # pre-computed model grids (large files may be external)
└── Inputs/ # example input photometry
