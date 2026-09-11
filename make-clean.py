# -*- coding: utf-8 -*-
"""Чистая памятка: из опубликованной версии артефакта, без машинерии сравнения."""
import io, re, sys

src = io.open(sys.argv[1], encoding='utf-8').read()
out_path = sys.argv[2]

title = re.search(r'<title>(.*?)</title>', src, re.S).group(1)
links = [l for l in re.findall(r'<link [^>]*>', src) if 'fonts.g' in l]
css   = re.search(r'<style>\n(.*?)\n</style>', src, re.S).group(1)
body  = re.search(r'<body[^>]*>(.*?)</body>', src, re.S).group(1)
# в артефакте title/link/style лежат внутри body — в новом документе они уедут в head
body  = re.sub(r'^.*?</style>\n', '', body, count=1, flags=re.S)

def cut(pattern, text, flags=re.S, expect=None):
    text, n = re.subn(pattern, '', text, flags=flags)
    if expect is not None:
        assert n == expect, 'ожидал %s вырезаний по %r, вышло %d' % (expect, pattern[:40], n)
    return text

# --- разметка -------------------------------------------------------------
body = cut(r'<div class="bar">.*?\n</div>\n', body, expect=1)          # переключатель режимов
body = cut(r'<div class="summary">.*?\n</div>\n\n', body, expect=1)     # «что изменилось» целиком
body = cut(r'<div id="oldside">.*?\n</div>\n\n', body, expect=1)        # старая редакция целиком
body = cut(r'\s*<details class="old">.*?</details>', body, expect=6)    # старая редакция по блокам
body = cut(r'\s*<div class="old none">.*?</div>', body, expect=4)       # «в старом плане этого не было»
body = cut(r'\s*<div class="changed">.*?</div>', body, expect=10)       # плашки «что изменилось»
body = cut(r'\s*<script>.*?</script>', body, expect=2)                  # режимы + слой правки
body = cut(r'<div id="newside">\n', body, expect=1)
body = re.sub(r'\n</div>\n\n<footer>', '\n<footer>', body, count=1)     # закрывашка #newside

# --- блок 2: подводку про Бориса оформляем вопросом ----------------------
old_p = ('<p>Начинаем с Бориса и разбираем конкретное небольшое событие: доходы, расходы, '
         'кто получает оплату,\nкто несёт риск и что позволяет проводить его регулярно. '
         'Затем Тёма дополняет со стороны артиста.</p>')
new_p = ('<blockquote>Начинаем с Бориса и разбираем конкретное небольшое событие: доходы, расходы,\n'
         'кто получает оплату, кто несёт риск и что позволяет проводить его регулярно.</blockquote>\n'
         '<p>Затем Тёма дополняет со стороны артиста.</p>')
assert old_p in body, 'не нашёл абзац про Бориса'
body = body.replace(old_p, new_p, 1)

# --- CSS: выкидываем правила, которым больше нечего оформлять ------------
for a, b in [('/* ---------- Переключатель режимов ---------- */', '/* ---------- Шапка ---------- */'),
             ('/* ---------- Сводка изменений ---------- */',      '/* ---------- Блоки ---------- */'),
             ('/* ---------- Плашка «что изменилось» ---------- */', '/* ---------- Старая редакция ---------- */'),
             ('/* ---------- Старая редакция ---------- */',       '/* ---------- Режимы ---------- */'),
             ('/* ---------- Режимы ---------- */',                '.legend{')]:
    i, j = css.index(a), css.index(b)
    css = css[:i] + css[j:]
css = '\n'.join([l for l in css.split('\n') if '.legend' not in l])
css = css[:css.index('/* ---------- Правка прямо на странице ---------- */')]  # слой правки — только в артефакте
css = cut(r'  \.time\{.*?\n  \}\n', css, expect=1)                      # хронометраж был только в старой редакции
css = cut(r'\n *\.bar\{padding:9px 18px\}', css, expect=1)
css = cut(r'\n *\.summary\{padding:20px 18px\}', css, expect=1)
css = cut(r'\n *\.oldbody\{padding-left:16px; padding-right:16px\}', css, expect=1)
css = cut(r'\n *\.bar\{display:none\} ', css, expect=1)
css = cut(r'\n *details\.old\{display:none\}', css, expect=1)
css = css.replace('    .body{box-shadow:none}', '    .body{box-shadow:none}')
css = re.sub(r'\n{3,}', '\n\n', css)

doc = ('<!DOCTYPE html>\n<html lang="ru">\n<head>\n'
       '<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
       '<title>' + title + '</title>\n'
       '<meta name="description" content="Рабочая памятка модератора дискуссии «Как развивать музыкальную сцену в регионах», ИМИ.Конференция 2026.">\n'
       '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
       '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
       + [l for l in links if 'css2' in l][0].replace('&amp;', '&') + '\n'
       '<style>\n' + css.rstrip() + '\n</style>\n</head>\n<body>\n'
       + body.strip() + '\n</body>\n</html>\n')

io.open(out_path, 'w', encoding='utf-8').write(doc)
print('%s: %d bytes' % (out_path, len(doc.encode('utf-8'))))
