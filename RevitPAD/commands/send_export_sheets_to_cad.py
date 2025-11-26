import json
import time

WATCH = r"C:\PADApps\RevitPAD\Bridge\revit_command.json"

data = {
    "command": "export_sheets_to_cad",
    "sheet_ids": [359502, 842837],
    "cad_format": "dwg",
    "path": r"C:\PADApps\RevitPAD\Exports"
}

with open(WATCH, "w") as f:
    json.dump(data, f, indent=2)

print("Sent command: export_sheets_to_cad")
time.sleep(0.2)
