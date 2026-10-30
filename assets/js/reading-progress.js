(() => {
  const article = document.querySelector('.article-content');
  if (!article) return;
  const progress = document.createElement('progress');
  progress.className = 'reading-progress';
  progress.max = 100;
  progress.value = 0;
  progress.setAttribute('aria-label', '文章阅读进度');
  document.body.append(progress);
  let scheduled = false;
  const update = () => {
    const top = article.getBoundingClientRect().top + window.scrollY;
    const distance = Math.max(1, article.offsetHeight - window.innerHeight + 160);
    progress.value = Math.min(100, Math.max(0, (window.scrollY - top + 160) / distance * 100));
    scheduled = false;
  };
  const schedule = () => {
    if (!scheduled) { scheduled = true; requestAnimationFrame(update); }
  };
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  window.addEventListener('load', schedule);
  update();
})();
