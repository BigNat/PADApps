# -*- coding: utf-8 -*-
import os
import json
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ISelectionFilter, ObjectType

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


class PipeSelectionFilter(ISelectionFilter):
    def AllowElement(self, e):
        # Plumbing Pipe type (Revit API)
        from Autodesk.Revit.DB.Plumbing import Pipe
        return isinstance(e, Pipe)

    def AllowReference(self, ref, point):
        return True


def run(uiapp, data, log):
    """
    Allows user to select a pipe in Revit and returns its ElementId.
    Writes response.json for BlueTree to read.
    """
    try:
        uidoc = uiapp.ActiveUIDocument
        doc = uidoc.Document

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        log("Awaiting pipe selection...")

        # Prompt user
        ref = uidoc.Selection.PickObject(
            ObjectType.Element,
            PipeSelectionFilter(),
            "Select a pipe"
        )

        el = doc.GetElement(ref.ElementId)
        pid = el.Id.IntegerValue

        result = {
            "status": "ok",
            "pipe_id": pid
        }

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("Pipe selected → ID: {}".format(pid))

    except Exception as e:
        err = {"error": str(e)}
        with open(RESPONSE_PATH, "w") as f:
            json.dump(err, f, indent=2)
        log("Error in get_pipe_id: {}".format(e))
