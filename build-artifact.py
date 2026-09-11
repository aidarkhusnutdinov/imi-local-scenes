# -*- coding: utf-8 -*-
"""index.html -> artifact.html: снимает обёртку документа и добавляет слой правки."""
import io, re, sys

import os
D = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
src_path  = a[0] if len(a) > 0 else os.path.join(D, 'index.html')
out_path  = a[1] if len(a) > 1 else os.path.join(D, 'artifact.html')
css_path  = os.path.join(D, 'edit-layer', 'edit.css')
ctrl_path = os.path.join(D, 'edit-layer', 'controls.html')
js_path   = os.path.join(D, 'edit-layer', 'edit.js')
src = io.open(src_path, encoding='utf-8').read()

head = re.search(r'<head>(.*?)</head>', src, re.S).group(1)
body = re.search(r'<body[^>]*>(.*?)</body>', src, re.S).group(1)

title = re.search(r'<title>.*?</title>', head, re.S).group(0)
links = re.findall(r'<link [^>]*>', head)
style = re.search(r'<style>(.*?)</style>', head, re.S).group(1)

edit_css = io.open(css_path, encoding='utf-8').read()
controls = io.open(ctrl_path, encoding='utf-8').read()
edit_js = io.open(js_path, encoding='utf-8').read()

# кнопки правки — в панель, сразу после подсказки
body, n = re.subn(r'(<span class="hint" id="hint">.*?</span>)',
                  lambda m: m.group(1) + '\n' + controls.rstrip(), body, count=1, flags=re.S)
assert n == 1, 'не нашёл .hint для вставки кнопок'

out = (title + '\n'
       + '\n'.join(links) + '\n'
       + '<style>' + style.rstrip() + '\n' + edit_css.rstrip() + '\n</style>\n'
       + body.strip() + '\n\n'
       + edit_js.rstrip() + '\n')

io.open(out_path, 'w', encoding='utf-8').write(out)
print('%s: %d bytes, %d lines' % (out_path, len(out.encode('utf-8')), out.count('\n') + 1))
