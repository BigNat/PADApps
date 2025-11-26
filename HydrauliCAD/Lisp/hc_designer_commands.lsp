


(defun c:Designer_Pipe ( / )
  (hc-log "🧩 Designer_Pipe command started.")
  (set_layer_from_bridge)
  (hc-log "📏 Drawing pipe line...")
  (command "_.LINE")
  (hc-log "✅ Designer_Pipe command completed.")
  (princ)
)





(defun c:hc_designer_snap (/ a ang)
  (setvar "cmdecho" 0)
  (setvar "orthomode" 1)
  (setq SNAPANG? (getvar "snapang"))
  (setq sang SNAPANG?)
  (cond
    ((= sang 0)
      (setvar "snapang" 0.785398)
      (princ "\nSnap 45° – crosshairs rotated to 45 degrees"))
    ((= sang 0.785398)
      (setvar "snapang" 0)
      (princ "\nSnap 0° – crosshairs rotated to 0 degrees"))
    (t
      (setvar "snapang" 0)
      (princ "\nSnap reset to 0 degrees"))
  )
  (princ)
)

