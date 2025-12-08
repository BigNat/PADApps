# -*- coding: utf-8 -*-
import os
import json
import traceback

from Autodesk.Revit.DB import ElementId, FilteredElementCollector
from Autodesk.Revit.DB import VisibleInViewFilter
from Autodesk.Revit.DB.Plumbing import Pipe
from System.Collections.Generic import List

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def run(uiapp, data, log):
    """
    Fast version:
    - Collect only visible Pipes in the current view
    - Intersect with provided IDs
    - Select instantly
    """
    try:
        uidoc = uiapp.ActiveUIDocument
        doc = uidoc.Document
        view = uidoc.ActiveView
        
        ids = data.get("ids", [])
        if not ids:
            raise Exception("No pipe IDs provided.")

        log("FAST MODE: selecting visible pipes from {0}".format(ids))

        # Convert provided IDs into integer set
        target_ids = set(int(x) for x in ids)

        # Build visibility filter
        vis_filter = VisibleInViewFilter(doc, view.Id)

        # Collect ONLY visible pipes (super fast)
        visible_pipes = FilteredElementCollector(doc, view.Id) \
            .OfClass(Pipe) \
            .WherePasses(vis_filter) \
            .ToElements()

        # Extract only matching IDs
        matching_ids = []
        dotnet_ids = List[ElementId]()

        for p in visible_pipes:
            pid = p.Id.IntegerValue
            if pid in target_ids:
                matching_ids.append(pid)
                dotnet_ids.Add(p.Id)

        # Apply selection
        uidoc.Selection.SetElementIds(dotnet_ids)

        result = {
            "status": "ok",
            "selected_ids": matching_ids,
            "count": len(matching_ids)
        }

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("FAST MODE: selected {0} pipe(s)".format(len(matching_ids)))

    except Exception as e:
        log("FAST ERROR: {0}".format(e))
        log(traceback.format_exc())

        with open(RESPONSE_PATH, "w") as f:
            json.dump({"error": str(e)}, f, indent=2)
