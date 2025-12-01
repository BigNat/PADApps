(defun C:HC_GETCURRENTLAYER ( / ac doc cur name pybridge )

  (vl-load-com)

  (setq ac   (vlax-get-acad-object))
  (setq doc  (vla-get-ActiveDocument ac))
  (setq cur  (vla-get-ActiveLayer doc))
  (setq name (vla-get-Name cur))

  (setq pybridge (vlax-create-object "HydrauliCAD.JsonBridge"))

  ;; Generic: WriteKeyValue("current_layer", "<name>")
  (vlax-invoke pybridge 'WriteKeyValue "current_layer" name)

  (vlax-release-object pybridge)
  (princ)
)
