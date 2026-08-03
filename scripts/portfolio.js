(() => {
  'use strict';

  const filters = [...document.querySelectorAll('[data-project-filter]')];
  const cards = [...document.querySelectorAll('[data-project-card]')];
  const count = document.querySelector('[data-project-count]');
  const empty = document.querySelector('[data-empty-filter]');

  if (!filters.length || !cards.length) return;

  const validFilters = new Set(filters.map((button) => button.dataset.projectFilter));

  const applyFilter = (filter, { updateHash = true } = {}) => {
    const next = validFilters.has(filter) ? filter : 'all';
    let visible = 0;

    for (const button of filters) {
      button.setAttribute('aria-pressed', String(button.dataset.projectFilter === next));
    }

    for (const card of cards) {
      const categories = new Set((card.dataset.categories || '').split(/\s+/).filter(Boolean));
      const show = next === 'all' || categories.has(next);
      card.hidden = !show;
      if (show) visible += 1;
    }

    if (count) count.textContent = `${visible} PROJECT${visible === 1 ? '' : 'S'}`;
    if (empty) empty.hidden = visible !== 0;

    if (updateHash && /^(https?:)$/.test(window.location.protocol)) {
      const url = new URL(window.location.href);
      if (next === 'all') url.searchParams.delete('category');
      else url.searchParams.set('category', next);
      history.replaceState(null, '', `${url.pathname}${url.search}${url.hash}`);
    }
  };

  for (const button of filters) {
    button.addEventListener('click', () => applyFilter(button.dataset.projectFilter));
  }

  const initial = new URL(window.location.href).searchParams.get('category') || 'all';
  applyFilter(initial, { updateHash: false });
})();
