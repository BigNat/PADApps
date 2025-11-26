

(defun hc_filter_xrefs (xrefs / filtered)
  (setq filtered '())
  (foreach name xrefs
    (if (wcmatch (strcase name) "LT_XREF_*")
      (setq filtered (cons name filtered))
    )
  )
  (setq filtered (reverse filtered))
  (hc-log (strcat "🔍 hc_filter_xrefs → " (itoa (length filtered)) " Light Table XREF(s) found."))
  filtered
)


(defun hc_write_bridge (dwgpath xref_data / names paths pybridge)
  (vl-load-com)
  (foreach x xref_data
    (setq names (cons (cdr (assoc "name" x)) names))
    (setq paths (cons (cdr (assoc "path" x)) paths))
  )
  (setq names (reverse names))
  (setq paths (reverse paths))

  (setq pybridge (vlax-create-object "HydrauliCAD.JsonBridge"))
  (vlax-invoke pybridge 'BuildLightTableData dwgpath names paths)
  (vlax-release-object pybridge)
  (hc-log "✅ hc_write_bridge → bridge written successfully.")
)






(defun c:hc_write_xref_data ( / doc dwgpath xrefs lt_xrefs )
  (vl-load-com)
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (setq dwgpath (vla-get-FullName doc))

  (hc-log "📦 hc_write_xref_data started.")
  
  (setq xrefs (hc_get_xrefs))
  (setq xref_data (hc_get_xref_details))
  
  (hc_write_bridge dwgpath xref_data)
  
  (hc-log "📄 hc_write_xref_data completed successfully.")
  (princ)
)

