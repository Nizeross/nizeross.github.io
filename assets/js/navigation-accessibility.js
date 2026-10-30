(() => {
  const toggle = document.getElementById('mobile-menu-toggle');
  const dialog = document.getElementById('mobile-navigation');
  const labels = [...document.querySelectorAll('label[for="mobile-menu-toggle"]')];
  if (!toggle || !dialog) return;
  const opener = labels.find(label => !dialog.contains(label));
  const close = () => {
    toggle.checked = false;
    opener?.setAttribute('aria-expanded', 'false');
    opener?.focus();
  };
  opener?.setAttribute('aria-expanded', 'false');
  labels.forEach(label => label.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      label.click();
    }
  }));
  toggle.addEventListener('change', () => {
    opener?.setAttribute('aria-expanded', String(toggle.checked));
    requestAnimationFrame(() => {
      if (toggle.checked) dialog.querySelector('[role="button"]')?.focus();
      else opener?.focus();
    });
  });
  document.addEventListener('keydown', event => {
    if (!toggle.checked) return;
    if (event.key === 'Escape') { event.preventDefault(); close(); }
    if (event.key !== 'Tab') return;
    const focusable = [...dialog.querySelectorAll('a[href],button,[tabindex="0"]')].filter(el => el.getClientRects().length);
    if (event.shiftKey && document.activeElement === focusable[0]) {
      event.preventDefault(); focusable.at(-1)?.focus();
    } else if (!event.shiftKey && document.activeElement === focusable.at(-1)) {
      event.preventDefault(); focusable[0]?.focus();
    }
  });
})();
