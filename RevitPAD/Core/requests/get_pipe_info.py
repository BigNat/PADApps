# -*- coding: utf-8 -*-
import os
import json
import traceback

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ElementId
from Autodesk.Revit.DB.Plumbing import Pipe

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")

FT_TO_MM = 304.8


def mm(val):
    if val is None:
        return None
    return round(val * FT_TO_MM, 3)


def run(uiapp, data, log):
    try:
        uidoc = uiapp.ActiveUIDocument
        doc = uidoc.Document

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        log("Starting get_pipe_info...")

        # ================================================================
        # REQUIRED FIELD: pipe_ids
        # ================================================================
        pipe_ids = data.get("pipe_ids") or []
        if not pipe_ids:
            raise Exception("No pipe IDs provided.")

        log("Received {} pipe IDs".format(len(pipe_ids)))

        pipes_data = []

        # ================================================================
        # ITERATE USING ONLY PROVIDED IDS
        # ================================================================
        for pid in pipe_ids:
            el = doc.GetElement(ElementId(pid))
            if not isinstance(el, Pipe):
                log("Skipping non-pipe element ID: {}".format(pid))
                continue

            log("Processing pipe ID: {}".format(pid))

            # ------------------------------------------------------------
            # GET CONNECTORS (start/end elevations)
            # ------------------------------------------------------------
            conns = el.ConnectorManager.Connectors
            all_conns = [c for c in conns]

            if len(all_conns) < 2:
                log("Pipe {} has <2 connectors. Skipping.".format(pid))
                continue

            start = all_conns[0].Origin
            end = all_conns[1].Origin

            start_z = mm(start.Z)
            end_z = mm(end.Z)

            # ------------------------------------------------------------
            # DIAMETERS
            # ------------------------------------------------------------
            od = idm = wt = None

            p_od = el.LookupParameter("Outside Diameter")
            if p_od:
                od = mm(p_od.AsDouble())

            p_id = el.LookupParameter("Inside Diameter")
            if p_id:
                idm = mm(p_id.AsDouble())

            if od is not None and idm is not None:
                wt = round((od - idm) / 2.0, 3)

            # ------------------------------------------------------------
            # LENGTH
            # ------------------------------------------------------------
            length = None
            p_len = el.LookupParameter("Length")
            if p_len:
                length = mm(p_len.AsDouble())

            # ------------------------------------------------------------
            # SLOPE
            # ------------------------------------------------------------
            slope_percent = None
            if length and length != 0:
                slope_percent = round(((start_z - end_z) / length) * 100, 2)

            # ------------------------------------------------------------
            # SYSTEM INFO
            # ------------------------------------------------------------
            system_type = None
            system_name = None

            if el.MEPSystem:
                system_type = el.MEPSystem.SystemType.ToString()
                system_name = el.MEPSystem.Name

            # ------------------------------------------------------------
            # MATERIAL
            # ------------------------------------------------------------
            material = None
            p_mat = el.LookupParameter("Material")
            if p_mat:
                material = p_mat.AsString()

            # ------------------------------------------------------------
            # STORE RESULT
            # ------------------------------------------------------------
            pipes_data.append({
                "element_id": pid,
                "start_elev_mm": start_z,
                "end_elev_mm": end_z,
                "slope_percent": slope_percent,
                "outside_diameter_mm": od,
                "inside_diameter_mm": idm,
                "wall_thickness_mm": wt,
                "length_mm": length,
                "system_type": system_type,
                "system_name": system_name,
                "material": material,
            })

        # ================================================================
        # WRITE RESULT
        # ================================================================
        result = {"status": "ok", "pipes": pipes_data}

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("Pipe info data written successfully.")
        log("Completed get_pipe_info.")

    except Exception as e:
        log("EXCEPTION in get_pipe_info: {}".format(e))
        log(traceback.format_exc())

        with open(RESPONSE_PATH, "w") as f:
            json.dump({"error": str(e)}, f, indent=2)
