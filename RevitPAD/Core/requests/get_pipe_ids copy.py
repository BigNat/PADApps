# -*- coding: utf-8 -*-
import os
import json
import traceback
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType, ISelectionFilter

# Needed to use .NET List for SetElementIds
import clr
clr.AddReference("System")
from System.Collections.Generic import List

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


class PipeSelectionFilter(ISelectionFilter):
    def AllowElement(self, e):
        from Autodesk.Revit.DB.Plumbing import Pipe
        return isinstance(e, Pipe)

    def AllowReference(self, ref, point):
        return True


def write_debug(log, msg):
    try:
        log("[DEBUG get_pipe_ids] " + msg)
    except:
        pass


def run(uiapp, data, log):
    write_debug(log, "=== get_pipe_ids.py START ===")

    uidoc = uiapp.ActiveUIDocument
    doc = uidoc.Document

    try:
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        write_debug(log, "ActiveView: {}".format(uidoc.ActiveView.Name))
        write_debug(log, "About to call PickObjects...")

        # ======================================================================
        # MULTI-SELECTION
        # ======================================================================
        refs = uidoc.Selection.PickObjects(
            ObjectType.Element,
            PipeSelectionFilter(),
            "Select one or more pipes"
        )

        write_debug(log, "PickObjects returned {} references".format(len(refs)))

        pipe_ids = []
        for r in refs:
            try:
                eid = r.ElementId
                el = doc.GetElement(eid)
                if el:
                    pid = el.Id.IntegerValue
                    pipe_ids.append(pid)
                    write_debug(log, "  - Picked Pipe ID: {}".format(pid))
                else:
                    write_debug(log, "  - WARNING: doc.GetElement returned None")
            except Exception as inner_e:
                write_debug(log, "  - ERROR processing reference: {}".format(inner_e))

        # ======================================================================
        # WRITE RESPONSE
        # ======================================================================
        result = {"status": "ok", "pipe_ids": pipe_ids}
        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        write_debug(log, "Response written successfully.")
        write_debug(log, "Pipe IDs: {}".format(pipe_ids))

        # ======================================================================
        # CLEAR REVIT SELECTION
        # ======================================================================
        try:
            empty = List[ElementId]()   # empty .NET list
            uidoc.Selection.SetElementIds(empty)
            write_debug(log, "Revit selection cleared successfully.")
        except Exception as clear_e:
            write_debug(log, "ERROR clearing selection: {}".format(clear_e))

    except Exception as e:
        tb = traceback.format_exc()
        write_debug(log, "EXCEPTION TRIGGERED DURING PICK")
        write_debug(log, "Exception: {}".format(e))
        write_debug(log, "Traceback: {}".format(tb))

        # Write error response
        err = {"error": str(e)}
        with open(RESPONSE_PATH, "w") as f:
            json.dump(err, f, indent=2)

        log("Error in get_pipe_ids: {}".format(e))

    write_debug(log, "=== get_pipe_ids.py END ===")
