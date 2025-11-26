

;;; -----------------------------
;;; hc_cleanup_hatching.lsp
;;; -----------------------------
(defun c:HC_DELETEHATCHING ( / ss)
  (hc-log "🧹 DeleteHatching started.")
  (setq ss (ssget "X" '((0 . "HATCH"))))
  (if ss
    (repeat (sslength ss)
      (setq e (ssname ss 0))
      (entdel e)
      (ssdel e ss)
    )
  )
  (hc-log "✅ DeleteHatching completed.")
  (princ)
)
