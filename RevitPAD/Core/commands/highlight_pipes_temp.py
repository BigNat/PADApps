# -*- coding: utf-8 -*-
import os
import json
import traceback

import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import ElementId, OverrideGraphicSettings, Color, Transaction


REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def run(uiapp, data, log):
    """
    Highlights pipes using view overrides.
    Requires a transaction in Revit 2020–2024.
    """
    try:
        uidoc = uiapp.ActiveUIDocument
        doc = uidoc.Document
        view = uidoc.ActiveView

        ids = data.get("ids", [])
        if not ids:
            raise Exception("No pipe IDs provided to highlight.")

        log("HIGHLIGHT: Applying view overrides to pipes: {0}".format(ids))

        element_ids = [ElementId(int(x)) for x in ids]

        # Highlight graphics
        ogs = OverrideGraphicSettings()
        ogs.SetProjectionLineColor(Color(255, 0, 0))
        ogs.SetProjectionLineWeight(10)
        ogs.SetSurfaceForegroundPatternColor(Color(255, 200, 200))

        # OPEN TRANSACTION
        t = Transaction(doc, "Highlight Pipes")
        t.Start()

        for eid in element_ids:
            try:
                view.SetElementOverrides(eid, ogs)
            except Exception as inner_e:
                log(" - ERROR highlight {0}: {1}".format(eid.IntegerValue, inner_e))

        t.Commit()

        # RESULT JSON
        result = {
            "status": "ok",
            "highlighted_ids": ids,
            "count": len(ids)
        }

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("HIGHLIGHT: Completed for {0} pipe(s)".format(len(ids)))

    except Exception as e:
        log("Error in highlight_pipes_temp: {0}".format(e))
        log(traceback.format_exc())
        with open(RESPONSE_PATH, "w") as f:
            json.dump({"error": str(e)}, f, indent=2)
