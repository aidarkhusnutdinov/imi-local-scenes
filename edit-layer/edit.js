<script>
/* Правка прямо на странице. Работает только в опубликованном артефакте:
   локально window.claude нет, и страница остаётся просто читалкой. */
(function(){
  var body     = document.body;
  var ui       = document.getElementById("edit");
  var editbtn  = document.getElementById("editbtn");
  var savebtn  = document.getElementById("savebtn");
  var statusEl = document.getElementById("editstate");
  var art = null, editing = false, dirty = false;

  var SEL = ".wrap h1, .wrap h2, .wrap p, .wrap li, .wrap blockquote, .wrap .changed, .wrap .meta span";

  function say(t){ statusEl.textContent = t || ""; }

  function targets(){
    return Array.prototype.filter.call(document.querySelectorAll(SEL), function(n){
      return !n.closest("details.old") && !n.closest("footer") && !n.closest(".bar");
    });
  }

  function setEditing(on){
    editing = on;
    body.classList.toggle("editing", on);
    editbtn.setAttribute("aria-pressed", String(on));
    savebtn.hidden = !on;
    targets().forEach(function(n){
      if (on){ n.setAttribute("contenteditable", "true"); n.setAttribute("spellcheck", "true"); }
      else   { n.removeAttribute("contenteditable"); n.removeAttribute("spellcheck"); }
    });
    if (on) say("Правь текст прямо на странице. ⌘S — сохранить.");
    else say(dirty ? "Есть несохранённые правки." : "");
  }

  /* Состояние страницы в покое: без режима правки, без рабочих атрибутов. */
  function serialize(){
    var c = document.documentElement.cloneNode(true);
    var cbody = c.querySelector("body");
    if (cbody) cbody.classList.remove("editing");
    c.querySelectorAll("[contenteditable]").forEach(function(n){
      n.removeAttribute("contenteditable"); n.removeAttribute("spellcheck");
    });
    c.querySelectorAll("details.old").forEach(function(d){ d.removeAttribute("open"); });
    var x;
    if ((x = c.querySelector("#edit")))      x.setAttribute("hidden", "");
    if ((x = c.querySelector("#savebtn"))){ x.setAttribute("hidden", ""); x.removeAttribute("disabled"); }
    if ((x = c.querySelector("#editbtn")))   x.setAttribute("aria-pressed", "false");
    if ((x = c.querySelector("#editstate"))) x.textContent = "";
    return "<!DOCTYPE html>\n" + c.outerHTML;
  }

  function save(){
    if (!art || savebtn.disabled) return;
    savebtn.disabled = true;
    say("Сохраняю…");
    art.publish(serialize()).then(function(){
      dirty = false;
      say("Сохранено");
    }, function(e){
      var code = e && e.code;
      if (code === "conflict") say("Кто-то сохранил раньше — страница сейчас обновится.");
      else if (code === "not_granted" || code === "not_writer"){
        say("Здесь можно только читать.");
        setEditing(false);
        ui.hidden = true;
      }
      else say("Не сохранилось: " + ((e && e.message) || "неизвестная ошибка") + ". Попробуй ещё раз.");
    }).then(function(){ savebtn.disabled = false; });
  }

  savebtn.disabled = false;
  editbtn.addEventListener("click", function(){ setEditing(!editing); });
  savebtn.addEventListener("click", save);

  document.addEventListener("input", function(){
    if (!editing) return;
    dirty = true;
    say("Не сохранено. ⌘S — сохранить.");
  });

  /* Enter — перевод строки внутри абзаца, чтобы разметка не рассыпалась. */
  document.addEventListener("keydown", function(e){
    if ((e.metaKey || e.ctrlKey) && (e.key === "s" || e.key === "S")){
      e.preventDefault();
      if (editing) save();
      return;
    }
    if (!editing) return;
    if (e.key === "Escape"){ setEditing(false); return; }
    if (e.key === "Enter" && !e.shiftKey && e.target && e.target.isContentEditable){
      e.preventDefault();
      document.execCommand("insertLineBreak");
    }
  });

  /* Вставка — только текст, без чужих шрифтов и цветов. */
  document.addEventListener("paste", function(e){
    if (!editing || !e.target || !e.target.isContentEditable) return;
    var t = (e.clipboardData || window.clipboardData).getData("text/plain");
    e.preventDefault();
    document.execCommand("insertText", false, t.replace(/\s*\n\s*/g, " "));
  });

  window.addEventListener("beforeunload", function(e){
    if (!dirty) return;
    e.preventDefault();
    e.returnValue = "";
  });

  if (window.claude && window.claude.use){
    Promise.resolve(window.claude.use("artifact")).then(function(a){
      if (!a) return;
      art = a;
      ui.hidden = false;
    }, function(){});
  }
})();
</script>
