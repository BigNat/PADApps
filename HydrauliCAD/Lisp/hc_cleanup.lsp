;;; =============================================================
;;; HydrauliCAD Cleanup Suite (Pure AutoLISP Implementation)
;;; Modular cleanup command set for batch or toggle use.
;;; =============================================================

;;; Each command is self-contained and independent — no external VBA/Funcs.
;;; All use standard AutoCAD COM calls for portability.


;; -----------------------------
;; hc_cleanup_main.lsp
;; -----------------------------

(setq *hc_cleanup_toggles*
  '(
    ("MakeByLayer" . T)
    ("ChangeLineWeight" . T)
    ("DeleteBlocks" . NIL)
    ("DeleteDimensions" . NIL)
    ("DeleteHatching" . NIL)
    ("DeleteText" . NIL)
    ("DeleteTextMatch" . NIL)
    ("DeleteUCS" . NIL)
  )
)

(defun hc-toggle-cleanup (name)
  (if (assoc name *hc_cleanup_toggles*)
    (progn
      (setq current (cdr (assoc name *hc_cleanup_toggles*)))
      (setq *hc_cleanup_toggles*
        (subst (cons name (not current)) (assoc name *hc_cleanup_toggles*) *hc_cleanup_toggles*)
      )
      (hc-log (strcat "🔘 " name " toggle → " (if (not current) "ON" "OFF")))
    )
  )
)

(defun c:HC_CLEANUP ( / )
  (hc-log "🧹 HydrauliCAD Cleanup started.")
  (foreach toggle *hc_cleanup_toggles*
    (if (cdr toggle)
      (progn
        (setq cmd (strcat "C:HC_" (strcase (car toggle))))
        (if (fboundp (read cmd))
          (progn
            (hc-log (strcat "▶ Running " (car toggle)))
            (eval (read (strcat "(C:HC_" (strcase (car toggle)) ")")))
          )
          (hc-log (strcat "⚠️ Missing cleanup command: " (car toggle)))
        )
      )
    )
  )
  (hc-log "✅ HydrauliCAD Cleanup completed.")
  (princ)
)

