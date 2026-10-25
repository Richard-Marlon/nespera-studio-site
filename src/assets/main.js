(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Menu móvel
  var btn = document.querySelector(".menu-btn"), nav = document.getElementById("nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && nav.classList.contains("open")) {
        nav.classList.remove("open"); btn.setAttribute("aria-expanded", "false"); btn.focus();
      }
    });
  }

  // Único movimento da página: a linha datilografada do topo
  var t = document.querySelector(".typing");
  if (t && !reduce) {
    var full = t.getAttribute("data-text"), i = 0;
    t.setAttribute("aria-label", full);
    t.textContent = "";
    (function step() {
      t.textContent = full.slice(0, ++i);
      if (i < full.length) setTimeout(step, full[i - 1] === "," ? 260 : 45);
    })();
  }

  // Filtros e busca da vitrine
  var lista = document.getElementById("lista");
  if (lista) {
    var cards = [].slice.call(lista.querySelectorAll(".item"));
    var chips = [].slice.call(document.querySelectorAll(".chip"));
    var busca = document.getElementById("busca"), nada = document.getElementById("nada");
    var cat = "";
    function apply() {
      var q = busca ? busca.value.trim().toLowerCase() : "", n = 0;
      cards.forEach(function (c) {
        var ok = (!cat || c.dataset.cat === cat) && (!q || c.dataset.busca.indexOf(q) > -1);
        c.hidden = !ok; if (ok) n++;
      });
      if (nada) nada.hidden = n > 0;
    }
    chips.forEach(function (ch) {
      ch.addEventListener("click", function () {
        cat = ch.dataset.filter;
        chips.forEach(function (o) { o.setAttribute("aria-pressed", String(o === ch)); });
        apply();
      });
    });
    if (busca) busca.addEventListener("input", apply);
  }

  // Validação dos formulários (o envio real é feito pelo Netlify Forms)
  var msgs = {
    valueMissing: "Preencha este campo.",
    typeMismatch: "Digite um e-mail válido, como nome@exemplo.com.",
    tooShort: "Escreva um pouco mais."
  };
  function check(f) {
    var err = f.type === "checkbox"
      ? f.closest("form").querySelector(".err-check")
      : f.closest(".field") && f.closest(".field").querySelector(".err");
    var m = "";
    if (!f.validity.valid) {
      if (f.type === "checkbox") m = "Marque a autorização para continuar.";
      else m = f.validity.valueMissing ? msgs.valueMissing : f.validity.typeMismatch ? msgs.typeMismatch :
        f.validity.tooShort ? msgs.tooShort : "Confira este campo.";
    }
    f.setAttribute("aria-invalid", m ? "true" : "false");
    if (err) err.textContent = m;
    return !m;
  }
  [].forEach.call(document.querySelectorAll("form.form"), function (form) {
    var fields = [].slice.call(form.querySelectorAll("[required]"));
    fields.forEach(function (f) {
      f.addEventListener(f.type === "checkbox" || f.tagName === "SELECT" ? "change" : "blur", function () { check(f); });
    });
    form.addEventListener("submit", function (ev) {
      var first = null;
      fields.forEach(function (f) { if (!check(f) && !first) first = f; });
      if (first) { ev.preventDefault(); first.focus(); return; }
      var b = form.querySelector("button[type=submit]");
      if (b) { b.disabled = true; b.textContent = "Enviando..."; }
    });
  });
  // Se a pessoa voltar pelo histórico, reativa o botão
  window.addEventListener("pageshow", function () {
    [].forEach.call(document.querySelectorAll("form.form button[disabled]"), function (b) {
      b.disabled = false; b.textContent = b.closest("form").name === "contato" ? "Enviar mensagem" : "Avisar no lançamento";
    });
  });

  // Google Analytics 4 só após consentimento (só ativo se ga4_id estiver configurado)
  var id = document.body.getAttribute("data-ga4"), box = document.querySelector(".consent");
  function loadGA() {
    var s = document.createElement("script");
    s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(id);
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date()); window.gtag("config", id, { anonymize_ip: true });
  }
  if (id && box) {
    var pref = null;
    try { pref = localStorage.getItem("nespera-consent"); } catch (e) {}
    if (pref === "yes") loadGA();
    else if (pref !== "no") box.hidden = false;
    box.addEventListener("click", function (ev) {
      var v = ev.target.getAttribute("data-consent");
      if (!v) return;
      try { localStorage.setItem("nespera-consent", v); } catch (e) {}
      box.hidden = true;
      if (v === "yes") loadGA();
    });
  }
})();
