(() => {
  'use strict';
  const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;' }[char]));
  const normalize = (value) => String(value ?? '').normalize('NFKC').toLocaleLowerCase('ko-KR').replace(/\s+/g, ' ').trim();
  const fetchJson = async (url) => {
    const response = await fetch(url, { credentials: 'same-origin' });
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    return response.json();
  };
  const cardHtml = (item, basePath = '') => {
    const title = escapeHtml(item.title);
    const summary = escapeHtml(item.summary || item.description || '');
    const status = escapeHtml(item.status || item.type || '');
    const href = item.url || (item.route ? `${basePath}/wiki/${item.route}/`.replace(/\/+/g, '/') : '');
    const body = `<div><h3>${title}</h3><p>${summary}</p><div class="catalog-meta"><span>${escapeHtml(item.profile || item.type || '')}</span><span>${escapeHtml(item.kind || item.domain || '')}</span></div></div><span class="catalog-status ${status === 'published' ? 'published' : ''}">${status}</span>`;
    return href ? `<a class="catalog-item" href="${escapeHtml(href)}">${body}</a>` : `<article class="catalog-item">${body}</article>`;
  };

  document.querySelectorAll('[data-domain-catalog]').forEach(async (root) => {
    const list = root.querySelector('[data-catalog-list]');
    const input = root.querySelector('[data-catalog-query]');
    const status = root.querySelector('[data-catalog-status]');
    const count = root.querySelector('[data-catalog-count]');
    const prev = root.querySelector('[data-page-prev]');
    const next = root.querySelector('[data-page-next]');
    const pageOutput = root.querySelector('[data-page-output]');
    const pageSize = Number(root.dataset.pageSize || 24);
    const basePath = root.dataset.basePath || '';
    let items = [];
    let filtered = [];
    let page = 1;
    const apply = () => {
      const query = normalize(input?.value);
      const state = status?.value || 'all';
      filtered = items.filter((item) => (!query || normalize(`${item.title} ${(item.aliases || []).join(' ')} ${item.summary} ${(item.topics || []).join(' ')}`).includes(query)) && (state === 'all' || item.status === state));
      const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
      page = Math.min(page, pages);
      const slice = filtered.slice((page - 1) * pageSize, page * pageSize);
      list.innerHTML = slice.length ? slice.map((item) => cardHtml(item, basePath)).join('') : '<p class="search-empty">조건에 맞는 개념이 없습니다.</p>';
      if (count) count.textContent = String(filtered.length);
      if (pageOutput) pageOutput.textContent = `${page} / ${pages}`;
      if (prev) prev.disabled = page <= 1;
      if (next) next.disabled = page >= pages;
    };
    try {
      items = await fetchJson(root.dataset.shardUrl);
      filtered = items;
      const initialQuery = new URL(window.location.href).searchParams.get('q');
      if (initialQuery && input) input.value = initialQuery;
      apply();
    } catch (error) {
      list.innerHTML = `<p class="search-empty">카탈로그를 불러오지 못했습니다: ${escapeHtml(error.message)}</p>`;
    }
    input?.addEventListener('input', () => { page = 1; apply(); });
    status?.addEventListener('change', () => { page = 1; apply(); });
    prev?.addEventListener('click', () => { page = Math.max(1, page - 1); apply(); root.scrollIntoView({ behavior:'smooth', block:'start' }); });
    next?.addEventListener('click', () => { page += 1; apply(); root.scrollIntoView({ behavior:'smooth', block:'start' }); });
  });

  const globalRoot = document.querySelector('[data-global-search]');
  if (globalRoot) {
    const input = globalRoot.querySelector('[data-search-query]');
    const typeFilter = globalRoot.querySelector('[data-search-type]');
    const results = globalRoot.querySelector('[data-search-results]');
    const count = globalRoot.querySelector('[data-search-count]');
    const min = Number(globalRoot.dataset.minimumLength || 2);
    let loaded = null;
    const loadAll = async () => {
      if (loaded) return loaded;
      const manifest = await fetchJson(globalRoot.dataset.manifestUrl);
      const shards = await Promise.all([fetchJson(manifest.content), ...manifest.wiki.map((entry) => fetchJson(entry.url))]);
      loaded = shards.flat();
      return loaded;
    };
    const render = async () => {
      const query = normalize(input.value);
      if (query.length < min) { results.innerHTML = `<p class="search-empty">${min}글자 이상 입력하면 분할 인덱스를 불러옵니다.</p>`; if(count)count.textContent='0'; return; }
      results.innerHTML = '<p class="search-empty">검색 인덱스를 불러오는 중입니다.</p>';
      try {
        const items = await loadAll();
        const type = typeFilter.value;
        const allMatches = items.filter((item) => (type === 'all' || item.type === type) && normalize(`${item.title} ${item.summary || item.description || ''} ${(item.aliases || []).join(' ')} ${(item.keywords || item.tags || []).join(' ')}`).includes(query));
        const matches = allMatches.slice(0, 100);
        if (count) count.textContent = String(allMatches.length);
        const capNotice = allMatches.length > matches.length ? `<p class="search-empty">전체 ${allMatches.length}건 중 상위 ${matches.length}건만 표시합니다. 검색어를 더 구체적으로 입력해 보세요.</p>` : '';
        results.innerHTML = matches.length ? matches.map((item) => {
          const body = `<h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.summary || item.description || '')}</p><div class="search-meta"><span>${escapeHtml(item.type)}</span><span>${escapeHtml(item.domain || item.primaryDomain || '')}</span><span>${escapeHtml(item.status || '')}</span></div>`;
          return item.url ? `<a class="search-result surface-panel" href="${escapeHtml(item.url)}">${body}</a>` : `<article class="search-result surface-panel">${body}</article>`;
        }).join('') + capNotice : '<p class="search-empty">검색 결과가 없습니다.</p>';
      } catch (error) { results.innerHTML = `<p class="search-empty">검색 인덱스를 불러오지 못했습니다: ${escapeHtml(error.message)}</p>`; }
    };
    let timer;
    input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(render, 120); });
    typeFilter.addEventListener('change', render);
  }
})();
