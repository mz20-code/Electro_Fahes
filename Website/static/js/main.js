/* Shared interface. The cart stores IDs and quantities; the server sets prices. */
(() => {
  'use strict';
  window.addEventListener('pageshow', event => { if (event.persisted) location.reload(); });
  const ui = JSON.parse(document.getElementById('ui-data').textContent);
  const t = key => ui.strings[key] || key;
  const csrf = document.querySelector('meta[name="csrf-token"]').content;
  const node = (tag, cls, value) => { const n = document.createElement(tag); if (cls) n.className = cls; if (value !== undefined) n.textContent = value; return n; };
  async function api(path, options = {}) {
    const headers = { ...(options.headers || {}), 'X-CSRF-Token': csrf };
    if (options.body && typeof options.body !== 'string') { headers['Content-Type'] = 'application/json'; options = { ...options, body: JSON.stringify(options.body) }; }
    let response;
    try { response = await fetch(path, { ...options, headers, credentials: 'same-origin' }); } catch (_) { throw new Error(t('server_error')); }
    let data; try { data = await response.json(); } catch (_) { throw new Error(t('server_error')); }
    if (!response.ok) throw new Error(data.error || t('server_error'));
    return data;
  }
  let toastTimer;
  function toast(value) { const el = document.getElementById('toast'); el.textContent = value; el.hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(() => { el.hidden = true; }, 4000); }
  function readCart() {
    try {
      const value = JSON.parse(localStorage.getItem('techverse_cart') || '[]');
      if (!Array.isArray(value)) return [];
      return value.filter(i => i && /^tv-\d{3,10}$/.test(i.id) && Number.isInteger(i.quantity) && i.quantity >= 1 && i.quantity <= 99).slice(0, 150);
    } catch (_) { return []; }
  }
  function writeCart(value) { try { localStorage.setItem('techverse_cart', JSON.stringify(value)); } catch (_) { toast(t('storage_unavailable')); } updateBadge(value); }
  function updateBadge(value = readCart()) { const count = value.reduce((a, i) => a + i.quantity, 0); const badge = document.getElementById('cart-badge'); if (badge) { badge.textContent = count; badge.hidden = !count; } }
  function money(cents) { return new Intl.NumberFormat(ui.language === 'ar' ? 'ar-LB' : 'en-US', { style: 'currency', currency: 'USD' }).format(cents / 100); }
  function icon(name) { const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); svg.setAttribute('class', 'icon'); svg.setAttribute('viewBox', '0 0 24 24'); svg.setAttribute('fill', 'none'); svg.setAttribute('stroke', 'currentColor'); svg.setAttribute('stroke-width', '1.7'); svg.setAttribute('stroke-linecap', 'round'); svg.setAttribute('aria-hidden', 'true'); const path = document.createElementNS(svg.namespaceURI, 'path'); path.setAttribute('d', { trash: 'M3 6h18M9 6V3h6v3M6 6l1 15h10l1-15m-8 4v6m4-6v6', arrow: 'M5 12h14m-5-5 5 5-5 5', book: 'M3 4h6a4 4 0 0 1 3 2 4 4 0 0 1 3-2h6v15h-6a4 4 0 0 0-3 2 4 4 0 0 0-3-2H3V4ZM12 6v15' }[name] || 'M5 12h14'); svg.append(path); return svg; }
  function sourceUrl(source) { const url = source.local_file || source.url; return url + (source.page ? '#page=' + source.page : ''); }
  window.TechVerse = { ui, t, node, api, toast, readCart, writeCart, money, icon, sourceUrl };
  updateBadge();
  window.addEventListener('storage', e => { if (e.key === 'techverse_cart') updateBadge(); });
  document.addEventListener('click', e => {
    const add = e.target.closest('[data-add-cart]');
    if (add) { const cart = readCart(); const item = cart.find(i => i.id === add.dataset.addCart); if (item) item.quantity = Math.min(99, item.quantity + 1); else cart.push({ id: add.dataset.addCart, quantity: 1 }); writeCart(cart); toast(t('added')); }
    const dismiss = e.target.closest('[data-dismiss-flash]'); if (dismiss) dismiss.closest('.flash').remove();
  });
  const nav = document.getElementById('nav-menu'), navToggle = document.getElementById('nav-toggle');
  if (nav && navToggle) {
    const setNav = open => {
      nav.classList.toggle('open', open);
      navToggle.setAttribute('aria-expanded', String(open));
      navToggle.setAttribute('aria-label', t(open ? 'close' : 'menu'));
    };
    navToggle.addEventListener('click', () => setNav(!nav.classList.contains('open')));
    nav.addEventListener('click', event => { if (event.target.closest('a')) setNav(false); });
    document.addEventListener('click', event => { if (!nav.contains(event.target) && !navToggle.contains(event.target)) setNav(false); });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && nav.classList.contains('open')) { setNav(false); navToggle.focus(); }
    });
    window.matchMedia('(min-width: 1051px)').addEventListener('change', () => setNav(false));
  }
  document.querySelectorAll('[data-password-toggle]').forEach(button => button.addEventListener('click', () => {
    const input = document.getElementById(button.dataset.passwordToggle), visible = input.type === 'password';
    input.type = visible ? 'text' : 'password'; button.setAttribute('aria-pressed', String(visible)); button.setAttribute('aria-label', t(visible ? 'hide_password' : 'show_password'));
  }));
  const themeToggle = document.getElementById('theme-toggle');
  function themeLabel() {
    const dark = document.documentElement.dataset.theme === 'dark';
    themeToggle.setAttribute('aria-label', t('theme') + ': ' + t(dark ? 'light' : 'dark'));
    themeToggle.setAttribute('aria-pressed', String(dark));
    document.querySelector('meta[name="theme-color"]').content = dark ? '#101113' : '#f6f6f1';
  }
  themeToggle.addEventListener('click', async () => { const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; document.documentElement.dataset.theme = theme; try { localStorage.setItem('techverse_theme', theme); } catch (_) {} themeLabel(); try { await api('/theme', { method: 'POST', body: { theme } }); } catch (e) { toast(e.message); } });
  document.querySelectorAll('[data-theme-choice]').forEach(button => button.addEventListener('click', () => { try { localStorage.setItem('techverse_theme', button.dataset.themeChoice); } catch (_) {} }));
  themeLabel();

  const addFeedback = new WeakMap();
  document.addEventListener('click', event => {
    const button = event.target.closest('[data-add-cart]');
    if (!button) return;
    clearTimeout(addFeedback.get(button));
    button.classList.add('is-added');
    addFeedback.set(button, setTimeout(() => button.classList.remove('is-added'), 1300));
  });
  const topButton = document.getElementById('back-to-top');
  if (topButton) {
    let queued = false;
    window.addEventListener('scroll', () => {
      if (queued) return;
      queued = true;
      requestAnimationFrame(() => { topButton.hidden = window.scrollY < 700; queued = false; });
    }, { passive: true });
    topButton.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
      const target = document.querySelector('.wordmark');
      if (target) target.focus({ preventScroll: true });
    });
  }

  document.querySelectorAll('form[data-enhanced-form]').forEach((form, formIndex) => {
    form.noValidate = true;
    const fields = [...form.querySelectorAll('input:not([type="hidden"]),select,textarea')];
    const summary = node('div', 'form-error-summary');
    summary.id = 'form-errors-' + formIndex;
    summary.tabIndex = -1;
    summary.hidden = true;
    summary.setAttribute('role', 'alert');
    form.prepend(summary);
    const password = form.querySelector('[name="password"]');
    const confirmation = form.querySelector('[name="confirm_password"]');
    function syncPasswords() {
      if (password && confirmation) confirmation.setCustomValidity(
        confirmation.value && confirmation.value !== password.value ? t('account_password_match') : '');
    }
    const originalDescriptions = new Map(fields.map(field => [field, field.getAttribute('aria-describedby') || '']));
    function validate(field) {
      const id = field.id + '-error';
      let error = document.getElementById(id);
      const valid = field.validity.valid;
      if (valid) {
        field.removeAttribute('aria-invalid');
        if (originalDescriptions.get(field)) field.setAttribute('aria-describedby', originalDescriptions.get(field));
        else field.removeAttribute('aria-describedby');
        if (error) error.remove();
        return true;
      }
      if (!error) {
        error = node('p', 'field-error');
        error.id = id;
        (field.closest('.field') || field.parentElement).append(error);
      }
      error.textContent = field.validationMessage;
      field.setAttribute('aria-invalid', 'true');
      field.setAttribute('aria-describedby', (originalDescriptions.get(field) + ' ' + id).trim());
      return false;
    }
    fields.forEach(field => {
      field.addEventListener('blur', () => { syncPasswords(); validate(field); });
      field.addEventListener('input', () => {
        syncPasswords();
        if (field.hasAttribute('aria-invalid')) validate(field);
        if (confirmation?.hasAttribute('aria-invalid')) validate(confirmation);
      });
    });
    form.addEventListener('submit', event => {
      syncPasswords();
      const invalid = fields.filter(field => !validate(field));
      if (invalid.length) {
        event.preventDefault();
        summary.replaceChildren(node('p', '', t('account_form_required')));
        const list = node('ul');
        invalid.forEach(field => {
          const item = node('li');
          const label = form.querySelector('label[for="' + field.id + '"]');
          const link = node('a', '', (label ? label.textContent : field.name) + ': ' + field.validationMessage);
          link.href = '#' + field.id;
          link.addEventListener('click', click => { click.preventDefault(); field.focus(); });
          item.append(link); list.append(item);
        });
        summary.append(list); summary.hidden = false; summary.focus();
        return;
      }
      summary.hidden = true;
      const submit = event.submitter || form.querySelector('button:not([type="button"])');
      if (submit) { submit.disabled = true; submit.setAttribute('aria-busy', 'true'); submit.textContent = t('form_sending'); }
    });
  });
  const listingCheckout = document.getElementById('listing-checkout-button');
  if (listingCheckout) listingCheckout.addEventListener('click', async () => { listingCheckout.disabled = true; try { const result = await api('/api/payments/checkout', { method: 'POST', body: { purpose: 'technician' } }); const target = new URL(result.url); if (target.protocol !== 'https:' || target.hostname !== 'checkout.stripe.com') throw new Error(t('checkout_unavailable')); window.location.assign(target.href); } catch (e) { toast(e.message); listingCheckout.disabled = false; } });
  const checkout = document.getElementById('checkout-button');
  if (checkout) checkout.addEventListener('click', async () => { checkout.disabled = true; try { const result = await api('/api/payments/checkout', { method: 'POST', body: {} }); const target = new URL(result.url); if (target.protocol !== 'https:' || target.hostname !== 'checkout.stripe.com') throw new Error(t('checkout_unavailable')); window.location.assign(target.href); } catch (e) { toast(e.message); checkout.disabled = false; } });
})();
