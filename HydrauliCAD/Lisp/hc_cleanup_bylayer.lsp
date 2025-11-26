


;;; -----------------------------
;;; hc_cleanup_bylayer.lsp
;;; -----------------------------
(defun c:HC_MAKEBYLAYER ( / doc ent)
  (hc-log "🧹 MakeByLayer started.")
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (vlax-for ent (vla-get-ModelSpace doc)
    (if (and (not (vlax-property-available-p ent 'IsXRef)) (/= (vla-get-Color ent) 256))
      (vla-put-Color ent 256)
    )
  )
  (hc-log "✅ MakeByLayer completed.")
  (princ)
)
