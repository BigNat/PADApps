;; ===============================================================
;; hc_json.lsp — HydrauliCAD JSON Read/Write Utility (Generic)
;; ===============================================================

(defun hc-json-get (path key / jsonObj val)
  (setq jsonObj (vlax-create-object "HydrauliCAD.JsonBridge"))
  (setq val (vlax-invoke jsonObj 'GetValue path key))
  (vlax-release-object jsonObj)
  val
)