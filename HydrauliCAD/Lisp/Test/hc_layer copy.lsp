(defun hc-create-layer (layer_name color weight line_type / doc layers layer oldColor oldWeight oldType)
  (hc-ensure-linetype-loaded line_type)
  (setq doc (vla-get-ActiveDocument (vlax-get-Acad-Object)))
  (setq layers (vla-get-Layers doc))

  ;; Validate color
  (if (or (not (numberp color)) (< color 1) (> color 255))
    (setq color 7)
  )

  ;; Get or create the layer
  (if (tblsearch "LAYER" layer_name)
    (progn
      (setq layer (vla-Item layers layer_name))
      (setq oldColor (vla-get-Color layer))
      (setq oldWeight (vla-get-LineWeight layer))
      (setq oldType (vla-get-Linetype layer))

      (hc-log (strcat "🔍 Found existing layer: " layer_name))
      (hc-log (strcat "   BEFORE → Color:" (itoa oldColor)
                      " | Weight:" (itoa oldWeight)
                      " | Linetype:" oldType))

      ;; Force overwrite
      (vla-put-Color layer color)
      (vla-put-LineWeight layer (vlax-make-variant weight))
      (if (tblsearch "LTYPE" line_type)
        (vla-put-Linetype layer line_type)
        (vla-put-Linetype layer "Continuous"))

      ;; Verify
      (hc-log (strcat "✅ AFTER  → Color:" (itoa (vla-get-Color layer))
                      " | Weight:" (itoa (vla-get-LineWeight layer))
                      " | Linetype:" (vla-get-Linetype layer)))
    )
    (progn
      ;; Create new
      (setq layer (vla-Add layers layer_name))
      (vla-put-Color layer color)
      (vla-put-LineWeight layer (vlax-make-variant weight))
      (if (tblsearch "LTYPE" line_type)
        (vla-put-Linetype layer line_type)
        (vla-put-Linetype layer "Continuous"))
      (hc-log (strcat "🎨 Created new layer: " layer_name))
    )
  )

  ;; Refresh display
  (vla-Regen doc acAllViewports)
)






(defun hc-ensure-linetype-loaded (line_type / doc)
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (if (not (tblsearch "LTYPE" line_type))
    (progn
      (command "_.-linetype" "_load" line_type "C:\\HydrauliCAD\\Tools\\Designer\\Support\\Designer.lin" "")
      (hc-log (strcat "📏 Linetype loaded → " line_type))
    )
    (hc-log (strcat "ℹ️ Linetype already available: " line_type))
  )
)



(defun set_layer_from_bridge ( / jsonfile txt layer_name)
  (setq jsonfile (hc-get-bridge-json-path))


  (setq layer_name (hc-json-get jsonfile "layer"))
  (setq line_type (hc-json-get jsonfile "linetype"))
  (setq color (atoi (hc-json-get jsonfile "color")))
  (setq weight (atoi (hc-json-get jsonfile "weight")))

  (if (not layer_name)
    (progn
      (setq layer_name "Hyd_Pipe_Default")
      (hc-log "⚠️ Bridge JSON missing → Using default layer: Hyd_Pipe_Default")
    )
  )
    
  (if (not line_type)
    (progn
      (setq line_type "Continuous")
      (hc-log "⚠️ Bridge JSON missing → Using default linetype: Continuous")
    )
  )
    
  (if (not color)
    (progn
      (setq color 7)
      (hc-log "⚠️ Bridge JSON missing → Using default color: 7")
    )
  )
    
  (if (not weight)
    (progn
      (setq weight 25)
      (hc-log "⚠️ Bridge JSON missing → Using default weight: 25")
    )
  )
    
    
    
  (if (not (tblsearch "LAYER" layer_name))
    (progn
      (hc-create-layer layer_name color weight line_type)
      (hc-log (strcat "🎨 Created missing layer: " layer_name))
    )
    (hc-log (strcat "ℹ️ Layer already loaded: " layer_name))
  )
  
  (setvar "clayer" layer_name)
  (hc-log (strcat "✅ Current layer set → " layer_name))
  (princ)
)

