;;; ---------------------------------------------------------------------------
;;; STEP 1: Raw layer collector
;;; ---------------------------------------------------------------------------
(defun hc_get_layers_raw ( / doc ac
                             names colors ltypes lws locked frozen on
                             name color ltype lw lk fr onflag )

  (setq names   '()
        colors  '()
        ltypes  '()
        lws     '()
        locked  '()
        frozen  '()
        on      '()
  )

  (setq ac  (vlax-get-acad-object))
  (setq doc (vla-get-ActiveDocument ac))

  (vlax-for L (vla-get-Layers doc)

    (setq name  (vla-get-Name L))
    (setq color (vla-get-Color L))
    (setq ltype (vla-get-Linetype L))
    (setq lw    (vla-get-Lineweight L))

    (setq lk     (if (= (vla-get-Lock L) :vlax-true) 1 0))
    (setq fr     (if (= (vla-get-Freeze L) :vlax-true) 1 0))
    (setq onflag (if (= (vla-get-LayerOn L) :vlax-true) 1 0))

    (setq names   (cons name names))
    (setq colors  (cons color colors))
    (setq ltypes  (cons ltype ltypes))
    (setq lws     (cons lw    lws))
    (setq locked  (cons lk     locked))
    (setq frozen  (cons fr     frozen))
    (setq on      (cons onflag on))
  )

  (list
    (reverse names)
    (reverse colors)
    (reverse ltypes)
    (reverse lws)
    (reverse locked)
    (reverse frozen)
    (reverse on)
  )
)


;;; ---------------------------------------------------------------------------
;;; STEP 2: Write layer list to Python bridge (needs DWG_PATH)
;;; ---------------------------------------------------------------------------
(defun hc_write_layer_bridge (dwg_path layer_list / pybridge
                                     names colors ltypes lws locked frozen on)
  (vl-load-com)

  ;; extract the lists safely (only one-level selectors)
  (setq names   (car  layer_list))
  (setq colors  (cadr layer_list))
  (setq ltypes  (caddr layer_list))
  (setq lws     (cadddr layer_list))
  (setq locked  (nth 4 layer_list))
  (setq frozen  (nth 5 layer_list))
  (setq on      (nth 6 layer_list))

  (setq pybridge (vlax-create-object "HydrauliCAD.JsonBridge"))

  ;; call JSON Bridge with seven arguments
  (vlax-invoke pybridge 'BuildLayerList
    dwg_path
    names
    colors
    ltypes
    lws
    locked
    frozen
    on
  )

  (vlax-release-object pybridge)

  (hc-log "✅ hc_write_layer_bridge → layer bridge JSON written successfully.")

  T
)



;;; ---------------------------------------------------------------------------
;;; STEP 3: MAIN COMMAND (must be a real AutoCAD command)
;;; ---------------------------------------------------------------------------
(defun C:HC_GETLAYERS ( / layers ac doc dwg_path )
  (hc-log "📄 HC_GETLAYERS started.")

  (setq ac  (vlax-get-acad-object))
  (setq doc (vla-get-ActiveDocument ac))
  (setq dwg_path (vla-get-FullName doc))

  ;; 1) Collect layers
  (setq layers (hc_get_layers_raw))

  ;; 2) Write bridge with correct DWG path
  (hc_write_layer_bridge dwg_path layers)

  (hc-log "📄 HC_GETLAYERS completed successfully.")
  (princ)
)
