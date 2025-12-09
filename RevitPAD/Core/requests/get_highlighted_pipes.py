# -*- coding: utf-8 -*-
import os
import json
import traceback

import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB.Plumbing import Pipe

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def safe_color_tuple(c):
    """
    Safely returns (R,G,B) or None if color is invalid/uninitialized.
    """
    try:
        return (c.Red, c.Green, c.Blue)
    except:
        return None


def run(uiapp, data, log):
    """
    Detects ONLY pipes highlighted using your highlight_pipes_temp overrides.
    """
    try:
        uidoc = uiapp.ActiveUIDocument
        doc = uidoc.Document
        view = uidoc.ActiveView

        log("=== GET HIGHLIGHTED PIPES: START ===")

        highlighted_ids = []

        # Values used by highlight command
        HL_LINE_COLOR = (255, 0, 0)
        HL_SURF_COLOR = (255, 200, 200)
        HL_LINE_WEIGHT = 10

        collector = DB.FilteredElementCollector(doc, view.Id).OfClass(Pipe)

        for p in collector:
            eid = p.Id
            ogs = view.GetElementOverrides(eid)

            # Extract overrides safely
            proj_color = safe_color_tuple(ogs.ProjectionLineColor)
            surf_color = safe_color_tuple(ogs.SurfaceForegroundPatternColor)
            lw = ogs.ProjectionLineWeight

            # A pipe is highlighted if ANY of the applied override values match
            is_highlighted = False

            if proj_color == HL_LINE_COLOR:
                is_highlighted = True

            if surf_color == HL_SURF_COLOR:
                is_highlighted = True

            if lw == HL_LINE_WEIGHT:
                is_highlighted = True

            if is_highlighted:
                highlighted_ids.append(eid.IntegerValue)

            # DEBUG LOGGING
            log("Pipe {0} → proj:{1} surf:{2} lw:{3} highlighted:{4}"
                .format(eid.IntegerValue, proj_color, surf_color, lw, is_highlighted))

        # Output result JSON
        result = {
            "status": "ok",
            "highlighted_ids": highlighted_ids,
            "count": len(highlighted_ids)
        }

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("=== GET HIGHLIGHTED PIPES: FOUND {0} ===".format(len(highlighted_ids)))

    except Exception as e:
        log("Error in get_highlighted_pipes: {0}".format(e))
        log(traceback.format_exc())
        try:
            with open(RESPONSE_PATH, "w") as f:
                json.dump({"error": str(e)}, f, indent=2)
        except:
            pass
