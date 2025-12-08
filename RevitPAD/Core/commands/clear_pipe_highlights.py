# -*- coding: utf-8 -*-
import os
import json
import traceback

import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import ElementId, OverrideGraphicSettings, Transaction

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def run(uiapp, data, log):
    """
    Clears highlight overrides for a list of pipe IDs.
    """
    try:
        uidoc = uiapp.ActiveUIDocument
        doc = uidoc.Document
        view = uidoc.ActiveView

        ids = data.get("ids", [])

        if not ids:
            raise Exception("No pipe IDs provided to clear highlights.")

        log("CLEAR HIGHLIGHT: removing overrides for pipes: {0}".format(ids))

        # Convert to ElementId list
        element_ids = [ElementId(int(x)) for x in ids]

        ogs_clear = OverrideGraphicSettings()

        t = Transaction(doc, "Clear Pipe Highlights")
        t.Start()

        for eid in element_ids:
            try:
                view.SetElementOverrides(eid, ogs_clear)
            except Exception as inner:
                log(" - ERROR clearing {0}: {1}".format(eid.IntegerValue, inner))

        t.Commit()

        # JSON Response
        result = {
            "status": "ok",
            "cleared_ids": ids,
            "count": len(ids)
        }

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("CLEAR HIGHLIGHT: completed for {0} pipe(s)".format(len(ids)))

    except Exception as e:
        log("Error in clear_pipe_highlights: {0}".format(e))
        log(traceback.format_exc())
        with open(RESPONSE_PATH, "w") as f:
            json.dump({"error": str(e)}, f, indent=2)
