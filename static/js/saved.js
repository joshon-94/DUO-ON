/* 데이트 장소 찜하기: 로그인 없이 브라우저(localStorage)에 id 목록을 저장한다. */
(function () {
  var KEY = 'duon_saved_places';

  function read() {
    try {
      var v = JSON.parse(localStorage.getItem(KEY) || '[]');
      return Array.isArray(v) ? v : [];
    } catch (e) { return []; }
  }
  function write(ids) {
    try { localStorage.setItem(KEY, JSON.stringify(ids)); } catch (e) {}
  }

  function paint(btn, on) {
    btn.classList.toggle('on', on);
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    var label = btn.querySelector('span');
    if (label) label.textContent = on ? '찜함' : '찜';
  }

  function updateCount() {
    var n = read().length;
    document.querySelectorAll('.saved-count').forEach(function (el) {
      el.textContent = n;
      el.hidden = n === 0;
    });
  }

  function burst(btn) {
    btn.classList.remove('burst');
    void btn.offsetWidth;  // 애니메이션 재시작
    btn.classList.add('burst');
    for (var i = 0; i < 6; i++) {
      var h = document.createElement('i');
      h.className = 'mini-heart';
      h.textContent = '♥';
      h.style.setProperty('--a', (i * 60 + Math.random() * 30) + 'deg');
      btn.appendChild(h);
      setTimeout(function (el) { el.remove(); }, 700, h);
    }
  }

  var api = {
    list: read,
    has: function (id) { return read().indexOf(id) !== -1; },
    toggle: function (id) {
      var ids = read();
      var i = ids.indexOf(id);
      var saved = i === -1;
      if (saved) ids.push(id); else ids.splice(i, 1);
      write(ids);
      updateCount();
      document.dispatchEvent(new CustomEvent('duon:saved-change', { detail: { id: id, saved: saved } }));
      return saved;
    },
    bind: function (root) {
      (root || document).querySelectorAll('[data-save]').forEach(function (btn) {
        paint(btn, api.has(btn.dataset.save));
      });
    }
  };
  window.DuonSaved = api;

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-save]');
    if (!btn) return;
    e.preventDefault();
    var on = api.toggle(btn.dataset.save);
    paint(btn, on);
    if (on) burst(btn);
  });

  document.addEventListener('DOMContentLoaded', function () {
    api.bind(document);
    updateCount();
  });
})();
