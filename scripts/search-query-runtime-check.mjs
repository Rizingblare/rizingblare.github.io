import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const source = fs.readFileSync(path.join(root, 'scripts/v2.js'), 'utf8');
const siteSource = fs.readFileSync(path.join(root, 'scripts/site.js'), 'utf8');

const element = (initial = {}) => ({
  value: '',
  textContent: '',
  innerHTML: '',
  dataset: {},
  attributes: new Map(),
  listeners: new Map(),
  setAttribute(name, value) { this.attributes.set(name, String(value)); },
  getAttribute(name) { return this.attributes.get(name); },
  addEventListener(name, listener) { this.listeners.set(name, listener); },
  ...initial
});

const waitFor = async (predicate) => {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    if (predicate()) return;
    await new Promise((resolve) => setTimeout(resolve, 0));
  }
  throw new Error('search render did not settle');
};

const runSearch = async (search, fixtures = {}) => {
  const input = element();
  const typeFilter = element({ value: 'all' });
  const results = element();
  const count = element({ textContent: '0' });
  const status = element();
  const elements = new Map([
    ['[data-search-query]', input],
    ['[data-search-type]', typeFilter],
    ['[data-search-results]', results],
    ['[data-search-count]', count],
    ['[data-search-status]', status]
  ]);
  const globalRoot = {
    dataset: { manifestUrl: '/search/manifest.json', minimumLength: '2' },
    querySelector(selector) { return elements.get(selector); }
  };
  const location = { search };
  let fetchCount = 0;
  const context = {
    URLSearchParams,
    clearTimeout,
    console,
    document: {
      querySelector(selector) { return selector === '[data-global-search]' ? globalRoot : null; },
      querySelectorAll() { return []; }
    },
    fetch: async (url) => {
      fetchCount += 1;
      const relative = new URL(url, 'https://example.test').pathname.replace(/^\//, '');
      const data = relative in fixtures
        ? fixtures[relative]
        : JSON.parse(fs.readFileSync(path.join(root, relative), 'utf8'));
      return { ok: true, json: async () => data };
    },
    location,
    setTimeout,
    window: { location }
  };
  vm.runInNewContext(source, context, { filename: 'scripts/v2.js' });
  await waitFor(() => results.getAttribute('aria-busy') === 'false' && status.textContent !== '');
  return { input, results, count, status, fetchCount };
};

const assertResult = async (search, query, title, fixtures = {}) => {
  const state = await runSearch(search, fixtures);
  assert.equal(state.input.value, query);
  assert.equal(state.count.textContent, '1');
  assert.equal(state.status.textContent, '1개 검색 결과가 있습니다.');
  assert.match(state.results.innerHTML, new RegExp(`<h3>${title}</h3>`));
  assert.equal(state.results.getAttribute('aria-busy'), 'false');
};

const assertNoResult = async (search, query, fixtures = {}) => {
  const state = await runSearch(search, fixtures);
  assert.equal(state.input.value, query);
  assert.equal(state.count.textContent, '0');
  assert.equal(state.status.textContent, '0개 검색 결과가 있습니다.');
  assert.match(state.results.innerHTML, /검색 결과가 없습니다/);
  assert.equal(state.results.getAttribute('aria-busy'), 'false');
};

await assertNoResult('?q=MVCC', 'MVCC');
await assertNoResult('?q=%EC%93%B0%EA%B8%B0%20%EC%8A%A4%ED%81%90', '쓰기 스큐');
await assertResult('?q=%ED%91%B8%EB%A6%AC%EC%97%90%20%EB%B3%80%ED%99%98', '푸리에 변환', '푸리에 변환');

const contractFixtures = {
  'search/contract-manifest.json': {
    content: '/search/empty-content.json',
    wiki: [{ id: 'contract', count: 2, url: '/search/wiki/contract.json' }]
  },
  'search/empty-content.json': [],
  'search/wiki/contract.json': [
    {
      type: 'concept', id: 'future-pending', title: '미래 작성 계약', aliases: [],
      status: 'pending', summary: '실제 작성이 시작된 문서입니다.', domain: 'contract'
    },
    {
      type: 'concept', id: 'poisoned-proposed', title: '내부 제안 누출', aliases: [],
      status: 'proposed', summary: '공개되면 안 됩니다.', domain: 'contract', url: '/should-not-render/'
    }
  ]
};
const pending = await runSearch('?q=%EB%AF%B8%EB%9E%98%20%EC%9E%91%EC%84%B1%20%EA%B3%84%EC%95%BD', {
  ...contractFixtures,
  'search/manifest.json': contractFixtures['search/contract-manifest.json']
});
assert.equal(pending.count.textContent, '1');
assert.match(pending.results.innerHTML, /<article class="search-result surface-panel">/);
assert.match(pending.results.innerHTML, /작성 중/);
assert.doesNotMatch(pending.results.innerHTML, /<a class="search-result/);

await assertNoResult('?q=%EB%82%B4%EB%B6%80%20%EC%A0%9C%EC%95%88%20%EB%88%84%EC%B6%9C', '내부 제안 누출', {
  ...contractFixtures,
  'search/manifest.json': contractFixtures['search/contract-manifest.json']
});

const short = await runSearch('?q=M');
assert.equal(short.input.value, 'M');
assert.equal(short.count.textContent, '0');
assert.equal(short.status.textContent, '검색하려면 2글자 이상 입력하세요.');
assert.match(short.results.innerHTML, /2글자 이상/);
assert.equal(short.results.getAttribute('aria-busy'), 'false');
assert.equal(short.fetchCount, 0);

assert.doesNotMatch(siteSource, /클릭하면 독립 문서로 이동합니다\./);
assert.doesNotMatch(siteSource, /독립 문서 작성 전: 도메인 카탈로그에서 해당 후보를 찾습니다\./);
assert.match(siteSource, /클릭하면 학습 문서로 이동합니다\./);
assert.doesNotMatch(siteSource, /관련 학습 문서는 준비 중입니다\./);

console.log('initial search query runtime: ok (proposed hidden, published found, short query)');
console.log('future pending contract: ok (visible as 작성 중, not linked)');
console.log('concept tooltip learner copy: ok (published links only)');
