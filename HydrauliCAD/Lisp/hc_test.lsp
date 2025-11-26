

(defun c:t1 ( / jsonfile txt layer_name service desc)
  (setq jsonfile (hc-get-bridge-json-path))
  (setq txt (hc-json-read jsonfile))
  
  (hc-log "📦 Bridge data loaded.")
  (hc-log (strcat "📄 JSON preview: " (substr txt 1 1000)))

  (setq layer_name (hc-parse-json-value txt "layer"))
  (setq line_type (hc-parse-json-value txt "linetype"))
  (setq color (atoi (hc-parse-json-value txt "color")))
  (setq weight (atoi (hc-parse-json-value txt "weight")))
  (setq plot/ (vlax-make-variant T))
  
  (setq service (hc-parse-json-value txt "service"))
  (setq desc (hc-parse-json-value txt "description"))

  (hc-log (strcat "💧 Service → " service " (" desc ")"))
  (hc-log (strcat "🧱 Target layer → " layer_name))
  (hc-log (strcat "🎨 Layer properties → Color: " (itoa color)
                  " | Weight: " (itoa weight)
                  " | Linetype: " line_type
                  " | Plot: " (if plot/ "Yes" "No")))
  (hc-log "✅ Test completed successfully.")
  (princ)
)


(defun c:t2 ( / value )
  (setq value (hc-json-get (hc-get-bridge-json-path) "color"))
  (princ (strcat "\nColor: " value))
  (princ)
)
