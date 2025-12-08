# -*- coding: utf-8 -*-
import os
import json
import traceback
from Autodesk.Revit.DB import ElementId
from System.Collections.Generic import List

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def run(uiapp, data, log):
    """
    Selects one or more elements in Revit based on a list of element IDs.
    Expected JSON from BlueTree:
    {
        "ids": [123456, 234567, 345678]
    }
    """
    try:
        uidoc = uiapp.ActiveUIDocument
        doc = uidoc.Document

        ids = data.get("ids")

        if not ids or not isinstance(ids, list):
            raise Exception("Missing or invalid 'ids' list for select-elements")

        log("Selecting elements: {}".format(ids))

        # Convert Python list -> .NET List[ElementId]
        dotnet_ids = List[ElementId]()
        for i in ids:
            try:
                eid = ElementId(int(i))
                if doc.GetElement(eid):
                    dotnet_ids.Add(eid)
                    log(" - Valid element selected: {}".format(i))
                else:
                    log(" - WARNING: No element found with ID {}".format(i))
            except Exception as single_e:
                log(" - ERROR converting ID {}: {}".format(i, single_e))

        # Apply selection
        uidoc.Selection.SetElementIds(dotnet_ids)

        result = {
            "status": "ok",
            "selected_ids": ids,
            "count": len(dotnet_ids)
        }

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("Selection applied: {} element(s)".format(len(dotnet_ids)))

    except Exception as e:
        tb = traceback.format_exc()
        log("Error in select_elements: {}".format(e))
        log(tb)

        with open(RESPONSE_PATH, "w") as f:
            json.dump({"error": str(e)}, f, indent=2)
