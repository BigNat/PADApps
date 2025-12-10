# -*- coding: utf-8 -*-
import os
import json
import traceback

from Autodesk.Revit.DB import (
    FilteredElementCollector,
    VisibleInViewFilter,
    BuiltInCategory
)
from Autodesk.Revit.DB.Plumbing import Pipe

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")

FT_TO_MM = 304.8   # Revit internal → mm


def mm(val):
    """Convert feet → mm with 3-decimal rounding."""
    if val is None:
        return None
    return round(val * FT_TO_MM, 3)


def run(uiapp, data, log):
    try:
        uidoc = uiapp.ActiveUIDocument
        doc = uidoc.Document
        view = uidoc.ActiveView

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        log("Starting get_pipe_info...")

        # ================================================================
        # MODE SELECTION
        # ================================================================
        mode = data.get("mode", "selected")  # "selected" or "all_in_view"
        pipes_data = []
        pipe_elements = []

        # ---------------------------------------------------------------
        # MODE 1 — GET ALL VISIBLE PIPES IN VIEW
        # ---------------------------------------------------------------
        if mode == "all_in_view":
            log("Collecting ALL visible pipes in current view...")

            vis_filter = VisibleInViewFilter(doc, view.Id)

            pipe_elements = (
                FilteredElementCollector(doc, view.Id)
                .OfCategory(BuiltInCategory.OST_PipeCurves)
                .WherePasses(vis_filter)
                .ToElements()
            )

            log("Found {} visible pipes.".format(len(pipe_elements)))

        # ---------------------------------------------------------------
        # MODE 2 — GET SELECTED PIPES (original behavior)
        # ---------------------------------------------------------------
        else:
            sel_ids = uidoc.Selection.GetElementIds()
            if not sel_ids or len(sel_ids) == 0:
                raise Exception("No pipes selected.")

            log("Selected items: {}".format(len(sel_ids)))
            pipe_elements = [doc.GetElement(x) for x in sel_ids]

        # ================================================================
        # ITERATE AND EXTRACT PIPE DATA
        # ================================================================
        for el in pipe_elements:
            if not isinstance(el, Pipe):
                continue

            eid = el.Id.IntegerValue
            log("Processing pipe ID: {}".format(eid))

            # ------------------------------------------------------------
            # 1. GEOMETRIC START/END ELEVATIONS
            # ------------------------------------------------------------
            conns = el.ConnectorManager.Connectors
            all_conns = [c for c in conns]

            if len(all_conns) < 2:
                log("Pipe has <2 connectors. Skipping.")
                continue

            start = all_conns[0].Origin
            end = all_conns[1].Origin

            start_z = mm(start.Z)
            end_z = mm(end.Z)

            # ------------------------------------------------------------
            # 2. DIAMETERS
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
            # 3. LENGTH (mm)
            # ------------------------------------------------------------
            length = None
            p_len = el.LookupParameter("Length")
            if p_len:
                length = mm(p_len.AsDouble())

            # ------------------------------------------------------------
            # 4. SLOPE (%)
            # ------------------------------------------------------------
            slope_percent = None
            if length and length != 0:
                slope_percent = round(((start_z - end_z) / length) * 100, 2)

            # ------------------------------------------------------------
            # 5. SYSTEM TYPE / NAME
            # ------------------------------------------------------------
            system_type = None
            system_name = None
            if el.MEPSystem:
                system_type = el.MEPSystem.SystemType.ToString()
                system_name = el.MEPSystem.Name

            # ------------------------------------------------------------
            # 6. MATERIAL
            # ------------------------------------------------------------
            material = None
            p_mat = el.LookupParameter("Material")
            if p_mat:
                material = p_mat.AsString()

            # ------------------------------------------------------------
            # STORE RESULT
            # ------------------------------------------------------------
            pipes_data.append({
                "element_id": eid,
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
