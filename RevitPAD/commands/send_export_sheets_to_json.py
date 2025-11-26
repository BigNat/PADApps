import json
import time

WATCH = r"C:\PADApps\RevitPAD\Bridge\revit_command.json"

data = {
    "command": "export_sheets_to_json"
}

with open(WATCH, "w") as f:
    json.dump(data, f, indent=2)

print("Sent command: export_sheets_to_json")
time.sleep(0.2)
