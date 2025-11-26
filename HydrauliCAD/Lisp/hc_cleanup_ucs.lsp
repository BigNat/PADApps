

;;; -----------------------------
;;; hc_cleanup_ucs.lsp
;;; -----------------------------
(defun c:HC_DELETEUCS ( / )
  (hc-log "🧹 DeleteUCS started.")
  (command "UCS" "W")
  (command "PLAN" "W")
  (command "UCSFOLLOW" 1)
  (hc-log "✅ DeleteUCS completed.")
  (princ)
)

(princ)
