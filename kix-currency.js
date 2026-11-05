(() => {
  'use strict';
  if (window.__KIX_CURRENCY_READY__) return;
  window.__KIX_CURRENCY_READY__ = true;

  // Official public-facing rate: 1 USD = 1,520 IQD.
  const IQD_PER_USD = 1520;
  const STORAGE_KEY = 'kix-display-currency';
  let currency = localStorage.getItem(STORAGE_KEY) === 'USD' ? 'USD' : 'IQD';
  const originals = new WeakMap();
  const elementOriginals = new WeakMap();
  let updating = false;

  const toLatin = value => value.replace(/[٠-٩۰-۹]/g, ch => {
    const a = '٠١٢٣٤٥٦٧٨٩'.indexOf(ch);
    return String(a >= 0 ? a : '۰۱۲۳۴۵۶۷۸۹'.indexOf(ch));
  });
  const parseAmount = value => {
    const normalized = toLatin(value).replace(/[٬،\s]/g, '').replace(/,/g, '');
    const n = Number(normalized);
    return Number.isFinite(n) ? n : null;
  };
  const formatIQD = n => new Intl.NumberFormat('en-US', {maximumFractionDigits:0}).format(Math.round(n)) + ' د.ع';
  const formatUSD = n => '$' + (n / IQD_PER_USD).toFixed(2);

  function convertText(source) {
    if (!/(د\s*\.\s*ع|ع\s*\.\s*د|دينار|IQD)/i.test(source)) return source;
    let output = source;
    const after = /(\d[\d٠-٩۰-۹٬،,. ]*)\s*(د\s*\.\s*ع|ع\s*\.\s*د|دينار(?:\s*عراقي)?|IQD)/gi;
    output = output.replace(after, (whole, raw) => {
      const amount = parseAmount(raw);
      return amount === null ? whole : (currency === 'USD' ? formatUSD(amount) : formatIQD(amount));
    });
    const before = /(IQD|د\s*\.\s*ع|ع\s*\.\s*د)\s*(\d[\d٠-٩۰-۹٬،,. ]*)/gi;
    output = output.replace(before, (whole, _symbol, raw) => {
      const amount = parseAmount(raw);
      return amount === null ? whole : (currency === 'USD' ? formatUSD(amount) : formatIQD(amount));
    });
    return output;
  }

  function isStandalonePrice(value) {
    return /^\s*(?:(?:د\s*\.\s*ع|ع\s*\.\s*د|IQD)\s*[\d٠-٩۰-۹][\d٠-٩۰-۹٬،,. ]*|[\d٠-٩۰-۹][\d٠-٩۰-۹٬،,. ]*\s*(?:د\s*\.\s*ع|ع\s*\.\s*د|دينار(?:\s*عراقي)?|IQD))\s*$/i.test(value);
  }

  function processPriceElement(element) {
    if (!element || element.nodeType !== Node.ELEMENT_NODE || updating) return;
    if (element.closest('script,style,textarea,input,[contenteditable="true"],.kix-currency-control,.kix-currency-wrap')) return;
    const current = element.textContent || '';
    if (!isStandalonePrice(current)) return;
    if (!elementOriginals.has(element)) elementOriginals.set(element, current);
    const next = convertText(elementOriginals.get(element));
    if (current !== next) {
      updating = true;
      element.textContent = next;
      updating = false;
    }
  }

  function processTextNode(node) {
    if (!node || node.nodeType !== Node.TEXT_NODE || !node.parentElement || updating) return;
    if (node.parentElement.closest('script,style,textarea,input,[contenteditable="true"],.kix-currency-control,.kix-currency-wrap')) return;
    if (!originals.has(node)) originals.set(node, node.nodeValue);
    const next = convertText(originals.get(node));
    if (node.nodeValue !== next) {
      updating = true;
      node.nodeValue = next;
      updating = false;
    }
  }

  function scan(root) {
    if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) processTextNode(node);
    if (root.nodeType === Node.ELEMENT_NODE) processPriceElement(root);
    if (root.querySelectorAll) root.querySelectorAll('*').forEach(processPriceElement);
  }

  function renderAll() {
    scan(document.body);
    const button = document.querySelector('.kix-currency-control');
    if (button) {
      button.textContent = currency === 'IQD' ? 'عرض الأسعار بالدولار USD' : 'عرض الأسعار بالدينار د.ع';
      button.setAttribute('aria-label', currency === 'IQD' ? 'Switch prices to US dollars' : 'Switch prices to Iraqi dinars');
    }
    const note = document.querySelector('.kix-currency-note');
    if (note) note.textContent = 'سعر التحويل: 1 دولار = ' + IQD_PER_USD.toLocaleString('en-US') + ' دينار، وفق سعر بيع الدولار للجمهور المعلن من البنك المركزي العراقي.';
  }

  function mountControl() {
    if (document.querySelector('.kix-currency-control')) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'kix-currency-control';
    button.addEventListener('click', () => {
      currency = currency === 'IQD' ? 'USD' : 'IQD';
      localStorage.setItem(STORAGE_KEY, currency);
      renderAll();
      window.dispatchEvent(new Event('kix-currency-changed'));
    });
    const note = document.createElement('span');
    note.className = 'kix-currency-note';
    const wrap = document.createElement('div');
    wrap.className = 'kix-currency-wrap';
    wrap.append(button, note);
    const header = document.querySelector('header, .site-header, .navbar, nav');
    if (header) header.prepend(wrap);
    else document.body.prepend(wrap);
  }

  function start() {
    mountControl();
    renderAll();
    const observer = new MutationObserver(records => {
      for (const record of records) {
        if (record.type === 'characterData') processTextNode(record.target);
        else for (const added of record.addedNodes) {
          if (added.nodeType === Node.TEXT_NODE) processTextNode(added);
          else if (added.nodeType === Node.ELEMENT_NODE) scan(added);
        }
      }
    });
    observer.observe(document.body, {subtree:true, childList:true, characterData:true});
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once:true});
  else start();
})();