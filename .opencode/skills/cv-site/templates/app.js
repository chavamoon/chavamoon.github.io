// Generated site behaviour: year, language switch, active nav link.
// The page is fully readable without this file.

(function () {
  var years = [].slice.call(document.querySelectorAll('.js-year'));
  years.forEach(function (y) { y.textContent = new Date().getFullYear(); });
})();

(function () {
  var blocks = [].slice.call(document.querySelectorAll('[data-lang]'));
  var buttons = [].slice.call(document.querySelectorAll('[data-set-lang]'));
  var SUFFIX = { en: '', es: '-es' };

  var remapHash = function (lang) {
    var id = (location.hash || '').slice(1);
    if (!id || !blocks.length) return;
    var base = id.replace(/-es$/, '');
    var target = document.getElementById(base + SUFFIX[lang]);
    if (!target) return;
    if (target.id !== id) {
      try { history.replaceState(null, '', '#' + target.id); } catch (e) { /* ignore */ }
    }
  };

  var apply = function (lang) {
    if (lang !== 'es') lang = 'en';
    blocks.forEach(function (b) {
      b.hidden = b.getAttribute('data-lang') !== lang;
    });
    buttons.forEach(function (b) {
      var on = b.getAttribute('data-set-lang') === lang;
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    document.documentElement.lang = lang;
    remapHash(lang);
    try { localStorage.setItem('site:lang', lang); } catch (e) { /* ignore */ }
  };

  buttons.forEach(function (b) {
    b.addEventListener('click', function () { apply(b.getAttribute('data-set-lang')); });
  });

  if (buttons.length) {
    var saved = 'en';
    try { saved = localStorage.getItem('site:lang') || 'en'; } catch (e) { /* ignore */ }
    apply(saved);
  }
})();

(function () {
  var links = [].slice.call(document.querySelectorAll('.nav a[href^="#"]'));
  if (!links.length || !('IntersectionObserver' in window)) return;

  var byId = {};
  links.forEach(function (a) {
    var id = a.getAttribute('href').slice(1);
    if (id) byId[id] = a;
  });

  var spy = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      var a = byId[entry.target.id];
      if (!a) return;
      links.forEach(function (l) { l.classList.remove('on'); });
      a.classList.add('on');
    });
  }, { rootMargin: '-45% 0px -50% 0px' });

  Object.keys(byId).forEach(function (id) {
    var el = document.getElementById(id);
    if (el) spy.observe(el);
  });
})();
