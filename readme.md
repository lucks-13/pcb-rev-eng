# PCB Reverse Engineering CLI

Hello everyone! this is one of my experimental project where im trying to solve a problem where usually requires a lot of manual work which is building a pcb from scratch only with its physical image and converting them into a draft schematic.

my project idea is simple but the implementing the in project is really a headache 

so basically what it does it 2 image [ top and bottom view of the pcb ] is given as input and it gives a rought .kicad_sch file 

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
