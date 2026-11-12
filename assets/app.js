// Shared behaviour for every page.

/* ---------- footer year ---------- */
(function () {
  var y = document.getElementById('y');
  if (y) y.textContent = new Date().getFullYear();
})();

/* ---------- helpers ---------- */
var esc = function (s) {
  return String(s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  });
};
var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
var when = function (iso) {
  var parts = String(iso || '').split('-');
  if (parts.length !== 3 || !parts[0]) return iso || '';
  return Number(parts[2]) + ' ' + MONTHS[Number(parts[1]) - 1] + ' ' + parts[0];
};
var getJSON = function (url) {
  return fetch(url, { cache: 'no-store' }).then(function (res) {
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return res.json();
  });
};

/* ---------- radar tabs ---------- */
(function () {
  var tabs = [].slice.call(document.querySelectorAll('.tab[data-panel]'));
  if (!tabs.length) return;

  var show = function (name, syncHash) {
    var known = tabs.some(function (t) { return t.dataset.panel === name; });
    if (!known) name = tabs[0].dataset.panel;

    tabs.forEach(function (t) {
      var on = t.dataset.panel === name;
      t.classList.toggle('on', on);
      t.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    [].slice.call(document.querySelectorAll('.panel')).forEach(function (p) {
      p.hidden = p.id !== 'panel-' + name;
    });
    if (syncHash && location.hash !== '#' + name) {
      history.replaceState(null, '', '#' + name);
    }
  };

  tabs.forEach(function (t) {
    t.addEventListener('click', function () { show(t.dataset.panel, true); });
  });
  window.addEventListener('hashchange', function () {
    show((location.hash || '').replace('#', ''), false);
  });
  show((location.hash || '').replace('#', ''), false);
})();

/* ---------- news feed (news.json) ---------- */
(function () {
  var box = document.getElementById('news');
  if (!box) return;

  getJSON('/news.json')
    .then(function (data) {
      if (!data.items || !data.items.length) return;
      box.innerHTML = '<ul class="feed">' + data.items.map(function (item) {
        return '<li>' +
          '<a class="ptitle" href="' + esc(item.url) + '" target="_blank" rel="noopener">' + esc(item.title) + '</a>' +
          '<span class="pmeta">' + esc(item.source) + ' · ' + esc(when(item.published)) + '</span>' +
          '</li>';
      }).join('') + '</ul>';
    })
    .catch(function () { /* keep the static fallback */ });
})();

/* ---------- arXiv feed (papers.json) ---------- */
(function () {
  var box = document.getElementById('papers');
  if (!box) return;

  var authors = function (list) {
    if (!list || !list.length) return '';
    return list.length === 1 ? list[0] : list[0] + ' et al.';
  };

  getJSON('/papers.json')
    .then(function (data) {
      if (!data.topics || !data.topics.length) return;

      var html = data.topics.map(function (t) {
        var rows = t.papers.map(function (p) {
          return '<li>' +
            '<a class="ptitle" href="' + esc(p.url) + '" target="_blank" rel="noopener">' + esc(p.title) + '</a>' +
            '<span class="pmeta">' + esc(when(p.published)) + ' · ' + esc(authors(p.authors)) + '</span>' +
            '</li>';
        }).join('');
        var more = 'https://arxiv.org/search/?searchtype=all&query=' +
          encodeURIComponent(t.name) + '&order=-announced_date_first';
        return '<div class="feed-group"><h3><span>' + esc(t.name) + '</span>' +
          '<a href="' + esc(more) + '" target="_blank" rel="noopener">more on arXiv ↗</a></h3>' +
          '<ul class="feed">' + rows + '</ul></div>';
      }).join('');

      html += '<div class="feed-group"><h3><span>Keep browsing</span></h3><ul class="feed">' +
        '<li><a class="ptitle" href="https://arxiv.org/list/cs.AI/recent" target="_blank" rel="noopener">Everything new in cs.AI</a>' +
        '<span class="pmeta">arxiv.org/list/cs.AI/recent</span></li>' +
        '<li><a class="ptitle" href="https://arxiv.org/list/cs.MA/recent" target="_blank" rel="noopener">Multi-agent systems</a>' +
        '<span class="pmeta">arxiv.org/list/cs.MA/recent</span></li>' +
        '</ul></div>';

      box.innerHTML = html;
    })
    .catch(function () { /* keep the static fallback */ });
})();
