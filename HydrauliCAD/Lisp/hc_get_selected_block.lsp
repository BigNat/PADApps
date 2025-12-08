(defun C:HC_GETBLOCKNAME ( / ac doc sel ent blkname pybridge )

  (vl-load-com)

  ;; Prompt user to select a block reference
  (setq sel (entsel "\nSelect block: "))
  (if (null sel)
    (progn
      (princ "\nNo block selected.")
      (princ)
      (exit)
    )
  )

  (setq ent (vlax-ename->vla-object (car sel)))

  ;; Validate block type (BLOCKREFERENCE)
  (if (not (= "AcDbBlockReference" (vla-get-ObjectName ent)))
    (progn
      (princ "\nSelected object is not a block.")
      (princ)
      (exit)
    )
  )

  ;; Extract block name
  (setq blkname (vla-get-Name ent))

  ;; Write JSON response
  (setq pybridge (vlax-create-object "HydrauliCAD.JsonBridge"))
  (vlax-invoke pybridge 'WriteKeyValue "block_name" blkname)
  (vlax-release-object pybridge)

  (princ)
)


(defun C:HC_GETBLOCKATTRS ( / sel ent hasAtt attlist attCol att name val 
                               pybridge tags vals dwg_path blkname)

  (vl-load-com)

  (hc-log "🔎 HC_GETBLOCKATTRS started...")

  ;; Select block
  (setq sel (entsel "\nSelect block: "))
  (if (null sel)
    (progn (hc-log "⚠️ No block selected.") (princ) (exit))
  )

  (setq ent (vlax-ename->vla-object (car sel)))
  (hc-log (strcat "🧱 Selected entity: " (vla-get-ObjectName ent)))

  ;; Must be block reference
  (if (not (= "AcDbBlockReference" (vla-get-ObjectName ent)))
    (progn (hc-log "❌ Not a block.") (princ) (exit))
  )

  ;; Block name
  (setq blkname (vla-get-Name ent))
  (hc-log (strcat "🔤 Block name: " blkname))

  ;; DWG path
  (setq dwg_path (getvar "DWGPREFIX"))
  (setq dwg_path (strcat dwg_path (getvar "DWGNAME")))
  (hc-log (strcat "📄 DWG path: " dwg_path))

  ;; Get attributes
  (setq hasAtt (vla-get-HasAttributes ent))
  (setq attlist '())

  (if (= hasAtt :vlax-true)
    (progn
      (hc-log "📥 Block has attributes — retrieving...")
      (setq attCol (vlax-invoke ent 'GetAttributes))

      (foreach att attCol
        (setq name (strcase (vla-get-TagString att)))
        (setq val (vla-get-TextString att))

        ;; basic cleaning
        (setq val (vl-string-subst "" "(" val))
        (setq val (vl-string-subst "" ")" val))
        (setq val (vl-string-subst "-" ";" val))

        ;; add to list as (name value)
        (setq attlist (cons (list name val) attlist))

        (hc-log (strcat "   → " name " = " val))
      )
    )
    (hc-log "ℹ️ Block has no attributes.")
  )

  ;; Convert nested list to two simple lists
  (setq tags (mapcar 'car attlist))
  (setq vals (mapcar 'cadr attlist))

  ;; Write JSON through JsonBridge
  (setq pybridge (vlax-create-object "HydrauliCAD.JsonBridge"))
  (vlax-invoke pybridge 'BuildBlockAttributeList dwg_path blkname tags vals)
  (vlax-release-object pybridge)

  (hc-log "💾 HC_GETBLOCKATTRS → attributes written via BuildBlockAttributeList.")
  (princ)
)
