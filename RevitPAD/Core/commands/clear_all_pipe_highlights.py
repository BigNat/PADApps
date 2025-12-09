# -*- coding: utf-8 -*-
import os
import json
import traceback

import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import ElementId, OverrideGraphicSettings, Transaction
from Autodesk.Revit.DB.Plumbing import Pipe

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def run(uiapp, data, log):
    """
    Removes ALL highlight overrides for ALL pipes visible in the active view.
    """
    try:
        uidoc = uiapp.ActiveUIDocument
        doc = uidoc.Document
        view = uidoc.ActiveView

        log("CLEAR ALL HIGHLIGHTS: scanning active view...")

        collector = DB.FilteredElementCollector(doc, view.Id).OfClass(Pipe)
        pipes = list(collector)

        ogs_clear = OverrideGraphicSettings()

        t = Transaction(doc, "Clear All Pipe Highlights")
        t.Start()

        for p in pipes:
            try:
                view.SetElementOverrides(p.Id, ogs_clear)
            except Exception as inner:
                log(" - ERROR clearing {0}: {1}".format(p.Id.IntegerValue, inner))

        t.Commit()

        result = {
            "status": "ok",
            "cleared_count": len(pipes)
        }

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("CLEAR ALL HIGHLIGHTS: completed for {0} pipes".format(len(pipes)))

    except Exception as e:
        log("Error in clear_all_pipe_highlights: {0}".format(e))
        log(traceback.format_exc())

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        with open(RESPONSE_PATH, "w") as f:
            json.dump({"error": str(e)}, f, indent=2)
