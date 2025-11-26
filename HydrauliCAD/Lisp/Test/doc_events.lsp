;; ===============================================================
;; doc_timer.lsp — HydrauliCAD Open Drawing Tracker (Universal Timer)
;; ===============================================================

(vl-load-com)

;; ---------------------------------------------------------------
;; Utility: Write to HydrauliCAD log
;; ---------------------------------------------------------------
(defun hyd-log (msg / f tstamp line file)
  (setq file "C:/HydrauliCAD/Data/hydraulicad_log.txt")
  (setq tstamp (menucmd "M=$(edtime,$(getvar,date),YYYY-MM-DD HH:MM:SS)"))
  (setq line (strcat "[" tstamp "] " msg))
  (setq f (open file "a"))
  (if f (progn (write-line line f) (close f)))
  (princ (strcat "\n🪵 " line))
)

;; ---------------------------------------------------------------
;; Utility: Collect and write JSON
;; ---------------------------------------------------------------
(defun hyd-write-open-json ( / file drawlist current f jsontext app docs )
  (setq file "C:/HydrauliCAD/Data/open_drawings.json")
  (setq app (vlax-get-acad-object))
  (setq docs (vla-get-Documents app))
  (setq drawlist '())
  (vlax-for d docs
    (setq drawlist (cons (vla-get-FullName d) drawlist))
  )
  (setq drawlist (reverse drawlist))
  (setq current (strcat (getvar "DWGPREFIX") (getvar "DWGNAME")))

  ;; Build JSON
  (setq jsontext "{\n  \"current\": \"")
  (setq jsontext (strcat jsontext (vl-string-translate "\\" "/" current) "\",\n"))
  (setq jsontext (strcat jsontext "  \"open\": [\n"))
  (foreach dwg drawlist
    (if (/= dwg "")
      (setq jsontext (strcat jsontext "    \"" (vl-string-translate "\\" "/" dwg) "\",\n"))
    )
  )
  (if (> (strlen jsontext) 6)
    (setq jsontext (substr jsontext 1 (- (strlen jsontext) 2)))
  )
  (setq jsontext (strcat jsontext "\n  ]\n}\n"))

  (setq f (open file "w"))
  (if f (progn (write-line jsontext f) (close f)))
  (hyd-log (strcat "📘 Updated open_drawings.json (" (itoa (length drawlist)) " drawings)"))
)

;; ---------------------------------------------------------------
;; Heartbeat function
;; ---------------------------------------------------------------
(defun hyd-heartbeat-loop ( / delay )
  (setq delay 2000) ;; 2 seconds
  (while *HydHeartbeatActive*
    (vl-catch-all-apply 'hyd-write-open-json)
    (command "_delay" delay)
  )
)

;; ---------------------------------------------------------------
;; Commands
;; ---------------------------------------------------------------
(defun c:HYD_TIMER_START ( / )
  (if (not *HydHeartbeatActive*)
    (progn
      (setq *HydHeartbeatActive* T)
      (hyd-log "▶ Starting HydrauliCAD timer loop (2 sec)...")
      (hyd-write-open-json)
      (hyd-heartbeat-loop)
    )
    (hyd-log "⚠ Timer already running.")
  )
  (princ)
)

(defun c:HYD_TIMER_STOP ( / )
  (if *HydHeartbeatActive*
    (progn
      (setq *HydHeartbeatActive* nil)
      (hyd-log "⏹ HydrauliCAD timer stopped.")
    )
    (hyd-log "⚠ Timer not active.")
  )
  (princ)
)

;; ---------------------------------------------------------------
;; Load message
;; ---------------------------------------------------------------
(hyd-log "🔄 HydrauliCAD simple timer tracker loaded.")
(princ "\nType HYD_TIMER_START to begin 2-second tracking, HYD_TIMER_STOP to end.")
(princ)
