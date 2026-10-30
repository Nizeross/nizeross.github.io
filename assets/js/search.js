/* Uses Blowfish's local Fuse index; creates text nodes instead of injecting HTML. */
(() => {
  const wrapper = document.getElementById('search-wrapper');
  const input = document.getElementById('search-query');
  const output = document.getElementById('search-results');
  const modal = document.getElementById('search-modal');
  if (!wrapper || !input || !output || !modal) return;
  let indexPromise;
  let previousFocus;
  let visible = false;
  let queryRevision = 0;

  const index = () => indexPromise ||= fetch(`${wrapper.dataset.url.replace(/\/?$/, '/')}index.json`)
    .then(response => { if (!response.ok) throw new Error('Search index unavailable'); return response.json(); })
    .then(data => new Fuse(data, { ignoreLocation: true, threshold: .2, keys: ['title', 'summary', 'content', 'section'] }));

  const close = () => {
    visible = false;
    queryRevision++;
    wrapper.style.visibility = 'hidden';
    document.body.style.overflow = '';
    input.value = '';
    output.replaceChildren();
    previousFocus?.focus();
  };
  const open = () => {
    if (visible) return;
    visible = true;
    previousFocus = document.activeElement;
    wrapper.style.visibility = 'visible';
    document.body.style.overflow = 'hidden';
    input.focus();
    index().catch(() => { indexPromise = null; });
  };
  ['search-button', 'search-button-mobile'].forEach(id => document.getElementById(id)?.addEventListener('click', open));
  document.getElementById('close-search-button').addEventListener('click', close);
  wrapper.addEventListener('click', event => { if (event.target === wrapper) close(); });
  input.closest('form').addEventListener('submit', event => {
    event.preventDefault();
    output.querySelector('a')?.focus();
  });
  input.addEventListener('input', async () => {
    const revision = ++queryRevision;
    const term = input.value.trim();
    output.replaceChildren();
    if (!term) return;
    try {
      const fuse = await index();
      if (revision !== queryRevision || !visible) return;
      const results = fuse.search(term).slice(0, 12);
      if (!results.length) {
        const item = document.createElement('li');
        item.textContent = '没有找到匹配的文章。';
        output.append(item);
      }
      for (const { item } of results) {
        const li = document.createElement('li');
        const link = document.createElement('a');
        const title = document.createElement('strong');
        const summary = document.createElement('span');
        const url = new URL(item.permalink, location.origin);
        if (!['http:', 'https:'].includes(url.protocol)) continue;
        link.href = url.pathname + url.search + url.hash;
        link.className = 'search-result';
        title.textContent = item.title;
        const plain = new DOMParser().parseFromString(item.summary || '', 'text/html').body.textContent;
        summary.textContent = plain.slice(0, 130);
        link.append(title, summary);
        li.append(link);
        output.append(li);
      }
    } catch {
      output.textContent = '搜索暂时无法加载，请稍后重试。';
      indexPromise = null;
    }
  });
  document.addEventListener('keydown', event => {
    if (event.key === '/' && !visible && !/input|textarea|select/i.test(document.activeElement.tagName) && !document.activeElement.isContentEditable) {
      event.preventDefault(); open();
    }
    if (!visible) return;
    if (event.key === 'Escape') { event.preventDefault(); close(); }
    const elements = [...modal.querySelectorAll('input, button, a[href]')];
    const current = elements.indexOf(document.activeElement);
    if (event.key === 'Tab' && event.shiftKey && current === 0) { event.preventDefault(); elements.at(-1).focus(); }
    else if (event.key === 'Tab' && !event.shiftKey && current === elements.length - 1) { event.preventDefault(); elements[0].focus(); }
    if (event.key === 'ArrowDown') { event.preventDefault(); elements[Math.min(current + 1, elements.length - 1)]?.focus(); }
    if (event.key === 'ArrowUp') { event.preventDefault(); elements[Math.max(0, current - 1)]?.focus(); }
  });
})();
