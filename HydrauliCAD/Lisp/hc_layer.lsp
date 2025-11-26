(defun hc-create-layer (layer_name color weight line_type / doc layers layer oldColor oldWeight oldType)
  (hc-ensure-linetype-loaded line_type)
  (setq doc (vla-get-ActiveDocument (vlax-get-Acad-Object)))
  (setq layers (vla-get-Layers doc))

  ;; Validate color input
  (if (or (not (numberp color)) (< color 1) (> color 255))
    (setq color 7)
  )

  ;; Create or get the layer
  (if (tblsearch "LAYER" layer_name)
    (progn
      (setq layer (vla-Item layers layer_name))
      (setq oldColor (vla-get-Color layer))
      (setq oldWeight (vla-get-LineWeight layer))
      (setq oldType (vla-get-Linetype layer))

      (hc-log (strcat "🧱 Updating existing layer: " layer_name))
      (hc-log (strcat "   BEFORE → Color:" (itoa oldColor)
                      " | Weight:" (itoa oldWeight)
                      " | Linetype:" oldType))

      ;; Only apply changes if different (and log which change applied)
      (if (/= oldColor color)
        (progn
          (vla-put-Color layer color)
          (hc-log (strcat "   🖌️ Color changed: " (itoa oldColor) " → " (itoa color)))
        )
        (hc-log "   ℹ️ Color already correct.")
      )

      (if (/= oldWeight weight)
        (progn
          (vla-put-LineWeight layer (vlax-make-variant weight))
          (hc-log (strcat "   ⚖️ Lineweight changed: " (itoa oldWeight) " → " (itoa weight)))
        )
        (hc-log "   ℹ️ Lineweight already correct.")
      )

      (if (and oldType (/= (strcase oldType) (strcase line_type)))
        (progn
          (if (tblsearch "LTYPE" line_type)
            (vla-put-Linetype layer line_type)
            (vla-put-Linetype layer "Continuous"))
          (hc-log (strcat "   📏 Linetype changed: " oldType " → " line_type))
        )
        (hc-log "   ℹ️ Linetype already correct.")
      )

      ;; Verify after update
      (hc-log (strcat "✅ AFTER → Color:" (itoa (vla-get-Color layer))
                      " | Weight:" (itoa (vla-get-LineWeight layer))
                      " | Linetype:" (vla-get-Linetype layer)))
    )
    (progn
      (setq layer (vla-Add layers layer_name))
      (vla-put-Color layer color)
      (vla-put-LineWeight layer (vlax-make-variant weight))
      (if (tblsearch "LTYPE" line_type)
        (vla-put-Linetype layer line_type)
        (vla-put-Linetype layer "Continuous"))
      (hc-log (strcat "🎨 Created new layer: " layer_name
                      "  [Color: " (itoa color)
                      " | Weight: " (itoa weight)
                      " | Linetype: " (if (tblsearch "LTYPE" line_type) line_type "Continuous")
                      "]"))
    )
  )

  ;; Refresh to display changes
  (vla-Regen doc acAllViewports)
)







(defun hc-ensure-linetype-loaded (line_type / doc)
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (if (not (tblsearch "LTYPE" line_type))
    (progn
      (command "_.-linetype" "_load" line_type "C:\\PADApps\\HydrauliCAD\\Tools\\Designer\\Support\\Designer.lin" "")
      (hc-log (strcat "📏 Linetype loaded → " line_type))
    )
    (hc-log (strcat "ℹ️ Linetype already available: " line_type))
  )
)



(defun set_layer_from_bridge ( / jsonfile layer_name line_type color weight)
  (setq jsonfile (hc-get-bridge-json-path))
  (setq layer_name (hc-json-get jsonfile "layer"))
  (setq line_type (hc-json-get jsonfile "linetype"))
  (setq color (atoi (hc-json-get jsonfile "color")))
  (setq weight (atoi (hc-json-get jsonfile "weight")))

  (if (not layer_name) (setq layer_name "Hyd_Pipe_Default"))
  (if (not line_type) (setq line_type "Continuous"))
  (if (not color) (setq color 7))
  (if (not weight) (setq weight 25))

  (hc-create-layer layer_name color weight line_type)

  (setvar "clayer" layer_name)
  (hc-log (strcat "✅ Current layer set → " layer_name))
  (princ)
)
