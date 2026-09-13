from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1]
shutil.copy2(R/"exercise-data"/"exercises.json",R/"frontend"/"data"/"exercises.json")
