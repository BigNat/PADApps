# -*- coding: utf-8 -*-
import os
import json
import traceback

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
            # 4. SLOPE (%) (2 decimals)
            # ------------------------------------------------------------
            slope_percent = None
            if length and length != 0:
                slope_percent = round(((start_z - end_z) / length) * 100, 2)

            # ------------------------------------------------------------
            # 5. SYSTEM TYPE / SYSTEM NAME
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
            # 7. REFERENCE LEVEL + LEVEL RL
            # ------------------------------------------------------------
            reference_level_name = None
            reference_level_rl_mm = None

            ref_level = el.ReferenceLevel

            if ref_level:
                reference_level_name = ref_level.Name
                reference_level_rl_mm = mm(ref_level.Elevation)

            # ------------------------------------------------------------
            # 8. INVERT PARAMETERS (Plumbing)
            # ------------------------------------------------------------
            il_lower = None
            p_il_lower = el.LookupParameter("IL Lower")
            if p_il_lower:
                il_lower = mm(p_il_lower.AsDouble())

            il_upper = None
            p_il_upper = el.LookupParameter("IL Upper")
            if p_il_upper:
                il_upper = mm(p_il_upper.AsDouble())

            il_height_lower = None
            p_il_height_lower = el.LookupParameter("IL Height Lower")
            if p_il_height_lower:
                il_height_lower = mm(p_il_height_lower.AsDouble())

            il_height_upper = None
            p_il_height_upper = el.LookupParameter("IL Height Upper")
            if p_il_height_upper:
                il_height_upper = mm(p_il_height_upper.AsDouble())

            floor_rl_below = None
            p_floor_rl_below = el.LookupParameter("Floor RL Below")
            if p_floor_rl_below:
                floor_rl_below = mm(p_floor_rl_below.AsDouble())

            # ------------------------------------------------------------
            # STORE RESULT
            # ------------------------------------------------------------
            pipes_data.append({
                "element_id": eid.IntegerValue,
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
                "reference_level_name": reference_level_name,
                "reference_level_rl_mm": reference_level_rl_mm,

                # NEW IL FIELDS
                "il_lower_mm": il_lower,
                "il_upper_mm": il_upper,
                "il_height_lower_mm": il_height_lower,
                "il_height_upper_mm": il_height_upper,
                "floor_rl_below_mm": floor_rl_below
            })

        # ------------------------------------------------------------
        # WRITE RESULT
        # ------------------------------------------------------------
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
