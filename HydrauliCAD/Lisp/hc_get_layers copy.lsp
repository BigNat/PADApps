;;; ---------------------------------------------------------------------------
;;; STEP 1: Raw layer collector
;;; ---------------------------------------------------------------------------
(defun hc_get_layers_raw ( / layers doc ac )
  (setq layers '())
  (setq ac  (vlax-get-acad-object))
  (setq doc (vla-get-ActiveDocument ac))

  (vlax-for L (vla-get-Layers doc)
    (setq layers (cons (vla-get-Name L) layers))
  )

  (setq layers (reverse layers))

  (hc-log (strcat "📑 hc_get_layers_raw → " (itoa (length layers)) " layer(s) found."))

  layers
)

;;; ---------------------------------------------------------------------------
;;; STEP 2: Write layer list to Python bridge (needs DWG_PATH)
;;; ---------------------------------------------------------------------------
(defun hc_write_layer_bridge (dwg_path layer_list / pybridge)
  (vl-load-com)

  (setq pybridge (vlax-create-object "HydrauliCAD.JsonBridge"))

  ;; SAME CALL PATTERN AS XREF:
  ;; (vlax-invoke pybridge 'BuildLayerList dwg_path layer_list)
  (vlax-invoke pybridge 'BuildLayerList dwg_path layer_list)

  (vlax-release-object pybridge)

  (hc-log "✅ hc_write_layer_bridge → layer bridge JSON written successfully.")

  T
)

;;; ---------------------------------------------------------------------------
;;; STEP 3: MAIN COMMAND (must be a real AutoCAD command)
;;; ---------------------------------------------------------------------------
(defun C:HC_GETLAYERS ( / layers ac doc dwg_path )
  (hc-log "📄 HC_GETLAYERS started.")

  (setq ac  (vlax-get-acad-object))
  (setq doc (vla-get-ActiveDocument ac))
  (setq dwg_path (vla-get-FullName doc))

  ;; 1) Collect layers
  (setq layers (hc_get_layers_raw))

  ;; 2) Write bridge with correct DWG path
  (hc_write_layer_bridge dwg_path layers)

  (hc-log "📄 HC_GETLAYERS completed successfully.")
  (princ)
)
