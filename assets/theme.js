// Loaded synchronously in <head> so the theme is applied before first paint
// (no flash of the light theme for dark-mode visitors).
(function () {
  const root = document.documentElement;
  const media = window.matchMedia('(prefers-color-scheme: dark)');

  function saved() {
    try { return localStorage.getItem('theme'); } catch (e) { return null; }
  }

  function apply(theme) {
    root.setAttribute('data-theme', theme);
    const btn = document.querySelector('.theme-toggle');
    if (btn) btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }

  apply(saved() || (media.matches ? 'dark' : 'light'));

  // Follow the OS setting until the visitor picks a theme themselves.
  media.addEventListener('change', (e) => {
    if (!saved()) apply(e.matches ? 'dark' : 'light');
  });

  document.addEventListener('DOMContentLoaded', () => {
    const btn = document.querySelector('.theme-toggle');
    if (!btn) return;
    apply(root.getAttribute('data-theme'));
    btn.addEventListener('click', () => {
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('theme', next); } catch (e) {}
      apply(next);
    });
  });
})();
