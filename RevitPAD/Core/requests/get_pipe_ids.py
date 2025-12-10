# -*- coding: utf-8 -*-
import os
import json
import traceback

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType, ISelectionFilter
from Autodesk.Revit.DB.Plumbing import Pipe

import clr
clr.AddReference("System")
from System.Collections.Generic import List

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


# ----------------------------------------------------------------------
# Canonical Mode Values (must match Python enum values)
# ----------------------------------------------------------------------
MODE_PICK = "pick"
MODE_SELECTED = "selected"
MODE_VISIBLE_IN_VIEW = "visible_in_view"
MODE_ALL_IN_MODEL = "all_in_model"
MODE_TAGGED = "tagged"
MODE_PROVIDED = "provided"


# ----------------------------------------------------------------------
# Logging helpers
# ----------------------------------------------------------------------
def log_debug(log, msg):
    try:
        log("[DEBUG get_pipe_ids] " + msg)
    except:
        pass


def write_response(result):
    with open(RESPONSE_PATH, "w") as f:
        json.dump(result, f, indent=2)


# ----------------------------------------------------------------------
# Selection filter for Pick mode
# ----------------------------------------------------------------------
class PipeSelectionFilter(ISelectionFilter):
    def AllowElement(self, e):
        return isinstance(e, Pipe)

    def AllowReference(self, ref, point):
        return True


# ----------------------------------------------------------------------
# Mode implementations
# ----------------------------------------------------------------------
def collect_pick(uidoc, log):
    log_debug(log, "Mode = PICK")
    try:
        refs = uidoc.Selection.PickObjects(
            ObjectType.Element,
            PipeSelectionFilter(),
            "Select one or more pipes"
        )
    except Exception as e:
        log_debug(log, "PickObjects cancelled or failed: {}".format(e))
        return []

    pipe_ids = []
    for r in refs:
        el = uidoc.Document.GetElement(r.ElementId)
        if isinstance(el, Pipe):
            pid = el.Id.IntegerValue
            pipe_ids.append(pid)
            log_debug(log, "  - Picked Pipe: {}".format(pid))
    return pipe_ids


def collect_selected(uidoc, log):
    log_debug(log, "Mode = SELECTED")
    pipe_ids = []
    for eid in uidoc.Selection.GetElementIds():
        el = uidoc.Document.GetElement(eid)
        if isinstance(el, Pipe):
            pid = el.Id.IntegerValue
            pipe_ids.append(pid)
            log_debug(log, "  - Selected Pipe: {}".format(pid))
    return pipe_ids


def collect_visible(doc, view, log):
    log_debug(log, "Mode = VISIBLE_IN_VIEW")
    collector = FilteredElementCollector(doc, view.Id).OfClass(Pipe)
    pipe_ids = [p.Id.IntegerValue for p in collector]
    for pid in pipe_ids:
        log_debug(log, "  - Visible Pipe: {}".format(pid))
    return pipe_ids


def collect_all(doc, log):
    log_debug(log, "Mode = ALL_IN_MODEL")
    collector = FilteredElementCollector(doc).OfClass(Pipe)
    pipe_ids = [p.Id.IntegerValue for p in collector]
    log_debug(log, "Found {} pipes in model.".format(len(pipe_ids)))
    return pipe_ids


def collect_tagged(doc, view, log):
    log_debug(log, "Mode = TAGGED")
    return []


def collect_provided(data, log):
    ids = data.get("pipe_ids") or []
    log_debug(log, "Mode = PROVIDED → Received {} IDs".format(len(ids)))
    return ids


# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------
def run(uiapp, data, log):
    log_debug(log, "=== get_pipe_ids.py START ===")

    uidoc = uiapp.ActiveUIDocument
    doc = uidoc.Document
    view = uidoc.ActiveView

    mode = data.get("mode", MODE_PICK)
    log_debug(log, "Requested mode: {}".format(mode))

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    pipe_ids = []

    try:
        if mode == MODE_PICK:
            pipe_ids = collect_pick(uidoc, log)

        elif mode == MODE_SELECTED:
            pipe_ids = collect_selected(uidoc, log)

        elif mode == MODE_VISIBLE_IN_VIEW:
            pipe_ids = collect_visible(doc, view, log)

        elif mode == MODE_ALL_IN_MODEL:
            pipe_ids = collect_all(doc, log)

        elif mode == MODE_TAGGED:
            pipe_ids = collect_tagged(doc, view, log)

        elif mode == MODE_PROVIDED:
            pipe_ids = collect_provided(data, log)

        else:
            msg = "Unknown pipe selection mode: {}".format(mode)
            write_response({"error": msg})
            log_debug(log, msg)
            return

        write_response({"status": "ok", "pipe_ids": pipe_ids})
        log_debug(log, "Returned {} pipe IDs".format(len(pipe_ids)))

        if mode == MODE_PICK:
            try:
                empty = List[ElementId]()
                uidoc.Selection.SetElementIds(empty)
                log_debug(log, "Cleared Revit selection after PICK")
            except Exception as e:
                log_debug(log, "Failed to clear selection: {}".format(e))

    except Exception as e:
        write_response({"error": str(e)})
        log_debug(log, "EXCEPTION: {}".format(e))
        log_debug(log, traceback.format_exc())

    finally:
        log_debug(log, "=== get_pipe_ids.py END ===")
