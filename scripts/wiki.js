(() => {
  'use strict';

  const input = document.querySelector('[data-wiki-search]');
  const rows = [...document.querySelectorAll('[data-concept-row]')];
  const domainButtons = [...document.querySelectorAll('[data-domain-filter]')];
  const clearButton = document.querySelector('[data-domain-clear]');
  const count = document.querySelector('[data-wiki-result-count]');
  const empty = document.querySelector('[data-wiki-empty]');

  if (!input || !rows.length) return;

  let activeDomain = '';
  const normalize = (value) => String(value || '').trim().toLocaleLowerCase('ko-KR');

  const render = () => {
    const query = normalize(input.value);
    let visible = 0;

    for (const row of rows) {
      const matchesQuery = !query || normalize(row.dataset.search).includes(query);
      const matchesDomain = !activeDomain || row.dataset.domain === activeDomain;
      const show = matchesQuery && matchesDomain;
      row.hidden = !show;
      if (show) visible += 1;
    }

    for (const button of domainButtons) {
      button.setAttribute('aria-pressed', String(button.dataset.domainFilter === activeDomain));
    }

    if (clearButton) clearButton.hidden = !activeDomain;
    if (count) count.textContent = String(visible);
    if (empty) empty.hidden = visible !== 0;
  };

  input.addEventListener('input', render);

  for (const button of domainButtons) {
    button.addEventListener('click', () => {
      const selected = button.dataset.domainFilter || '';
      activeDomain = activeDomain === selected ? '' : selected;
      render();
      if (activeDomain) document.querySelector('.concept-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  clearButton?.addEventListener('click', () => {
    activeDomain = '';
    render();
  });

  render();
})();
