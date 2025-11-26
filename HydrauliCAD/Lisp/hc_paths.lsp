;; ===============================================================
;; hc_paths.lsp — HydrauliCAD Path Utilities 
;; ===============================================================

;; ---------------------------------------------------------------
;; Get HydrauliCAD root installation path 

(defun hc-get-root-path ( / path )
  (setq path "C:/PADApps/HydrauliCAD/")
  path
)

;; ---------------------------------------------------------------
;; Get HydrauliCAD data path
(defun hc-get-data-path ( / path )
  (setq path (strcat (hc-get-root-path) "Data/"))
  path
)

;; ---------------------------------------------------------------
;; Get HydrauliCAD lisp path
(defun hc-get-lisp-path ( / path )
  (setq path (strcat (hc-get-root-path) "Lisp/"))
  path
)
;; ---------------------------------------------------------------

;; Get HydrauliCAD Blocks path
(defun hc-get-blocks-path ( / path )
  (setq path (strcat (hc-get-root-path) "Blocks/"))
  path
)
;; ---------------------------------------------------------------

;; Get HydrauliCAD Support path
(defun hc-get-support-path ( / path )
  (setq path (strcat (hc-get-root-path) "Support/"))
  path
)
;; ---------------------------------------------------------------

;; Get HydrauliCAD Logs path
(defun hc-get-logs-path ( / path )
  (setq path (strcat (hc-get-root-path) "Logs/"))
  path
)

(defun hc-get-logs-file ( / path )
  (setq path (strcat (hc-get-logs-path) "hc_log.txt"))
  path
)

;; ---------------------------------------------------------------


(defun hc-get-service-json-path ()
  (strcat (hc-get-data-path) "services.json")
)

(defun hc-get-layer-json-path ()
  (strcat (hc-get-data-path) "layers.json")
)


(defun hc-get-bridge-json-path ()
  (strcat (hc-get-root-path) "Bridge/bridge.json")
)


(defun hc-get-layer-config ()
  (strcat (hc-get-root-path) "Bridge/layer_config.json")
)




(princ)