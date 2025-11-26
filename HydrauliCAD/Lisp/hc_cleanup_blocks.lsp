

;;; -----------------------------
;;; hc_cleanup_blocks.lsp
;;; -----------------------------
(defun c:HC_DELETEBLOCKS ( / blk ss)
  (setq blk (getstring "Enter block name to delete: "))
  (hc-log (strcat "🧹 DeleteBlocks → " blk))
  (setq ss (ssget "X" (list (cons 0 "INSERT") (cons 2 blk))))
  (if ss
    (repeat (sslength ss)
      (setq e (ssname ss 0))
      (entdel e)
      (ssdel e ss)
    )
  )
  (hc-log "✅ DeleteBlocks completed.")
  (princ)
)
