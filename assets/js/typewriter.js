(() => {
  const element = document.getElementById('typewriter');
  if (!element || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const text = element.dataset.text || element.textContent;
  element.textContent = '';
  let index = 0;
  const type = () => {
    element.textContent = text.slice(0, ++index);
    if (index < text.length) setTimeout(type, 350);
  };
  setTimeout(type, 350);
})();
