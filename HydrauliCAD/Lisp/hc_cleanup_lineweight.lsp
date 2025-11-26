
;;; -----------------------------
;;; hc_cleanup_lineweight.lsp
;;; -----------------------------
(defun c:HC_CHANGELINEWEIGHT ( / doc ent)
  (hc-log "🧹 ChangeLineWeight started.")
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (vlax-for ent (vla-get-ModelSpace doc)
    (vla-put-LineWeight ent acLnWt005)
  )
  (hc-log "✅ ChangeLineWeight completed.")
  (princ)
)
