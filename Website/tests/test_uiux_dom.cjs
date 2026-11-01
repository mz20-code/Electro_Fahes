/* DOM-level interaction tests. This is not a browser or screenshot test.
   Install dev-only jsdom in your chosen environment, then:
   node tests/test_uiux_dom.cjs <fixture-directory>
   Render fixtures with tools/render_uiux_fixtures.py first. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM, VirtualConsole } = require('jsdom');
const fixtures = process.argv[2];
if (!fixtures) throw new Error('Pass the rendered fixture directory.');
const root = path.resolve(__dirname, '..');
const catalogs = JSON.parse(fs.readFileSync(path.join(fixtures, 'catalogs.json'), 'utf8'));
const errors = [];
const tick = () => new Promise(resolve => setTimeout(resolve, 5));

function open(name, route = '/') {
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', error => errors.push(error.message));
  const dom = new JSDOM(fs.readFileSync(path.join(fixtures, name + '.html'), 'utf8'), {
    url: 'https://techverse.example' + route,
    runScripts: 'outside-only',
    pretendToBeVisual: true,
    virtualConsole
  });
  const w = dom.window;
  w.matchMedia = query => ({ matches: query.includes('prefers-reduced-motion'), addEventListener() {}, removeEventListener() {} });
  w.HTMLElement.prototype.scrollIntoView = function () {};
  w.scrollTo = function () {};
  w.fetch = async raw => {
    const url = new URL(raw, w.location.href);
    let data = {};
    if (url.pathname === '/api/conversations') data = { conversations: [] };
    if (url.pathname === '/api/products') data = { products: [{
      id: 'tv-001', name: 'Uploaded part', price_cents: 450,
      image_path: 'uploads/123.webp', image_url: '/media/products/123.webp'
    }] };
    if (url.pathname === '/api/lookup') {
      const model = catalogs.find(c => c.id === url.searchParams.get('model'));
      const entry = model.entries.find(e => e.type === url.searchParams.get('type') && e.code === url.searchParams.get('code'));
      data = {
        code: entry.code, name: entry.name, type_label: entry.type,
        steps: entry.steps.map(step => step.en), source: { ...model.source, page: entry.page }
      };
    }
    return { ok: true, json: async () => data };
  };
  const script = name => w.eval(fs.readFileSync(path.join(root, 'static/js', name), 'utf8'));
  script('main.js');
  return { dom, w, d: w.document, script };
}
const shown = d => [...d.querySelectorAll('.product-card')].filter(card => !card.hidden);
const input = (w, node, value) => { node.value = value; node.dispatchEvent(new w.Event('input', { bubbles: true })); };
const change = (w, node, value) => { node.value = value; node.dispatchEvent(new w.Event('change', { bubbles: true })); };

(async () => {
  for (const language of ['en', 'ar']) {
    const { dom, w, d, script } = open('public-' + language);
    script('shop.js');
    assert.equal(shown(d).length, 24);
    assert.equal(d.querySelectorAll('[data-add-cart]').length, 0);
    d.querySelector('[data-filter-category="sensors"]').click();
    assert(shown(d).length > 0 && shown(d).every(card => card.dataset.category === 'sensors'));
    assert.equal(d.querySelector('[data-filter-category="sensors"]').getAttribute('aria-pressed'), 'true');
    assert(!d.getElementById('active-category').hidden);
    assert(w.location.search.includes('category=sensors'));
    change(w, d.getElementById('shop-sort'), 'low');
    const prices = shown(d).map(card => card.dataset.price).filter(value => value !== '').map(Number);
    assert(prices.every((price, i) => !i || price >= prices[i - 1]));
    input(w, d.getElementById('shop-search'), 'no-matching-product-zxq');
    assert.equal(shown(d).length, 0);
    assert.equal(d.getElementById('shop-empty').hidden, false);
    d.getElementById('reset-filters').click();
    assert.equal(shown(d).length, 24);
    assert.equal(d.getElementById('shop-search').value, '');
    assert.equal(w.location.search, '');
    d.getElementById('show-more').click();
    assert.equal(shown(d).length, 48);
    d.querySelector('[data-catalog-view="list"]').click();
    assert(d.getElementById('products-grid').classList.contains('list-view'));
    assert.equal(w.localStorage.getItem('techverse_catalog_view'), 'list');
    assert.equal(d.querySelector('[data-catalog-view="list"]').getAttribute('aria-pressed'), 'true');
    input(w, d.getElementById('shop-search'), language === 'ar' ? 'اردوينو' : 'ESP32');
    assert(shown(d).length > 0);
    d.getElementById('clear-search').click();
    assert.equal(d.getElementById('shop-search').value, '');
    w.history.pushState({}, '', '?category=boards&sort=high&q=ESP');
    w.dispatchEvent(new w.PopStateEvent('popstate'));
    assert.equal(d.getElementById('shop-sort').value, 'high');
    assert(shown(d).length > 0 && shown(d).every(card => card.dataset.category === 'boards'));
    d.getElementById('nav-toggle').click();
    assert.equal(d.getElementById('nav-toggle').getAttribute('aria-expanded'), 'true');
    d.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    assert.equal(d.getElementById('nav-toggle').getAttribute('aria-expanded'), 'false');
    assert.equal(d.activeElement.id, 'nav-toggle');
    const theme = d.documentElement.dataset.theme;
    d.getElementById('theme-toggle').click();
    assert.notEqual(d.documentElement.dataset.theme, theme);
    assert.equal(w.localStorage.getItem('techverse_theme'), d.documentElement.dataset.theme);
    await tick(); dom.window.close();
  }

  {
    const { dom, w, d, script } = open('shop-en', '/shop');
    script('shop.js');
    d.querySelector('[data-add-cart="tv-001"]').click();
    assert.equal(JSON.parse(w.localStorage.getItem('techverse_cart'))[0].quantity, 1);
    assert.equal(d.getElementById('cart-badge').textContent, '1');
    assert(!d.getElementById('toast').hidden);
    assert(d.querySelector('[data-add-cart="tv-001"]').classList.contains('is-added'));
    dom.window.close();
  }

  {
    const { dom, w, d } = open('register-en', '/register');
    const form = d.querySelector('[data-enhanced-form]');
    let event = new w.Event('submit', { cancelable: true, bubbles: true });
    form.dispatchEvent(event);
    assert(event.defaultPrevented);
    assert(!d.querySelector('.form-error-summary').hidden);
    assert.equal(d.activeElement.className, 'form-error-summary');
    assert(d.getElementById('email').getAttribute('aria-describedby').includes('email-error'));
    input(w, d.getElementById('full_name'), 'Test Person');
    input(w, d.getElementById('email'), 'test@example.invalid');
    input(w, d.getElementById('phone'), '+96170000000');
    input(w, d.getElementById('password'), 'password123');
    input(w, d.getElementById('confirm_password'), 'different123');
    event = new w.Event('submit', { cancelable: true, bubbles: true });
    form.dispatchEvent(event);
    assert(event.defaultPrevented);
    assert.equal(d.getElementById('confirm_password').getAttribute('aria-invalid'), 'true');
    input(w, d.getElementById('confirm_password'), 'password123');
    assert(d.getElementById('confirm_password').validity.valid);
    const toggle = d.querySelector('[data-password-toggle="password"]');
    toggle.click(); assert.equal(d.getElementById('password').type, 'text');
    assert.equal(toggle.getAttribute('aria-pressed'), 'true');
    event = new w.Event('submit', { cancelable: true, bubbles: true });
    form.dispatchEvent(event);
    assert(!event.defaultPrevented);
    assert(form.querySelector('button.btn-primary').disabled);
    assert.equal(form.querySelector('button.btn-primary').getAttribute('aria-busy'), 'true');
    dom.window.close();
  }

  {
    const { dom, w, d, script } = open('advisor-en', '/advisor');
    script('advisor.js');
    await tick();
    d.getElementById('chat-tab').click();
    assert(d.getElementById('lookup-panel').hidden && !d.getElementById('chat-panel').hidden);
    d.querySelector('.tab-row').dispatchEvent(new w.KeyboardEvent('keydown', { key: 'Home', bubbles: true }));
    assert(!d.getElementById('lookup-panel').hidden);
    const visibleCard = [...d.querySelectorAll('[data-select-model]')].find(card => !card.hidden);
    visibleCard.click();
    assert(d.getElementById('model-gallery').hidden);
    const model = catalogs.find(c => c.id === d.getElementById('model-select').value);
    const entry = model.entries.find(e => e.type === 'Fault');
    input(w, d.getElementById('error-code'), entry.code);
    d.getElementById('lookup-button').click();
    await tick();
    assert(!d.getElementById('lookup-result').hidden);
    assert(d.getElementById('lookup-result').textContent.includes(entry.name));
    d.getElementById('choose-another-model').click();
    assert(!d.getElementById('model-gallery').hidden);
    const another = [...d.querySelectorAll('[data-brand]')].find(b => b.dataset.brand !== model.brand);
    another.click();
    assert(!d.getElementById('model-gallery').hidden);
    dom.window.close();
  }

  {
    const { dom, w, d, script } = open('cart-en', '/cart');
    w.localStorage.setItem('techverse_cart', JSON.stringify([{ id: 'tv-001', quantity: 2 }]));
    script('cart.js'); await tick();
    assert.equal(d.querySelector('#cart-items img').getAttribute('src'), '/media/products/123.webp');
    assert.equal(d.getElementById('cart-subtotal').textContent, '$9.00');
    dom.window.close();
  }

  assert.deepEqual(errors, []);
  console.log('PASS: English/Arabic catalog search, categories, sorting, pagination, views, navigation, themes, cart, form validation, and advisor interactions.');
})().catch(error => { console.error(error); process.exitCode = 1; });
