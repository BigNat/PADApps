import json
import time

WATCH = r"C:\PADApps\RevitPAD\Bridge\revit_command.json"

data = {
    "command": "start_watching"
}

with open(WATCH, "w") as f:
    json.dump(data, f, indent=2)

print("Sent command: start_watching")
time.sleep(0.2)
