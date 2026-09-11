# -*- coding: utf-8 -*-
"""Из опубликованной версии артефакта — обратно в проект:
artifact.html (то, что публикуется) и index.html (локальная читалка без слоя правки)."""
import io, re, sys

live = io.open(sys.argv[1], encoding='utf-8').read()
inner = re.search(r'<body[^>]*>(.*?)</body>', live, re.S).group(1).strip()

MARK = '/* ---------- Правка прямо на странице ---------- */'

# --- 1. artifact.html: тот же файл без обёртки документа, с починенной кнопкой ---
art = inner
art = art.replace('<button type="button" class="savebtn" id="savebtn" disabled="" hidden="">',
                  '<button type="button" class="savebtn" id="savebtn" hidden>')
old = '''    if ((x = c.querySelector("#savebtn")))   x.setAttribute("hidden", "");'''
new = '''    if ((x = c.querySelector("#savebtn"))){ x.setAttribute("hidden", ""); x.removeAttribute("disabled"); }'''
assert old in art
art = art.replace(old, new, 1)
old = '''  editbtn.addEventListener("click", function(){ setEditing(!editing); });'''
new = '''  savebtn.disabled = false;
  editbtn.addEventListener("click", function(){ setEditing(!editing); });'''
assert old in art
art = art.replace(old, new, 1)
io.open('artifact.html', 'w', encoding='utf-8').write(art + '\n')

# --- 2. index.html: полноценный документ, слой правки вырезан ---
title = re.search(r'<title>(.*?)</title>', art, re.S).group(1)
css   = re.search(r'<style>\n(.*?)\n</style>', art, re.S).group(1)
css   = css[:css.index(MARK)].rstrip()
body  = re.sub(r'^.*?</style>\n', '', art, count=1, flags=re.S)
body  = re.sub(r'\s*<div class="edit" id="edit".*?\n    </div>', '', body, count=1, flags=re.S)
body  = re.sub(r'\s*<script>\n/\* Правка прямо на странице.*?</script>', '', body, count=1, flags=re.S)
assert 'savebtn' not in body and 'class="edit"' not in body

doc = ('<!DOCTYPE html>\n<html lang="ru">\n<head>\n'
       '<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
       '<title>' + title + '</title>\n'
       '<meta name="description" content="Рабочая памятка модератора дискуссии с возможностью сравнить новую редакцию со старой.">\n'
       '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
       '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
       + re.search(r'<link href="https://fonts\.googleapis\.com/css2[^>]*>', art).group(0).replace('&amp;', '&') + '\n'
       '<style>\n' + css + '\n</style>\n</head>\n<body data-mode="new">\n'
       + body.strip() + '\n</body>\n</html>\n')
io.open('index.html', 'w', encoding='utf-8').write(doc)
print('artifact.html %d B, index.html %d B' % (len(art.encode('utf-8')), len(doc.encode('utf-8'))))
