# -*- coding: utf-8 -*-
import os
import json
import traceback

from Autodesk.Revit.DB import Transaction, ElementId
from Autodesk.Revit.DB.Plumbing import Pipe

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")

MM_TO_FT = 1.0 / 304.8      # mm → feet
FT_TO_MM = 304.8            # feet → mm


def to_ft(val):
    if val is None:
        return None
    return float(val) * MM_TO_FT


def to_mm(val):
    if val is None:
        return None
    return round(val * FT_TO_MM, 3)


def run(uiapp, data, log):
    try:
        uidoc = uiapp.ActiveUIDocument
        doc = uidoc.Document

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        log("=== set_pipe_il.py START ===")

        pipe_id = data.get("pipe_id")
        if not pipe_id:
            raise Exception("No pipe_id provided.")

        # incoming mm values from BlueTree
        il_lower_mm_in = data.get("il_lower_mm")
        il_upper_mm_in = data.get("il_upper_mm")
        h_lower_mm_in = data.get("il_height_lower_mm")
        h_upper_mm_in = data.get("il_height_upper_mm")
        floor_rl_mm_in = data.get("floor_rl_below")

        # convert inputs to feet for Revit
        il_lower_ft = to_ft(il_lower_mm_in)
        il_upper_ft = to_ft(il_upper_mm_in)
        h_lower_ft = to_ft(h_lower_mm_in)
        h_upper_ft = to_ft(h_upper_mm_in)
        floor_rl_ft = to_ft(floor_rl_mm_in)

        log("Updating IL parameters for pipe {}...".format(pipe_id))

        el = doc.GetElement(ElementId(int(pipe_id)))
        if not isinstance(el, Pipe):
            raise Exception("Element {} is not a Pipe.".format(pipe_id))

        applied_feet = {}   # track feet values internally

        t = Transaction(doc, "Set IL Parameters")
        t.Start()

        def set_param(name, ft_value):
            if ft_value is None:
                return
            p = el.LookupParameter(name)
            if p:
                p.Set(ft_value)
                applied_feet[name] = ft_value
                log("Set {} (ft) = {}".format(name, ft_value))
            else:
                log("Parameter '{}' not found.".format(name))

        # update in Revit
        set_param("IL Lower", il_lower_ft)
        set_param("IL Upper", il_upper_ft)
        set_param("IL Height Lower", h_lower_ft)
        set_param("IL Height Upper", h_upper_ft)
        set_param("Floor RL Below", floor_rl_ft)

        t.Commit()

        # Convert all applied feet → mm for return result
        applied_mm = {name: to_mm(val) for name, val in applied_feet.items()}

        result = {
            "status": "ok",
            "pipe_id": int(pipe_id),
            "message": "IL update confirmed",
            "applied_mm": applied_mm
        }

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("IL update completed and confirmed for pipe {}.".format(pipe_id))
        log("=== set_pipe_il.py END ===")

    except Exception as e:
        log("EXCEPTION: {}".format(e))
        log(traceback.format_exc())

        with open(RESPONSE_PATH, "w") as f:
            json.dump({"error": str(e)}, f, indent=2)
