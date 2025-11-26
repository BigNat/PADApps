;;; ---------------------------------------------------------------
;;; hc_loader.lsp – Auto-loader for HydrauliCAD (with logging order)
;;; ---------------------------------------------------------------
(vl-load-com)
(load "hc_paths.lsp")

(defun c:hc_loader ( / hc_path files full)
  (setq hc_path (hc-get-lisp-path))

  (if (not (vl-file-directory-p hc_path))
    (progn
      (princ (strcat "\n⚠️ HydrauliCAD folder not found: " hc_path))
      (exit)
    )
  )

  ;; ------------------------------------------------------------
  ;; 1️⃣ Always load logger first (safe dependency)
  ;; ------------------------------------------------------------
  (setq full (strcat hc_path "hc_paths.lsp"))
  (if (findfile full)
    (progn
      (load full)
    )
    (princ "\n⚠️ Paths file not found — hc_paths.lsp missing")
  )
  
  (setq full (strcat hc_path "hc_log.lsp"))
  (if (findfile full)
    (progn
      (load full)
      (princ "\n✅ Loaded hc_log.lsp (logger initialized)")
      (hc-log-init)
      (hc-log "🚀 Starting HydrauliCAD Loader...")
    )
    (princ "\n⚠️ Logger not found — hc_log.lsp missing")
  )

  ;; ------------------------------------------------------------
  ;; 2️⃣ Load all other .lsp files except this loader and logger
  ;; ------------------------------------------------------------
  (setq files
        (vl-remove-if
          '(lambda (x) (member x '("hc_loader.lsp" "hc_log.lsp" "hc_paths.lsp")))
          (vl-directory-files hc_path "*.lsp" 1)
        )
  )

  (foreach f files
    (setq full (strcat hc_path f))
    (if (findfile full)
      (progn
        (load full)
        (hc-log (strcat "✅ Loaded " f))
      )
      (hc-log (strcat "⚠️ Missing " full))
    )
  )

  (hc-log "✅ HydrauliCAD startup complete.")
  (princ "\nHydrauliCAD startup complete.")
  (princ)
)

;;; ------------------------------------------------------------
;;; Run only once per AutoCAD session
;;; ------------------------------------------------------------
(if (not (boundp '*hc_loader_initialized*))
  (progn
    (setq *hc_loader_initialized* T)
    (c:hc_loader)
  )
)
(princ)
