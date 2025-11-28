# -*- coding: utf-8 -*-
import os, json, clr
from pyrevit import forms
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    BuiltInCategory,
    ViewSheet,
    DWGExportOptions,
    DXFExportOptions,
    ElementId
)

# Add System.Collections.Generic for List[ElementId]
clr.AddReference("System")
from System.Collections.Generic import List

# --------------------------------------------------------------------------
# RESPONSE PATH
# --------------------------------------------------------------------------
REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def write_response(payload, log):
    """Write response.json for DWG export (success or error)."""
    try:
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
        with open(RESPONSE_PATH, "w") as f:
            json.dump(payload, f, indent=2)
        log("DWG response.json written.")
    except Exception as e:
        log("ERROR writing DWG response.json: {}".format(e))


# --------------------------------------------------------------------------
# MAIN ENTRY POINT
# --------------------------------------------------------------------------
def run(uiapp, data, log):
    """Exports selected Revit sheets to DWG or DXF and writes response.json."""
    try:
        doc = uiapp.ActiveUIDocument.Document

        # Extract parameters
        sheet_ids = data.get("sheet_ids", [])
        cad_format = data.get("cad_format", "dwg").lower()
        export_path = data.get("path", r"C:\PADApps\RevitPAD\ExportsDWG")

        if not os.path.exists(export_path):
            os.makedirs(export_path)

        log("Starting export_sheets_to_cad -> {}".format(export_path))
        log("Format: {} | Sheets: {}".format(cad_format, len(sheet_ids)))

        # Choose export options
        if cad_format == "dxf":
            options = DXFExportOptions()
        else:
            options = DWGExportOptions()

        # Options cleanup & safety
        try: options.ExportViewsAsExternalReferences = False
        except: pass
        try: options.MergedViews = True
        except: pass
        try: options.SharedCoords = False
        except: pass
        try: options.ExportingAreas = False
        except: pass

        # Collect sheets
        all_sheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets)

        if not sheet_ids:
            export_sheets = all_sheets
        else:
            export_sheets = [s for s in all_sheets if s.Id.IntegerValue in sheet_ids]

        if not export_sheets:
            msg = "No matching sheets found for DWG export."
            log(msg)
            write_response({"error": msg}, log)
            return

        exported = []

        # ----------------------------------------------------------------------
        # EXPORT LOOP
        # ----------------------------------------------------------------------
        for sheet in export_sheets:
            try:
                sheetnum = sheet.SheetNumber
                sheetname = sheet.Name

                # Safe filename
                combined = "{}_{}".format(sheetnum, sheetname)
                safe_name = "".join([c for c in combined if c.isalnum() or c in ("_", "-")])

                views = List[ElementId]([sheet.Id])
                result = doc.Export(export_path, safe_name, views, options)

                if result:
                    file_path = os.path.join(export_path, safe_name + "." + cad_format)
                    exported.append(file_path)
                    log("Exported: {}".format(file_path))

            except Exception as e:
                log("Failed to export sheet {}: {}".format(sheet.SheetNumber, e))

        # ----------------------------------------------------------------------
        # WRITE SUCCESS RESPONSE
        # ----------------------------------------------------------------------
        payload = {
            "status": "ok",
            "exported_count": len(exported),
            "exported_files": exported
        }

        write_response(payload, log)
        log("DWG Export complete: {} files".format(len(exported)))

    except Exception as e:
        err = "DWG Export error: {}".format(e)
        log(err)
        write_response({"error": err}, log)
