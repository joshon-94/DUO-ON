/* 듀온 공통 모션: 스크롤 등장, 하트 순차 점등, 탭 리플.
   prefers-reduced-motion 이면 아무것도 하지 않는다. */
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) return;
  document.documentElement.classList.add('motion');

  // 1) 스크롤 등장: 같은 부모 안의 형제끼리 순서대로 살짝 늦게 나타난다
  var SELECTOR = [
    '.place-card', '.mag-tile', '.zodiac-chip', '.trip-day', '.fortune-card',
    '.tarot-result', '.tarot-draw', '.fortune-rank li', '.feature-card', '.mbti-card',
    '.tip-card', '.news-card', '.review-card', '.cmp-card', '.trip-info > div',
    '.mag-hero', '.section-title', '.mag-cta', '.mbti-result', '.match-card', '.card'
  ].join(',');
  var items = Array.prototype.slice.call(document.querySelectorAll(SELECTOR));
  if ('IntersectionObserver' in window && items.length) {
    var order = new Map();
    items.forEach(function (el) {
      var p = el.parentNode;
      var i = order.get(p) || 0;
      order.set(p, i + 1);
      el.classList.add('rv');
      el.style.setProperty('--rv-delay', Math.min(i % 12, 8) * 60 + 'ms');
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('rv-in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -24px 0px' });
    items.forEach(function (el) { io.observe(el); });
  }

  // 2) 연애운 하트: 한 개씩 톡톡 채워진다
  document.querySelectorAll('.fortune-hearts').forEach(function (box) {
    var txt = box.textContent.trim();
    box.textContent = '';
    Array.prototype.forEach.call(txt, function (ch, i) {
      var s = document.createElement('span');
      s.className = 'heart' + (ch === '♥' ? ' full' : '');
      s.textContent = ch;
      s.style.animationDelay = (250 + i * 120) + 'ms';
      box.appendChild(s);
    });
  });

  // 3) 버튼·카드 탭 리플
  document.addEventListener('pointerdown', function (e) {
    var t = e.target.closest('.btn, .chip, .tab, .zodiac-chip');
    if (!t) return;
    var r = t.getBoundingClientRect();
    var d = Math.max(r.width, r.height);
    var dot = document.createElement('span');
    dot.className = 'ripple';
    dot.style.width = dot.style.height = d + 'px';
    dot.style.left = (e.clientX - r.left - d / 2) + 'px';
    dot.style.top = (e.clientY - r.top - d / 2) + 'px';
    t.appendChild(dot);
    setTimeout(function () { dot.remove(); }, 600);
  }, { passive: true });

  // 4) 필터 칩 줄: 선택된 칩이 보이도록 가로 스크롤 위치 맞추기
  document.querySelectorAll('.filter-row').forEach(function (row) {
    var on = row.querySelector('.chip.active');
    if (!on || row.scrollWidth <= row.clientWidth) return;
    var rr = row.getBoundingClientRect(), cr = on.getBoundingClientRect();
    if (cr.right > rr.right - 24) {  // 화면 밖에 있을 때만 가운데로
      row.scrollLeft += (cr.left - rr.left) - (rr.width - cr.width) / 2;
    }
  });
})();
