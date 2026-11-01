/* Catalog controls: one implementation for the public preview and signed-in shop. */
(() => {
  'use strict';
  const { t, toast } = window.TechVerse;
  const grid = document.getElementById('products-grid');
  if (!grid) return;
  const cards = [...grid.children];
  const search = document.getElementById('shop-search');
  const sort = document.getElementById('shop-sort');
  const more = document.getElementById('show-more');
  const empty = document.getElementById('shop-empty');
  const status = document.getElementById('catalog-status');
  const clear = document.getElementById('clear-search');
  const chip = document.getElementById('active-category');
  const title = document.getElementById('collection-title');
  const filters = [...document.querySelectorAll('[data-filter-category]')];
  const views = [...document.querySelectorAll('[data-catalog-view]')];
  const normalize = text => text.toLowerCase().normalize('NFKD')
    .replace(/[\u064B-\u065F\u0670]/g, '').replace(/[أإآ]/g, 'ا').trim();
  const searchIndex = new Map(cards.map(card => [card, normalize(card.dataset.search)]));
  let category = 'all', visible = 24, announceTimer;
  const labels = new Map(filters.map(button => [button.dataset.filterCategory, button.querySelector('span').textContent]));
  const validSorts = new Set(['retail', 'name', 'low', 'high']);

  function readLocation() {
    const params = new URLSearchParams(location.search);
    category = labels.has(params.get('category')) ? params.get('category') : 'all';
    search.value = params.get('q') || '';
    sort.value = validSorts.has(params.get('sort')) ? params.get('sort') : 'retail';
  }
  function setView(value, save = true) {
    const view = value === 'list' ? 'list' : 'grid';
    grid.classList.toggle('list-view', view === 'list');
    views.forEach(button => {
      const active = button.dataset.catalogView === view;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    if (save) { try { localStorage.setItem('techverse_catalog_view', view); } catch (_) {} }
  }
  function announce(value) {
    clearTimeout(announceTimer);
    status.textContent = '';
    announceTimer = setTimeout(() => { status.textContent = value; }, 120);
  }
  function render({ announceChange = true, updateUrl = true } = {}) {
    const terms = normalize(search.value).split(/\s+/).filter(Boolean);
    const selected = cards.filter(card =>
      (category === 'all' || card.dataset.category === category) &&
      terms.every(term => searchIndex.get(card).includes(term)));
    selected.sort((a, b) => {
      if (sort.value === 'name') return a.dataset.name.localeCompare(b.dataset.name, document.documentElement.lang);
      const pa = a.dataset.price === '' ? null : Number(a.dataset.price);
      const pb = b.dataset.price === '' ? null : Number(b.dataset.price);
      if (pa === null || pb === null) return pa === pb ? a.dataset.id.localeCompare(b.dataset.id) : pa === null ? 1 : -1;
      return sort.value === 'low' ? pa - pb : sort.value === 'high' ? pb - pa : a.dataset.id.localeCompare(b.dataset.id);
    });
    cards.forEach(card => { card.hidden = true; });
    const fragment = document.createDocumentFragment();
    selected.forEach((card, i) => { card.hidden = i >= visible; fragment.append(card); });
    grid.append(fragment);
    filters.forEach(button => {
      const active = button.dataset.filterCategory === category;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    title.textContent = labels.get(category);
    clear.hidden = !search.value;
    chip.hidden = category === 'all';
    chip.querySelector('span').textContent = labels.get(category);
    chip.setAttribute('aria-label', t('catalog_filter_remove') + ': ' + labels.get(category));
    empty.hidden = selected.length > 0;
    more.hidden = selected.length <= visible;
    if (updateUrl) {
      const url = new URL(location.href);
      if (category === 'all') url.searchParams.delete('category'); else url.searchParams.set('category', category);
      if (search.value.trim()) url.searchParams.set('q', search.value.trim()); else url.searchParams.delete('q');
      if (sort.value === 'retail') url.searchParams.delete('sort'); else url.searchParams.set('sort', sort.value);
      history.replaceState(null, '', url);
    }
    if (announceChange) announce(t(selected.length ? 'catalog_updated' : 'no_products'));
    return selected;
  }
  search.addEventListener('input', () => { visible = 24; render(); });
  sort.addEventListener('change', () => { visible = 24; render(); });
  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.filterCategory; visible = 24; render();
  }));
  clear.addEventListener('click', () => { search.value = ''; visible = 24; render(); search.focus(); });
  chip.addEventListener('click', () => { category = 'all'; visible = 24; render(); filters[0].focus(); });
  views.forEach(button => button.addEventListener('click', () => setView(button.dataset.catalogView)));
  more.addEventListener('click', () => {
    const previous = visible; visible += 24;
    const selected = render();
    const first = selected[previous]?.querySelector('.product-name');
    if (first) {
      first.focus({ preventScroll: true });
      first.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    }
  });
  document.getElementById('reset-filters').addEventListener('click', () => {
    category = 'all'; search.value = ''; sort.value = 'retail'; visible = 24; render(); search.focus();
  });
  window.addEventListener('popstate', () => { readLocation(); visible = 24; render({ updateUrl: false }); });
  readLocation();
  try { setView(localStorage.getItem('techverse_catalog_view'), false); } catch (_) { setView('grid', false); }
  render({ announceChange: false });
})();
