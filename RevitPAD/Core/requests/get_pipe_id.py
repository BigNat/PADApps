# -*- coding: utf-8 -*-
import os
import json
import traceback

from Autodesk.Revit.DB import BuiltInParameter
from Autodesk.Revit.DB.Plumbing import Pipe


REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def run(uiapp, data, log):
    """
    Reads elevation + dimensional data for selected pipes in Revit.
    Writes response.json for BlueTree.
    """

    try:
        uidoc = uiapp.ActiveUIDocument
        doc = uidoc.Document

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        log("Starting get_pipe_elevations...")

        sel_ids = uidoc.Selection.GetElementIds()

        if not sel_ids or len(sel_ids) == 0:
            raise Exception("No pipes selected.")

        log("Selected items: {}".format(len(sel_ids)))

        pipes_data = []

        for eid in sel_ids:
            el = doc.GetElement(eid)

            if not isinstance(el, Pipe):
                log("Skipping non-pipe ID: {}".format(eid.IntegerValue))
                continue

            log("Processing pipe ID: {}".format(eid.IntegerValue))

            # Read parameters safely
            def get_val(bip):
                try:
                    p = el.get_Parameter(bip)
                    if p:
                        return p.AsDouble()
                except:
                    return None

            elev_upper = get_val(BuiltInParameter.RBS_PIPE_UPPEREND_ELEVATION)
            elev_lower = get_val(BuiltInParameter.RBS_PIPE_LOWEREND_ELEVATION)
            cl_upper = get_val(BuiltInParameter.RBS_PIPE_UPPEREND_OFFSET)
            cl_lower = get_val(BuiltInParameter.RBS_PIPE_LOWEREND_OFFSET)

            od = get_val(BuiltInParameter.RBS_PIPE_OUTER_DIAMETER)
            idm = get_val(BuiltInParameter.RBS_PIPE_INNER_DIAMETER)
            wt = get_val(BuiltInParameter.RBS_PIPE_WALL_THICKNESS)
            nom = get_val(BuiltInParameter.RBS_CALCULATED_SIZE)
            length = get_val(BuiltInParameter.CURVE_ELEM_LENGTH)

            pipes_data.append({
                "element_id": eid.IntegerValue,
                "upper_centerline_elev": elev_upper,
                "lower_centerline_elev": elev_lower,
                "upper_centerline_offset": cl_upper,
                "lower_centerline_offset": cl_lower,
                "outside_diameter": od,
                "inside_diameter": idm,
                "wall_thickness": wt,
                "nominal_diameter": nom,
                "length": length
            })

        # Return result
        result = {"status": "ok", "pipes": pipes_data}

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("Pipe elevation data written successfully.")
        log("Completed get_pipe_elevations.")

    except Exception as e:
        log("EXCEPTION in get_pipe_elevations: {}".format(e))
        log(traceback.format_exc())

        with open(RESPONSE_PATH, "w") as f:
            json.dump({"error": str(e)}, f, indent=2)
