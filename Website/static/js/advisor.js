(() => {
  'use strict';
  const { t, node, api, toast, icon, sourceUrl, ui } = window.TechVerse;
  const data = JSON.parse(document.getElementById('advisor-data').textContent), models = new Map(data.catalogs.map(c => [c.id, c]));
  const local = (value, key) => ui.language === 'ar' ? value[key + '_ar'] || value[key] : value[key];
  const lookupPanel = document.getElementById('lookup-panel'), chatPanel = document.getElementById('chat-panel');
  function tab(which) { const chat = which === 'chat'; lookupPanel.hidden = chat; chatPanel.hidden = !chat; for (const id of ['lookup', 'chat']) { const button = document.getElementById(id + '-tab'); const active = (id === 'chat') === chat; button.classList.toggle('active', active); button.setAttribute('aria-selected', String(active)); button.tabIndex = active ? 0 : -1; } }
  document.getElementById('lookup-tab').addEventListener('click', () => { tab('lookup'); history.replaceState(null, '', '#lookup'); });
  document.getElementById('chat-tab').addEventListener('click', () => { tab('chat'); history.replaceState(null, '', '#chat'); });
  document.querySelector('.tab-row').addEventListener('keydown', e => { if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) { e.preventDefault(); const target = e.key === 'Home' ? 'lookup' : e.key === 'End' ? 'chat' : lookupPanel.hidden ? 'lookup' : 'chat'; tab(target); document.getElementById(target + '-tab').focus(); } });
  if (location.hash === '#chat') tab('chat');
  const modelSelect = document.getElementById('model-select'), alarmType = document.getElementById('alarm-type'), code = document.getElementById('error-code');
  const resultNode = document.getElementById('lookup-result'), specs = document.getElementById('model-specs'), heading = document.getElementById('model-heading');
  function linkForSource(source, label) { const link = node('a', '', label); link.href = sourceUrl(source); link.target = '_blank'; link.rel = 'noopener noreferrer'; return link; }
  function updateModel() {
    resultNode.hidden = true; code.value = ''; specs.replaceChildren(); specs.hidden = true;
    document.querySelectorAll('[data-catalog-model]').forEach(panel => { panel.hidden = panel.dataset.catalogModel !== modelSelect.value; });
    document.querySelectorAll('[data-select-model]').forEach(card => { const active = card.dataset.selectModel === modelSelect.value; card.classList.toggle('selected', active); card.setAttribute('aria-current', active ? 'true' : 'false'); });
    const model = models.get(modelSelect.value); document.getElementById('code-list').replaceChildren();
    if (!model) { document.getElementById('inverter-photo').hidden = true; return; }
    heading.textContent = model.brand + ' ' + model.model;
    const image = document.getElementById('inverter-img'); document.getElementById('inverter-photo').hidden = !model.image;
    if (model.image) { image.src = '/static/' + model.image; image.alt = model.brand + ' ' + model.model; }
    updateCodes();
    if (model.specs.length) { specs.append(node('h3', '', t('specifications'))); for (const spec of model.specs) { const row = node('div', 'spec-row'); const value = node('strong', '', spec.value); value.dir = 'ltr'; row.append(node('span', '', local(spec, 'label')), value); specs.append(row); } const source = node('div', 'source-footnote'); source.append(linkForSource({ ...model.source, page: (model.spec_pages || [])[0] }, t('manual_source') + ((model.spec_pages || []).length ? ' · ' + t('page') + ' ' + model.spec_pages.join('–') : ''))); specs.append(source); specs.hidden = false; }
  }
  function updateCodes() { resultNode.hidden = true; const model = models.get(modelSelect.value); const list = document.getElementById('code-list'); list.replaceChildren(); if (!model) return; for (const entry of model.entries.filter(e => e.type === alarmType.value)) { const option = node('option'); option.value = entry.code; option.label = local(entry, 'name'); list.append(option); } }
  document.querySelectorAll('[data-brand]').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('[data-brand]').forEach(b => { const active = b === button; b.classList.toggle('active', active); b.setAttribute('aria-pressed', String(active)); });
    const options = data.catalogs.filter(c => c.brand === button.dataset.brand); const placeholder = node('option', '', t('choose_model')); placeholder.value = ''; modelSelect.replaceChildren(placeholder);
    options.forEach(c => { const option = node('option', '', c.model); option.value = c.id; modelSelect.append(option); });
    document.querySelectorAll('[data-model-brand]').forEach(card => { card.hidden = card.dataset.modelBrand !== button.dataset.brand; });
    document.querySelectorAll('[data-catalog-model]').forEach(panel => { panel.hidden = true; });
    document.querySelectorAll('[data-select-model]').forEach(card => { card.classList.remove('selected'); card.removeAttribute('aria-current'); });
    heading.textContent = button.dataset.brand; document.getElementById('lookup-fields').hidden = !options.length; document.getElementById('pending-manual').hidden = !!options.length; document.getElementById('inverter-photo').hidden = true;
    if (!options.length) { const pending = data.pending.find(c => c.brand === button.dataset.brand); if (pending && pending.image) { document.getElementById('inverter-photo').hidden = false; const img = document.getElementById('inverter-img'); img.src = '/static/' + pending.image; img.alt = pending.brand + ' ' + (pending.model || ''); } }
    resultNode.hidden = true; specs.hidden = true; code.value = '';
    if (options.length === 1) { modelSelect.value = options[0].id; updateModel(); }
  }));
  modelSelect.addEventListener('change', updateModel); alarmType.addEventListener('change', () => { code.value = ''; updateCodes(); });
  const lookup = document.getElementById('lookup-button');
  async function findCode() {
    if (!modelSelect.value) { toast(t('choose_model')); modelSelect.focus(); return; } if (!code.value.trim()) { toast(t('choose_code')); code.focus(); return; }
    lookup.disabled = true; resultNode.hidden = true;
    try {
      const result = await api('/api/lookup?' + new URLSearchParams({ model: modelSelect.value, type: alarmType.value, code: code.value }));
      resultNode.replaceChildren(node('span', 'eyebrow muted', t('checked_manual')));
      const title = node('div', 'result-title'), text = node('div'); text.append(node('span', 'small', result.type_label), node('h3', '', result.name)); title.append(node('div', 'result-code', result.code), text); resultNode.append(title, node('h4', '', t('safe_steps')));
      const list = node('ol', 'steps-list'); result.steps.forEach(step => list.append(node('li', '', step))); resultNode.append(list); if (result.manual_note) resultNode.append(node('p', 'notice', result.manual_note));
      const footnote = node('div', 'source-footnote'), link = linkForSource(result.source, t('read_manual')); link.prepend(icon('book')); footnote.append(link, node('span', '', t('page') + ' ' + result.source.page), node('span', '', local(result.source, 'edition'))); resultNode.append(footnote); resultNode.hidden = false;
    } catch (error) { resultNode.replaceChildren(node('p', 'notice', error.message)); resultNode.hidden = false; } finally { lookup.disabled = false; }
  }
  lookup.addEventListener('click', findCode); code.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); findCode(); } });
  document.querySelectorAll('[data-select-model]').forEach(card => card.addEventListener('click', event => {
    event.preventDefault();
    const model = models.get(card.dataset.selectModel); if (!model) return;
    const brand = [...document.querySelectorAll('[data-brand]')].find(button => button.dataset.brand === model.brand);
    if (brand) brand.click(); modelSelect.value = model.id; updateModel();
    const url = new URL(location.href); url.searchParams.set('model', model.id); url.hash = 'lookup'; history.replaceState(null, '', url);
    const panel = document.querySelector('[data-catalog-model="' + model.id + '"]'); if (panel) panel.open = true;
    document.getElementById('lookup-fields').scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }));
  const gallery = document.getElementById('model-gallery');
  const chooseAnother = document.getElementById('choose-another-model');
  function showGallery(show) {
    gallery.hidden = !show;
    chooseAnother.hidden = false;
    chooseAnother.setAttribute('aria-expanded', String(show));
  }
  chooseAnother.addEventListener('click', () => {
    const show = gallery.hidden; showGallery(show);
    if (show) {
      const target = gallery.querySelector('[data-select-model]:not([hidden])');
      if (target) target.focus({ preventScroll: true });
      gallery.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    }
  });
  document.querySelectorAll('[data-select-model]').forEach(card => card.addEventListener('click', () => showGallery(false)));
  document.querySelectorAll('[data-brand]').forEach(button => button.addEventListener('click', () => {
    if (!chooseAnother.hidden) showGallery(true);
  }));
  const initialModel = models.get(data.initialModel);
  const initial = [...document.querySelectorAll('[data-brand]')].find(button => button.dataset.brand === (initialModel ? initialModel.brand : 'Growatt')) || document.querySelector('[data-brand]');
  if (initial) initial.click();
  if (initialModel) { modelSelect.value = initialModel.id; updateModel(); showGallery(false); }

  // Saved conversations are always requested through the account-protected API.
  const messages = document.getElementById('chat-messages'), emptyTemplate = document.getElementById('chat-empty').cloneNode(true), historyNode = document.getElementById('conversation-list');
  const chatModel = document.getElementById('chat-model'), chatAlarm = document.getElementById('chat-alarm-type'), form = document.getElementById('chat-form'); let currentId = null, sending = false;
  function prompts() { messages.querySelectorAll('[data-prompt]').forEach(button => button.addEventListener('click', () => { if (!form) { toast(t('member_required')); return; } document.getElementById('chat-input').value = button.dataset.prompt; document.getElementById('chat-input').focus(); })); }
  function reset() { if (sending) return; currentId = null; messages.replaceChildren(emptyTemplate.cloneNode(true)); prompts(); markConversation(); }
  function markConversation() { historyNode.querySelectorAll('[data-conversation]').forEach(row => row.classList.toggle('active', Number(row.dataset.conversation) === currentId)); }
  function appendMessage(role, content, metadata = {}) {
    const empty = messages.querySelector('#chat-empty'); if (empty) empty.remove();
    const row = node('div', 'chat-message ' + role);
    if (role === 'user') row.textContent = content;
    else {
      const avatar = node('img', 'assistant-avatar'); avatar.src = '/static/images/logo.png'; avatar.alt = 'TechVerse'; const body = node('div', 'message-body');
      if (metadata.notice) body.append(node('div', 'message-notice', metadata.notice)); body.append(node('div', 'message-text', content));
      if (metadata.sources && metadata.sources.length) { const sourceList = node('div', 'message-sources'); metadata.sources.forEach(source => sourceList.append(linkForSource(source, source.title + (source.page ? ' · ' + t('page') + ' ' + source.page : '')))); body.append(sourceList); }
      body.append(node('div', 'message-mode', t(metadata.mode === 'ai' ? 'chat_ai_mode' : 'chat_source_mode'))); row.append(avatar, body);
    }
    messages.append(row); messages.scrollTop = messages.scrollHeight; return row;
  }
  async function loadConversation(id) {
    if (sending) return;
    try { const result = await api('/api/conversations/' + id); currentId = result.conversation.id; chatModel.value = result.conversation.model_id; messages.replaceChildren(); for (const msg of result.messages) appendMessage(msg.role, msg.content, msg.metadata); markConversation(); } catch (err) { toast(err.message); }
  }
  async function loadHistory() {
    if (!data.membershipActive) return;
    try {
      const result = await api('/api/conversations'); historyNode.replaceChildren();
      if (!result.conversations.length) historyNode.append(node('p', 'muted small', t('no_chats')));
      result.conversations.forEach(c => { const row = node('div', 'conversation-row'); row.dataset.conversation = c.id; const open = node('button', '', c.title); open.title = c.title; open.addEventListener('click', () => loadConversation(c.id)); const remove = node('button', 'delete-button'); remove.setAttribute('aria-label', t('delete_chat') + ': ' + c.title); remove.append(icon('trash')); remove.addEventListener('click', async () => { if (sending) return; try { await api('/api/conversations/' + c.id, { method: 'DELETE' }); if (currentId === c.id) reset(); await loadHistory(); } catch (err) { toast(err.message); } }); row.append(open, remove); historyNode.append(row); }); markConversation();
    } catch (error) { toast(error.message); }
  }
  document.getElementById('new-chat').addEventListener('click', reset); chatModel.addEventListener('change', reset); prompts(); loadHistory();
  if (form) {
    const input = document.getElementById('chat-input'), send = document.getElementById('chat-send');
    input.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); form.requestSubmit(); } });
    form.addEventListener('submit', async e => {
      e.preventDefault(); if (sending) return; if (!chatModel.value) { toast(t('select_model_chat')); chatModel.focus(); return; }
      const text = input.value.trim(); if (!text) return; const userRow = appendMessage('user', text), thinking = node('div', 'chat-thinking', t('thinking')); messages.append(thinking); messages.scrollTop = messages.scrollHeight;
      sending = true; send.disabled = true; chatModel.disabled = true; input.value = '';
      try { const result = await api('/api/chat', { method: 'POST', body: { model_id: chatModel.value, alarm_type: chatAlarm.value, message: text, conversation_id: currentId } }); currentId = result.conversation_id; thinking.remove(); appendMessage('assistant', result.reply, result); await loadHistory(); }
      catch (error) { thinking.remove(); userRow.remove(); input.value = text; toast(error.message); }
      finally { sending = false; send.disabled = false; chatModel.disabled = false; input.focus(); }
    });
  }
})();
