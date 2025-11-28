# -*- coding: utf-8 -*-
import os, json, clr
from pyrevit import forms
from Autodesk.Revit.DB import View
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    BuiltInCategory,
    ElementId,
    NavisworksExportOptions,
    NavisworksExportScope,
    NavisworksCoordinates
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
    """Write response.json for NWC export (success or error)."""
    try:
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
        with open(RESPONSE_PATH, "w") as f:
            json.dump(payload, f, indent=2)
        log("NWC response.json written.")
    except Exception as e:
        log("ERROR writing NWC response.json: {}".format(e))


# --------------------------------------------------------------------------
# MAIN ENTRY POINT
# --------------------------------------------------------------------------
def run(uiapp, data, log):
    """Exports selected Revit views to NWC and writes response.json."""
    try:
        doc = uiapp.ActiveUIDocument.Document

        # Extract parameters
        view_ids = data.get("view_ids", [])
        export_path = data.get("path", r"C:\PADApps\RevitPAD\ExportsNWC")

        if not os.path.exists(export_path):
            os.makedirs(export_path)

        log("Starting export_views_to_nwc -> {}".format(export_path))
        log("Views: {}".format(len(view_ids)))

        # Collect all views
        all_views = FilteredElementCollector(doc).OfClass(View)


        if not view_ids:
            export_views = all_views
        else:
            export_views = [v for v in all_views if v.Id.IntegerValue in view_ids]

        if not export_views:
            msg = "No matching views found for NWC export."
            log(msg)
            write_response({"error": msg}, log)
            return

        exported = []

        # ----------------------------------------------------------------------
        # EXPORT LOOP
        # ----------------------------------------------------------------------
        for view in export_views:
            try:
                viewname = view.Name
                viewnum = view.Id.IntegerValue

                # Safe filename
                combined = "{}_{}".format(viewnum, viewname)
                safe_name = "".join([c for c in combined if c.isalnum() or c in ("_", "-")])

                # Options
                options = NavisworksExportOptions()
                options.ExportScope = NavisworksExportScope.View
                options.ViewId = view.Id
                options.Coordinates = NavisworksCoordinates.Shared

                try:
                    options.ExportLinks = True
                except:
                    pass

                # Export → always add .nwc suffix
                result = doc.Export(export_path, safe_name, options)

                file_path = os.path.join(export_path, safe_name + ".nwc")

                # Navisworks exporter often returns False even on success, so check file existence
                if os.path.exists(file_path):
                    exported.append(file_path)
                    log("Exported: {}".format(file_path))
                else:
                    log("⚠️ Export reported failure (return=False) but file not found.")

            except Exception as e:
                log("Failed to export view {}: {}".format(view.Id.IntegerValue, e))

        # ----------------------------------------------------------------------
        # WRITE SUCCESS RESPONSE
        # ----------------------------------------------------------------------
        payload = {
            "status": "ok",
            "exported_count": len(exported),
            "exported_files": exported
        }

        write_response(payload, log)
        log("NWC Export complete: {} files".format(len(exported)))

    except Exception as e:
        err = "NWC Export error: {}".format(e)
        log(err)
        write_response({"error": err}, log)
