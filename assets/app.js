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

/* ---------- language toggle (nd page) ---------- */
(function () {
  var blocks = [].slice.call(document.querySelectorAll('[data-lang]'));
  if (!blocks.length) return;

  var buttons = [].slice.call(document.querySelectorAll('[data-lang-set]'));
  var KEY = 'nd:lang';

  var apply = function (lang) {
    if (lang !== 'es') lang = 'en';
    blocks.forEach(function (b) {
      b.hidden = b.getAttribute('data-lang') !== lang;
    });
    buttons.forEach(function (b) {
      var on = b.getAttribute('data-lang-set') === lang;
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    document.documentElement.lang = lang;
    try { localStorage.setItem(KEY, lang); } catch (e) { /* ignore */ }
  };

  buttons.forEach(function (b) {
    b.addEventListener('click', function () { apply(b.getAttribute('data-lang-set')); });
  });

  var saved = 'en';
  try { saved = localStorage.getItem(KEY) || 'en'; } catch (e) { /* ignore */ }
  apply(saved);
})();

/* ---------- nd notes (nd.json) ---------- */
(function () {
  var boxes = [].slice.call(document.querySelectorAll('[data-notes]'));
  if (!boxes.length) return;

  getJSON('/nd.json')
    .then(function (data) {
      var notes = data.notes || [];
      if (!notes.length) return;

      boxes.forEach(function (box) {
        var lang = box.getAttribute('data-notes') === 'es' ? 'es' : 'en';
        box.innerHTML = '<ul class="feed notes">' + notes.map(function (n) {
          var text = lang === 'es' ? (n.es || n.en) : (n.en || n.es);
          var item = n.url
            ? '<a class="ptitle" href="' + esc(n.url) + '" target="_blank" rel="noopener">' + esc(text) + '</a>'
            : '<span class="ptitle">' + esc(text) + '</span>';
          return '<li>' + item + '<span class="pmeta">' + esc(when(n.date)) + '</span></li>';
        }).join('') + '</ul>';
      });
    })
    .catch(function () { /* keep the static fallback */ });
})();

/* ---------- console signature ---------- */
(function () {
  var tag = 'background:#0d1117;color:#58a6ff;font:600 12px/1 ui-monospace,monospace;padding:5px 8px;border-radius:4px';
  var plain = 'color:#c9d1d9;font:12px/1.6 ui-monospace,monospace';
  var muted = 'color:#8b949e;font:12px/1.6 ui-monospace,monospace';

  console.log('%c// salvador luna', tag);
  console.log('%cAI Engineer · Guadalajara, MX', muted);
  console.log('%cyou opened the console. of course you did.', plain);
  console.log('%ctry: whoami()   hire()   or \u2191\u2191\u2193\u2193\u2190\u2192\u2190\u2192BA', muted);

  window.whoami = function () {
    console.log('%cAI Engineer \u2014 agents, tool use, MCP, retrieval, evaluation.', plain);
    return 'salvador luna';
  };
  window.hire = function () {
    console.log('%csalvadorlunahdz@hotmail.com', 'color:#58a6ff;font:12px/1.6 ui-monospace,monospace');
    console.log('%cgithub.com/chavamoon \u00b7 linkedin.com/in/salvadorlunahdz', muted);
    return 'say hi';
  };
})();

/* ---------- tab title on blur ---------- */
(function () {
  var base = document.title;
  var fileEl = document.querySelector('.file');
  var label = fileEl && fileEl.textContent.trim() ? fileEl.textContent.trim() : base;
  var away = false;

  var setAway = function (on) {
    if (on === away) return;
    away = on;
    document.title = on ? '\u25cf ' + label + ' \u2014 1 unread' : base;
  };

  window.addEventListener('blur', function () { setAway(true); });
  window.addEventListener('focus', function () { setAway(false); });
  document.addEventListener('visibilitychange', function () { setAway(document.hidden); });
})();

/* ---------- easter egg: the agent ---------- */
(function () {
  var KEY = 'egg:agent';
  try {
    if (sessionStorage.getItem(KEY)) return;
  } catch (e) { /* private mode: just let it play */ }

  var SPRITE =
    '<svg viewBox="0 0 12 16" shape-rendering="crispEdges" aria-hidden="true">' +
      '<rect x="5" y="0" width="2" height="1" fill="#58a6ff"/>' +
      '<rect x="5" y="1" width="2" height="1" fill="#30363d"/>' +
      '<rect x="2" y="2" width="8" height="5" fill="#e6edf3"/>' +
      '<rect x="3" y="3" width="6" height="3" fill="#0d1117"/>' +
      '<rect x="4" y="4" width="1" height="1" fill="#58a6ff"/>' +
      '<rect x="7" y="4" width="1" height="1" fill="#58a6ff"/>' +
      '<rect x="5" y="7" width="2" height="1" fill="#8b949e"/>' +
      '<rect x="1" y="8" width="1" height="3" fill="#1f6feb"/>' +
      '<rect x="10" y="8" width="1" height="3" fill="#1f6feb"/>' +
      '<rect x="2" y="8" width="8" height="4" fill="#1f6feb"/>' +
      '<rect x="5" y="9" width="2" height="1" fill="#0d1117"/>' +
      '<rect x="3" y="12" width="2" height="2" fill="#8b949e"/>' +
      '<rect x="7" y="12" width="2" height="2" fill="#8b949e"/>' +
      '<rect x="2" y="14" width="3" height="2" fill="#ff5f57"/>' +
      '<rect x="7" y="14" width="3" height="2" fill="#ff5f57"/>' +
    '</svg>';

  var BLOCKS = [24, 48, 72];
  var running = false;
  var played = false;
  var stage, carrier, sprite, bubble, textEl, banner, branch;

  var wait = function (ms) {
    return new Promise(function (done) { setTimeout(done, ms); });
  };

  var setStatus = function () {
    var foot = document.querySelector('footer.status');
    if (foot) document.documentElement.style.setProperty('--status-h', foot.offsetHeight + 'px');
  };

  var say = function (text, hold) {
    return new Promise(function (done) {
      var i = 0;
      bubble.hidden = false;
      textEl.textContent = '';
      var tick = function () {
        textEl.textContent = text.slice(0, i++);
        if (i <= text.length) setTimeout(tick, 14);
        else setTimeout(done, hold);
      };
      tick();
    });
  };

  var move = function (pct, offset) {
    offset = offset === undefined ? -24 : offset;
    var width = window.innerWidth;
    var center = (pct / 100) * width + offset + 24;
    var bubbleWidth = Math.min(252, width * 0.72);
    var edge = Math.min(Math.max(center - bubbleWidth / 2, 8), width - bubbleWidth - 8);

    carrier.style.left = 'calc(' + pct + '% + ' + offset + 'px)';
    bubble.style.left = (edge - (center - 24)) + 'px';
    return wait(720);
  };

  var hop = function () {
    sprite.classList.add('hop');
    return wait(620).then(function () { sprite.classList.remove('hop'); });
  };

  var bump = function (block) {
    block.classList.add('hit');
    block.textContent = '\u25a3';
    var coin = document.createElement('b');
    coin.className = 'coin';
    coin.style.left = block.style.left;
    stage.appendChild(coin);
    setTimeout(function () { coin.remove(); }, 900);
  };

  var build = function () {
    stage = document.createElement('div');
    stage.className = 'agent-stage';
    stage.setAttribute('aria-hidden', 'true');
    stage.innerHTML =
      '<div class="agent-carrier">' +
        '<div class="agent-bubble" hidden><span class="agent-text"></span><i class="agent-caret"></i></div>' +
        '<div class="agent-sprite">' + SPRITE + '</div>' +
      '</div>' +
      '<div class="agent-blocks">' +
        BLOCKS.map(function (x) {
          return '<i class="qblock" style="left:' + x + '%">?</i>';
        }).join('') +
      '</div>' +
      '<div class="agent-banner" hidden></div>';

    document.body.appendChild(stage);

    carrier = stage.querySelector('.agent-carrier');
    sprite = stage.querySelector('.agent-sprite');
    bubble = stage.querySelector('.agent-bubble');
    textEl = stage.querySelector('.agent-text');
    banner = stage.querySelector('.agent-banner');
    setStatus();
    requestAnimationFrame(function () { stage.classList.add('on'); });
  };

  var finish = function (started) {
    stage.classList.remove('on');
    setTimeout(function () {
      stage.remove();
      if (branch) branch.textContent = 'main';
      console.log('%c// agent: done in ' + ((Date.now() - started) / 1000).toFixed(1) + 's',
        'color:#8b949e;font:12px/1.6 ui-monospace,monospace');
      running = false;
    }, 320);
  };

  var run = async function () {
    if (running || played) return;
    running = true;
    played = true;
    try { sessionStorage.setItem(KEY, '1'); } catch (e) { /* ignore */ }

    var started = Date.now();
    build();
    branch = document.querySelector('footer.status .branch');
    if (branch) branch.textContent = 'feat/agent-mode';
    console.log('%c// agent: run started', 'color:#8b949e;font:12px/1.6 ui-monospace,monospace');

    var calm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (calm) {
      banner.hidden = false;
      banner.innerHTML = '<b>context complete</b> \u2014 nothing hallucinated.';
      await wait(3200);
      finish(started);
      return;
    }

    await move(14);
    await say('plan: find the easter egg', 420);
    await say('act: grep -r "easter" .', 440);
    await say('observe: 1 hit \u2014 this page', 440);
    await say('plan: collect 3 tokens', 380);

    var blocks = [].slice.call(stage.querySelectorAll('.qblock'));
    for (var i = 0; i < blocks.length; i++) {
      await move(BLOCKS[i], -61);
      await hop();
      bump(blocks[i]);
      await say('observe: token ' + (i + 1) + '/3', 260);
    }

    banner.hidden = false;
    bubble.hidden = true;
    banner.innerHTML = '<b>context complete</b> \u2014 nothing hallucinated.';
    await wait(2100);
    banner.hidden = true;

    await move(112);
    finish(started);
  };

  /* Konami code */
  var CODE = ['arrowup', 'arrowup', 'arrowdown', 'arrowdown',
              'arrowleft', 'arrowright', 'arrowleft', 'arrowright', 'b', 'a'];
  var buffer = [];
  window.addEventListener('keydown', function (event) {
    if (event.repeat) return;
    buffer.push((event.key || '').toLowerCase());
    if (buffer.length > CODE.length) buffer.shift();
    if (buffer.join(',') === CODE.join(',')) {
      buffer.length = 0;
      run();
    }
  });

  /* mobile: three taps on the photo */
  var taps = 0;
  var tapTimer;
  [].slice.call(document.querySelectorAll('.photo, .avatar')).forEach(function (el) {
    el.addEventListener('click', function () {
      taps += 1;
      clearTimeout(tapTimer);
      tapTimer = setTimeout(function () { taps = 0; }, 1200);
      if (taps >= 3) {
        taps = 0;
        run();
      }
    });
  });

  window.addEventListener('resize', function () {
    if (stage) setStatus();
  });
})();
