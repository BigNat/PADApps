(defun hc_get_xrefs ( / doc blk result name )
  (vl-load-com)
  (setq result '())
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))

  (hc-log "🔍 hc_get_xrefs → scanning drawing for XREFs...")

  (vlax-for blk (vla-get-Blocks doc)
    (if (and (vlax-property-available-p blk 'IsXRef)
             (= (vla-get-IsXRef blk) :vlax-true))
      (progn
        (setq name (vla-get-Name blk))
        (setq result (cons name result))
        (hc-log (strcat "   🔗 Found XREF: " name))
      )
    )
  )

  (setq result (reverse result))
  (hc-log (strcat "📊 hc_get_xrefs → total XREFs found: " (itoa (length result))))
  result
)



(defun hc_get_xref_details ( / doc blk result entry val_safe val_name val_load val_resolve val_path )
  (vl-load-com)
  (setq result '())
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))

  ;; Safe property getter with error handling and logging
  (defun val_safe (obj prop)
    (setq val (vl-catch-all-apply '(lambda () (vlax-get-property obj prop))))
    (if (vl-catch-all-error-p val)
      (progn
        (hc-log (strcat "      ⚠️ Property access failed: " (vl-princ-to-string prop)))
        nil
      )
      (progn
        (hc-log (strcat "      ✅ " (vl-princ-to-string prop) " = " (vl-princ-to-string val)))
        val
      )
    )
  )

  (hc-log "🔍 hc_get_xref_details → scanning blocks for Light Table XREFs...")

  (vlax-for blk (vla-get-Blocks doc)
    (if (and (vlax-property-available-p blk 'IsXRef)
             (= (vla-get-IsXRef blk) :vlax-true))
      (progn
        (setq val_name (vla-get-Name blk))
        (hc-log (strcat "   🔹 Processing XREF: " val_name))
        (setq val_path    (val_safe blk 'Path))

        (setq entry
          (list
            (cons "name" val_name)
            (cons "path" (if val_path val_path ""))
          )
        )

        (setq result (cons entry result))
        (hc-log (strcat "   💡 Captured XREF entry: " val_name))
      )
    )
  )

  (setq result (reverse result))
  (hc-log (strcat "📊 hc_get_xref_details → total Light Table XREFs captured: " (itoa (length result))))
  result
)



(defun hc_convert_xref_data (xref_list / jsonlist item)
  (setq jsonlist '())
  (foreach item xref_list
    ;; Convert assoc list → JSON-like list of pairs: [key, value]
    (setq jsonlist
      (cons
        (list
          (cdr (assoc "name" item))
          (cdr (assoc "path" item))
        )
        jsonlist
      )
    )
  )
  (reverse jsonlist)
)
