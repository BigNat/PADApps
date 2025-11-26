

;;; -----------------------------
;;; hc_cleanup_text.lsp
;;; -----------------------------
(defun c:HC_DELETETEXT ( / ss)
  (hc-log "🧹 DeleteText started.")
  (setq ss (ssget "X" '((0 . "TEXT"))))
  (if ss
    (progn
      (repeat (sslength ss)
        (setq e (ssname ss 0))
        (entdel e)
        (ssdel e ss)
      )
    )
  )
  (hc-log "✅ DeleteText completed.")
  (princ)
)

(defun c:HC_DELETETEXTMATCH ( / txt ss)
  (setq txt (getstring "Enter text to delete: "))
  (hc-log (strcat "🧹 DeleteTextMatch → " txt))
  (setq ss (ssget "X" (list (cons 0 "TEXT") (cons 1 txt))))
  (if ss
    (repeat (sslength ss)
      (setq e (ssname ss 0))
      (entdel e)
      (ssdel e ss)
    )
  )
  (hc-log "✅ DeleteTextMatch completed.")
  (princ)
)
