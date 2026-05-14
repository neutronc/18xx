(function () {
  'use strict';

  /* ---- helpers ---- */

  function headingText(h) {
    // text nodes only — excludes injected anchor-link elements
    return Array.from(h.childNodes)
      .filter(function (n) { return n.nodeType === 3; })
      .map(function (n) { return n.textContent; })
      .join('').trim();
  }

  function flashClass(el, cls, ms) {
    el.classList.add(cls);
    setTimeout(function () { el.classList.remove(cls); }, ms || 1500);
  }

  function copyText(text, onDone) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(onDone).catch(function () {});
    } else {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.cssText = 'position:fixed;opacity:0';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); onDone(); } catch (e) {}
      document.body.removeChild(ta);
    }
  }

  /* ---- 1. Copy buttons ---- */

  function initCopyButtons() {
    document.querySelectorAll('pre').forEach(function (pre) {
      var wrap = document.createElement('div');
      wrap.className = 'pre-wrap';
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(pre);

      var btn = document.createElement('button');
      btn.className = 'copy-btn';
      btn.setAttribute('aria-label', 'Copy code');
      btn.textContent = 'Copy';
      wrap.appendChild(btn);

      btn.addEventListener('click', function () {
        var code = pre.querySelector('code');
        copyText((code || pre).textContent, function () {
          btn.textContent = 'Copied!';
          flashClass(btn, 'copied', 2000);
          setTimeout(function () { btn.textContent = 'Copy'; }, 2000);
        });
      });
    });
  }

  /* ---- 2. Heading anchor links ---- */

  function initAnchorLinks() {
    var article = document.querySelector('article');
    if (!article) return;
    article.querySelectorAll('h2[id], h3[id], h4[id]').forEach(function (h) {
      var a = document.createElement('a');
      a.className = 'anchor-link';
      a.href = '#' + h.id;
      a.setAttribute('aria-label', 'Link to this section');
      a.textContent = '\u00a7';
      h.appendChild(a);
      a.addEventListener('click', function (e) {
        e.preventDefault();
        history.pushState(null, '', '#' + h.id);
        copyText(location.href, function () { flashClass(a, 'anchor-copied'); });
      });
    });
  }

  /* ---- 3. Floating TOC ---- */

  function initTOC() {
    var article = document.querySelector('article');
    if (!article) return;
    var headings = Array.from(article.querySelectorAll('h2[id], h3[id]'));
    if (headings.length < 3) return;

    /* build panel */
    var nav = document.createElement('nav');
    nav.id = 'toc';
    nav.setAttribute('aria-label', 'Page contents');

    var hdr = document.createElement('div');
    hdr.className = 'toc-header';
    hdr.textContent = 'Contents';
    nav.appendChild(hdr);

    var ul = document.createElement('ul');
    headings.forEach(function (h) {
      var li = document.createElement('li');
      li.className = h.tagName === 'H3' ? 'toc-h3' : 'toc-h2';
      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = headingText(h);
      a.dataset.id = h.id;
      li.appendChild(a);
      ul.appendChild(li);
    });
    nav.appendChild(ul);

    /* toggle button for medium viewports */
    var btn = document.createElement('button');
    btn.id = 'toc-toggle';
    btn.setAttribute('aria-label', 'Table of contents');
    btn.textContent = '\u2630';
    document.body.appendChild(btn);
    document.body.appendChild(nav);

    btn.addEventListener('click', function () { nav.classList.toggle('toc-visible'); });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') nav.classList.remove('toc-visible');
    });

    /* scroll spy */
    var active = null;
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          if (active) active.classList.remove('toc-active');
          active = ul.querySelector('a[data-id="' + entry.target.id + '"]');
          if (active) active.classList.add('toc-active');
        }
      });
    }, { rootMargin: '-10% 0px -80% 0px', threshold: 0 });
    headings.forEach(function (h) { observer.observe(h); });
  }

  /* ---- 4. Status board: layer filter + group-by toggle ---- */

  /* shared milestone filter — works on both status board and coverage heatmap */
  function initMilestoneFilter() {
    var milestoneBtns = document.querySelectorAll('.milestone-btn');
    if (!milestoneBtns.length) return;

    milestoneBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        milestoneBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        var scope = btn.dataset.scope || '';

        /* coverage heatmap cells */
        document.querySelectorAll('.cov-item[data-scope]').forEach(function (el) {
          el.classList.toggle('scope-dimmed', !!(scope && el.dataset.scope !== scope));
        });
        /* chapter headers: dim entirely-beta chapters when alpha selected */
        document.querySelectorAll('.cov-chapter[data-chapter-scope]').forEach(function (el) {
          var allBeta = el.dataset.chapterScope === 'beta';
          el.classList.toggle('scope-dimmed', !!(scope === 'alpha' && allBeta));
        });

        /* status board items */
        document.querySelectorAll('.sb-item[data-scope]').forEach(function (el) {
          el.classList.toggle('scope-dimmed', !!(scope && el.dataset.scope !== scope));
        });
      });
    });
  }

  function initStatusBoard() {
    var board = document.querySelector('.status-board');
    if (!board) return;

    /* layer filter */
    var layerBtns = document.querySelectorAll('.layer-btn');
    layerBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        layerBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        var filter = btn.dataset.layer || '';
        board.querySelectorAll('.sb-item').forEach(function (item) {
          var layer = item.dataset.layer || '';
          if (!filter || layer.indexOf(filter) !== -1) {
            item.removeAttribute('data-hidden');
          } else {
            item.setAttribute('data-hidden', '');
          }
        });
      });
    });

    /* group-by toggle */
    var groupBtns = document.querySelectorAll('.group-btn');
    var viewBodies = board.querySelectorAll('.view-rules, .view-layer');
    groupBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        groupBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        var group = btn.dataset.group;
        viewBodies.forEach(function (body) {
          body.style.display = body.classList.contains('view-' + group) ? '' : 'none';
        });
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initTOC();           // before anchor links so headingText() reads clean nodes
    initAnchorLinks();
    initCopyButtons();
    initMilestoneFilter();
    initStatusBoard();
  });
}());
