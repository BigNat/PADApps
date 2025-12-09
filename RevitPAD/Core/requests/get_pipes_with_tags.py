# coding: utf-8

import os
import json
import traceback

from Autodesk.Revit.DB import (
    FilteredElementCollector,
    IndependentTag,
    ElementId,
    VisibleInViewFilter,
    LinkElementId
)
from Autodesk.Revit.DB.Plumbing import Pipe

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def write_debug(log, msg):
    try:
        log("[DEBUG get_pipes_with_tags] " + msg)
    except:
        pass


def resolve_tagged_element_ids(tag, doc, log):
    """Return a list of ElementId objects referenced by a tag."""
    ids = []

    if not hasattr(tag, "GetTaggedElementIds"):
        return ids

    try:
        refs = tag.GetTaggedElementIds()
    except:
        return ids

    for ref in refs:
        # Try linked element id first
        try:
            linked_id = ref.LinkedElementId
            if linked_id and linked_id.IntegerValue > 0:
                ids.append(linked_id)
                continue
        except:
            pass

        # Try ElementId next
        try:
            eid = ref.ElementId
            if eid and eid.IntegerValue > 0:
                ids.append(eid)
                continue
        except:
            pass

        write_debug(log, "Unhandled reference: {}".format(ref))

    return ids


def run(uiapp, data, log):
    write_debug(log, "=== get_pipes_with_tags.py START ===")

    try:
        uidoc = uiapp.ActiveUIDocument
        doc = uidoc.Document
        view = uidoc.ActiveView

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        write_debug(log, "Scanning current view for pipe tags...")

        vis_filter = VisibleInViewFilter(doc, view.Id)

        tags = FilteredElementCollector(doc, view.Id) \
            .OfClass(IndependentTag) \
            .WherePasses(vis_filter) \
            .ToElements()

        write_debug(log, "Found {} tags visible in current view".format(len(tags)))

        pipe_ids = set()

        for tag in tags:
            ids = resolve_tagged_element_ids(tag, doc, log)

            for eid in ids:
                if eid and eid.IntegerValue > 0:
                    el = doc.GetElement(eid)
                    if isinstance(el, Pipe):
                        pipe_ids.add(eid.IntegerValue)

        final_ids = sorted(pipe_ids)
        write_debug(log, "Pipes with tags in current view: {}".format(final_ids))

        result = {"status": "ok", "pipe_ids": final_ids}

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        write_debug(log, "Response written successfully.")

    except Exception as e:
        write_debug(log, "EXCEPTION: {}".format(e))
        write_debug(log, traceback.format_exc())

        with open(RESPONSE_PATH, "w") as f:
            json.dump({"error": str(e)}, f, indent=2)

    write_debug(log, "=== get_pipes_with_tags.py END ===")
