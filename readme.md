# PCB Reverse Engineering CLI

Hello everyone! this is one of my experimental project where im trying to solve a problem where usually requires a lot of manual work which is building a pcb from scratch only with its physical image and converting them into a draft schematic.

my project idea is simple but the implementing the in project is really a headache 

so basically what it does it 2 image [ top and bottom view of the pcb ] is given as input and it gives a rought .kicad_sch file

this project is currently use a 2 layered boards, refer sample board for references

Also this project is still under development phase so consider this as a version 1

# How to run this project

Clone the repository:
```
git clone https://github.com/lucks-13/pcb-rev-eng.git
cd pcb-rev-eng
```
Install the dependencies:
```
pip install -r requirements.txt
```
To run the pipeline:
```
python run_pipeline.py --board sample_board
```
You can also provide custom YOLO weights.
```
python run_pipeline.py --board sample_board --weights file.pt
```
To specify a custom output directory:
```
python run_pipeline.py --board sample_board --out-dir outputs/custom_board
```
To view the component and net summary:
```
python -m src.review_cli --board sample_board --summary
```
To update a component value:
```
python -m src.review_cli --board sample_board --part R1 --value 10k --reexport
```
To update a footprint:
```
python -m src.review_cli --board sample_board --part R1 --footprint 0805 --reexport
```
To rename a component:
```
python -m src.review_cli --board sample_board --part R1 --rename R2 --reexport
```
To approve a reviewed component:
```
python -m src.review_cli --board sample_board --part R1 --approve --reexport
```
# What i learned
* learned Image processing and feature detection using OpenCV
* implemented object detection using yolo
* connected component analysis for copper region extraction
* used graph based connectivity reconstruction using NetworkX

# Ai Disclosure

I used AI alot but not for code generation coz this a very complicated project so technically i cannot build them without using ai { here ai means chatgpt, gemini, claude not ai agent like claude code, codex } so i use ai as learning, I mainly used it to understand image processing techniques, explore PCB reverse engineering approaches and solve some errors and issues inside the code.