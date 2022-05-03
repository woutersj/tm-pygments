
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;
;; MODULE      : init-pygments.scm
;; DESCRIPTION : Initialize the 'pygments' plugin
;; COPYRIGHT   : (C) 2021  Darcy Shen, Jeroen Wouters
;;
;; This software falls under the GNU general public license version 3 or later.
;; It comes WITHOUT ANY WARRANTY WHATSOEVER. For details, see the file LICENSE
;; in the root directory or <http://www.gnu.org/licenses/gpl-3.0.html>.
;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (pygments-serialize lan t)
    (with u (pre-serialize lan t)
      (with s (texmacs->code (stree->tree u) "SourceCode")
        (string-append  s  "\n<EOF>\n"))))

(define (python-utf8-command) (string-append (python-command) " -X utf8 "))

(define (python-launcher)
  (if (url-exists? "$TEXMACS_HOME_PATH/plugins/pygments")
      (string-append (python-utf8-command) " \""
                     (getenv "TEXMACS_HOME_PATH")
                     "/plugins/pygments/src/tm-pygments.py\"")
      (string-append (python-utf8-command) " \""
                     (getenv "TEXMACS_PATH")
                     "/plugins/pygments/src/tm-pygments.py\"")))

(plugin-configure pygments
  (:winpath "python*" ".")
  (:winpath "Python*" ".")
  (:winpath "Python/Python*" ".")
  (:require (url-exists-in-path? (python-command)))
  (:require (== ""
      (eval-system (string-append (python-command) " -c \"import pygments\""))))
  (:launch ,(python-launcher))
  (:serializer ,pygments-serialize)
  (:session "Pygments")
  (:scripts "Pygments"))
