(() => {
  'use strict';
  const { t, node, api, toast, readCart, writeCart, money, icon } = window.TechVerse;
  const itemsNode = document.getElementById('cart-items'), form = document.getElementById('order-form'); let products = new Map(), cart = [];
  function render() {
    itemsNode.replaceChildren(); let subtotal = 0, quoteItems = 0;
    for (const item of cart) {
      const product = products.get(item.id); if (!product) continue;
      if (product.price_cents === null) quoteItems += item.quantity; else subtotal += product.price_cents * item.quantity;
      const row = node('article', 'cart-item'), image = node('img'); image.src = product.image_url || '/static/' + product.image_path; image.alt = product.name; image.width = 95; image.height = 80;
      const body = node('div'), title = node('h3', '', product.name), link = node('a'); link.href = '/shop/product/' + product.id; link.append(title); body.append(link, node('div', 'product-price', product.price_cents === null ? t('request_price') : money(product.price_cents * item.quantity)));
      const control = node('div', 'cart-quantity'), label = node('label', '', t('quantity')), input = node('input'); input.type = 'number'; input.min = '1'; input.max = '99'; input.value = item.quantity; input.id = 'qty-' + item.id; label.htmlFor = input.id;
      input.addEventListener('change', () => { const value = Number(input.value); item.quantity = Number.isInteger(value) && value >= 1 && value <= 99 ? value : 1; writeCart(cart); render(); }); control.append(label, input); body.append(control);
      const remove = node('button', 'remove-item'); remove.type = 'button'; remove.setAttribute('aria-label', t('remove') + ': ' + product.name); remove.append(icon('trash')); remove.addEventListener('click', () => { cart = cart.filter(i => i.id !== item.id); writeCart(cart); render(); });
      row.append(image, body, remove); itemsNode.append(row);
    }
    document.getElementById('cart-empty').hidden = cart.length !== 0; document.getElementById('cart-summary').hidden = cart.length === 0;
    document.getElementById('cart-subtotal').textContent = money(subtotal); document.getElementById('cart-quotes').textContent = quoteItems;
    document.getElementById('order-result').hidden = true;
  }
  form.addEventListener('submit', async e => {
    e.preventDefault(); if (!cart.length) return; const button = document.getElementById('order-submit'); button.disabled = true;
    try {
      const values = Object.fromEntries(new FormData(form)); const result = await api('/api/orders', { method: 'POST', body: { ...values, items: cart.map(i => ({ id: i.id, quantity: i.quantity })) } });
      const output = document.getElementById('order-result'); output.replaceChildren(node('p', '', result.message + ' #' + result.id));
      if (result.whatsapp_configured) { const link = node('a', 'btn btn-secondary full-width', t('send_whatsapp')); link.href = result.whatsapp_url; link.target = '_blank'; link.rel = 'noopener noreferrer'; output.append(link); }
      output.hidden = false; toast(t('request_saved')); output.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    } catch (err) { toast(err.message); } finally { button.disabled = false; }
  });
  api('/api/products').then(data => { products = new Map(data.products.map(p => [p.id, p])); cart = readCart().filter(i => products.has(i.id)); writeCart(cart); render(); }).catch(err => { itemsNode.append(node('p', 'notice', err.message)); });
})();
