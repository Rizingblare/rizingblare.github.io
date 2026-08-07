(() => {
  'use strict';
  const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;' }[char]));
  const normalize = (value) => String(value ?? '').normalize('NFKC').toLocaleLowerCase('ko-KR').replace(/\s+/g, ' ').trim();
  const domainLabels = {
    'algorithms-data-structures':'자료구조·알고리즘', 'broadcast-media':'방송 미디어·영상',
    'computer-architecture':'컴퓨터구조·디지털논리', databases:'데이터베이스',
    'electronics-circuits':'전자공학·회로', 'general-knowledge':'일반상식·시사',
    'information-security':'정보보안', 'mobile-communications':'이동통신·5G', networking:'네트워크',
    'operating-systems':'운영체제', programming:'코딩', 'radio-antenna':'전파·안테나·무선설비',
    'signal-processing':'신호처리', 'software-engineering':'소프트웨어 공학',
    'telecom-regulations':'정보통신 법규·설비기준', portfolio:'포트폴리오', blog:'블로그'
  };
  const learnerSummary = (item) => String(item.summary || item.description || '').replace(/에 대한 독립 문서 후보입니다\.$/, '의 핵심 개념을 살펴봅니다.');
  const typeLabel = (item) => ({ concept:'개념', project:'프로젝트', post:'블로그 글' }[item.type] || '학습 자료');
  const statusLabel = (item) => item.type === 'concept'
    ? (item.status === 'published' ? '학습 문서' : '작성 중')
    : '공개됨';
  const isPublicItem = (item) => item?.type === 'concept'
    ? (item.status === 'published' && Boolean(item.url)) || item.status === 'pending'
    : item?.status === 'published' && Boolean(item.url);
  const fetchJson = async (url) => {
    const response = await fetch(url, { credentials: 'same-origin' });
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    return response.json();
  };
  const cardHtml = (item) => {
    const title = escapeHtml(item.title);
    const summary = escapeHtml(learnerSummary(item));
    const status = item.status || '';
    const href = status === 'published' ? item.url : '';
    const body = `<div><h3>${title}</h3><p>${summary}</p></div><span class="catalog-status ${status}">${escapeHtml(statusLabel(item))}</span>`;
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
    let items = [];
    let filtered = [];
    let page = 1;
    const apply = () => {
      const query = normalize(input?.value);
      const requestedState = status?.value || 'all';
      const state = ['published', 'pending'].includes(requestedState) ? requestedState : 'all';
      filtered = items.filter((item) => (!query || normalize(`${item.title} ${(item.aliases || []).join(' ')} ${item.summary} ${(item.topics || []).join(' ')}`).includes(query)) && (state === 'all' || item.status === state));
      const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
      page = Math.min(page, pages);
      const slice = filtered.slice((page - 1) * pageSize, page * pageSize);
      list.innerHTML = slice.length ? slice.map((item) => cardHtml(item)).join('') : '<p class="search-empty">조건에 맞는 공개 자료가 없습니다.</p>';
      if (count) count.textContent = String(filtered.length);
      if (pageOutput) pageOutput.textContent = `${page} / ${pages}`;
      if (prev) prev.disabled = page <= 1;
      if (next) next.disabled = page >= pages;
    };
    try {
      items = (await fetchJson(root.dataset.shardUrl)).filter(isPublicItem);
      filtered = items;
      const initialQuery = new URL(window.location.href).searchParams.get('q');
      if (initialQuery && input) input.value = initialQuery;
      apply();
    } catch (error) {
      list.innerHTML = `<p class="search-empty">개념 목록을 불러오지 못했습니다: ${escapeHtml(error.message)}</p>`;
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
    const status = globalRoot.querySelector('[data-search-status]');
    const min = Number(globalRoot.dataset.minimumLength || 2);
    let loaded = null;
    const loadAll = async () => {
      if (loaded) return loaded;
      const manifest = await fetchJson(globalRoot.dataset.manifestUrl);
      const shards = await Promise.all([fetchJson(manifest.content), ...manifest.wiki.map((entry) => fetchJson(entry.url))]);
      loaded = shards.flat().filter(isPublicItem);
      return loaded;
    };
    const render = async () => {
      const query = normalize(input.value);
      if (query.length < min) {
        results.innerHTML = `<p class="search-empty">${min}글자 이상 입력하면 분할 인덱스를 불러옵니다.</p>`;
        results.setAttribute('aria-busy', 'false');
        if (count) count.textContent = '0';
        if (status) status.textContent = `검색하려면 ${min}글자 이상 입력하세요.`;
        return;
      }
      results.innerHTML = '<p class="search-empty">검색 인덱스를 불러오는 중입니다.</p>';
      results.setAttribute('aria-busy', 'true');
      try {
        const items = await loadAll();
        const type = typeFilter.value;
        const allMatches = items.filter((item) => (type === 'all' || item.type === type) && normalize(`${item.title} ${item.summary || item.description || ''} ${(item.aliases || []).join(' ')} ${(item.keywords || item.tags || []).join(' ')}`).includes(query));
        const matches = allMatches.slice(0, 100);
        if (count) count.textContent = String(allMatches.length);
        if (status) status.textContent = `${allMatches.length}개 검색 결과가 있습니다.`;
        const capNotice = allMatches.length > matches.length ? `<p class="search-empty">전체 ${allMatches.length}건 중 상위 ${matches.length}건만 표시합니다. 검색어를 더 구체적으로 입력해 보세요.</p>` : '';
        results.innerHTML = matches.length ? matches.map((item) => {
          const domain = domainLabels[item.domain || item.primaryDomain] || '';
          const body = `<h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(learnerSummary(item))}</p><div class="search-meta"><span>${escapeHtml(typeLabel(item))}</span>${domain ? `<span>${escapeHtml(domain)}</span>` : ''}<span>${escapeHtml(statusLabel(item))}</span></div>`;
          return item.status === 'published' ? `<a class="search-result surface-panel" href="${escapeHtml(item.url)}">${body}</a>` : `<article class="search-result surface-panel">${body}</article>`;
        }).join('') + capNotice : '<p class="search-empty">검색 결과가 없습니다.</p>';
      } catch (error) {
        results.innerHTML = `<p class="search-empty">검색 인덱스를 불러오지 못했습니다: ${escapeHtml(error.message)}</p>`;
        if (count) count.textContent = '0';
        if (status) status.textContent = '검색 결과를 불러오지 못했습니다.';
      } finally {
        results.setAttribute('aria-busy', 'false');
      }
    };
    let timer;
    input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(render, 120); });
    typeFilter.addEventListener('change', render);
    const initialQuery = new URLSearchParams(location.search).get('q');
    if (initialQuery !== null) {
      input.value = initialQuery;
      render();
    }
  }
})();
