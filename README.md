# ORCA Input Builder (GUI)

by Gabriel Monteiro de Castro.

## Description
A graphical tool for generating ORCA input files with ease.  
This application provides a user-friendly Tkinter interface to configure common job types, methods, basis sets, solvents, and advanced keywords for ORCA quantum chemistry calculations. It also includes a live preview of the generated input file.

## Purpose:
Developed as a personal project to support research in computational chemistry.

## Features
- Select common **job types** (SP, OPT, FREQ, TD-DFT, etc.)
- Choose from popular **DFT methods** and **basis sets**
- Built-in **solvent selection** for CPCM/SMD
- Toggle common **keywords & corrections** (TightSCF, D3BJ, RIJCOSX, etc.)
- Define **resources**: processors, memory (MaxCore)
- Import molecular **coordinates** (XYZ/PDB) or paste manually
- Add **custom blocks** (`%... end`) and custom keywords
- Live **preview panel** with lock/unlock, copy-to-clipboard, and word wrap
- Save inputs as `.inp` files
- Load and save templates for reuse

## Usage
Run the script with: python ORCA-Input-Builder.py

## Contributing
Suggestions are welcome! Feel free to use my repositories and improve them.

---
