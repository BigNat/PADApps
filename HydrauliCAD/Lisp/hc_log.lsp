;; ===============================================================
;; hc_log.lsp — HydrauliCAD Logging Utility (Session-Aware)
;; ===============================================================

(defun hc-log-init ( / file session-line)
  (setq file (hc-get-logs-file))
  (setq session-line
        (strcat
          "\n============================================================\n"
          "🕓 New HydrauliCAD Session: "
          (menucmd "M=$(edtime,$(getvar,date),YYYY-MM-DD HH:MM:SS)")
          "\n============================================================"))
  (setq f (open file "a"))
  (if f (progn (write-line session-line f) (close f)))
  (princ "\n🪵 Log session started.")
)

(defun hc-log-clear ( / file)
  (setq file (hc-get-logs-file))
  (if (findfile file)
    (progn
      (setq f (open file "w"))
      (write-line "🧹 Cleared previous HydrauliCAD log." f)
      (close f)
      (princ "\n🧹 Log file cleared."))
  )
)

(defun hc-log (msg / f tstamp line file)
  (setq file (hc-get-logs-file))
  (setq tstamp (menucmd "M=$(edtime,$(getvar,date),YYYY-MM-DD HH:MM:SS)"))
  (setq line (strcat "[" tstamp "] " msg))
  (setq f (open file "a"))
  (if f (progn (write-line line f) (close f)))
  (princ (strcat "\n🪵 " line))
)
(princ)
