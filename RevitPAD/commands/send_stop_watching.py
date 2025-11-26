import json
import time

WATCH = r"C:\PADApps\RevitPAD\Bridge\revit_command.json"

data = {
    "command": "test_command"
}

with open(WATCH, "w") as f:
    json.dump(data, f, indent=2)

print("Sent command: test_command")
time.sleep(0.2)
