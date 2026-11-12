// Shared behaviour for every page.

// Footer year.
(function () {
  var y = document.getElementById('y');
  if (y) y.textContent = new Date().getFullYear();
})();

// arXiv feed. papers.json is rebuilt by .github/workflows/papers.yml and served
// from the same origin (the arXiv API does not send CORS headers, so we cannot
// call it from the browser). If the fetch fails, the static fallback in the HTML
// stays in place.
(function () {
  var box = document.getElementById('papers');
  if (!box) return;

  var esc = function (s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  var authors = function (list) {
    if (!list || !list.length) return '';
    return list.length === 1 ? list[0] : list[0] + ' et al.';
  };
  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var when = function (iso) {
    var parts = String(iso || '').split('-');
    if (parts.length !== 3 || !parts[0]) return iso || '';
    return Number(parts[2]) + ' ' + MONTHS[Number(parts[1]) - 1] + ' ' + parts[0];
  };

  fetch('/papers.json', { cache: 'no-store' })
    .then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.json();
    })
    .then(function (data) {
      if (!data.topics || !data.topics.length) return;

      var html = data.topics.map(function (t) {
        var papers = t.papers.map(function (p) {
          return '<li>' +
            '<a class="ptitle" href="' + esc(p.url) + '" target="_blank" rel="noopener">' + esc(p.title) + '</a>' +
            '<span class="pmeta">' + esc(when(p.published)) + ' · ' + esc(authors(p.authors)) + '</span>' +
            '</li>';
        }).join('');
        var more = 'https://arxiv.org/search/?searchtype=all&query=' +
          encodeURIComponent(t.name) + '&order=-announced_date_first';
        return '<div class="feed-group"><h3><span>' + esc(t.name) + '</span>' +
          '<a href="' + esc(more) + '" target="_blank" rel="noopener">more on arXiv ↗</a></h3>' +
          '<ul class="feed">' + papers + '</ul></div>';
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
