

;;; -----------------------------
;;; hc_cleanup_dimensions.lsp
;;; -----------------------------
(defun c:HC_DELETEDIMENSIONS ( / ss)
  (hc-log "🧹 DeleteDimensions started.")
  (setq ss (ssget "X" '((0 . "DIMENSION"))))
  (if ss
    (repeat (sslength ss)
      (setq e (ssname ss 0))
      (entdel e)
      (ssdel e ss)
    )
  )
  (hc-log "✅ DeleteDimensions completed.")
  (princ)
)
