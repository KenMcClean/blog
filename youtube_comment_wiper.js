/*
This is a script that runs in the browser console, and deletes all of the comments that the logged-in YouTube account has made.

Given the workarounds required to automate this process, it will come as no surprise that this will need to be run several times if the account has made a lot of comments.

*/


(async () => {
  try { window.onbeforeunload = null; } catch {}
  try {
    Object.defineProperty(window, 'onbeforeunload', {
      configurable: true,
      get() { return null; },
      set(_) { console.debug('[beforeunload] blocked window.onbeforeunload setter'); }
    });
  } catch {}
  const swallowBeforeUnload = (e) => { e.stopImmediatePropagation(); };
  window.addEventListener('beforeunload', swallowBeforeUnload, { capture: true });
  document.addEventListener('beforeunload', swallowBeforeUnload, { capture: true });
  (function patchAddEventListener(target, name) {
    const orig = target.addEventListener;
    target.addEventListener = function(type, listener, options) {
      if (type === 'beforeunload') {
        console.debug(`[beforeunload] blocked addEventListener on ${name}`);
        return;
      }
      return orig.call(this, type, listener, options);
    };
  })(window, 'window');
  (function patchAddEventListener(target, name) {
    const orig = target.addEventListener;
    target.addEventListener = function(type, listener, options) {
      if (type === 'beforeunload') {
        console.debug(`[beforeunload] blocked addEventListener on ${name}`);
        return;
      }
      return orig.call(this, type, listener, options);
    };
  })(document, 'document');

  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  const $all = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function realClick(el) {
    const opts = { bubbles: true, cancelable: true, view: window };
    el.dispatchEvent(new MouseEvent('mouseover', opts));
    el.dispatchEvent(new MouseEvent('mousedown', opts));
    el.dispatchEvent(new MouseEvent('mouseup', opts));
    el.dispatchEvent(new MouseEvent('click', opts));
  }

  const findLoadMore = () =>
    $all('button').find(b => b.textContent.trim().toLowerCase() === 'load more');

  const collectDeleteButtons = () =>
    $all('button[aria-label^="Delete activity item"]');

  const findConfirmDeleteButton = () =>
    $all('button').find(b => b.textContent.trim() === 'Delete');

  // ========= 2) Actions =========
  const clickLoadMoreUntilDone = async (maxRounds = 50) => {
    let rounds = 0;
    while (rounds < maxRounds) {
      const btn = findLoadMore();
      if (!btn) break;
      console.log(`[LoadMore] Clicking (round ${rounds + 1})`);
      realClick(btn);
      await sleep(2000); // allow items to append
      rounds++;
    }
    console.log('[LoadMore] Done (or no button found).');
  };

  const deleteBatch = async (maxPerBatch = 100) => {
    const buttons = collectDeleteButtons();
    if (!buttons.length) {
      console.log('[Delete] No delete buttons found.');
      return 0;
    }
    let count = 0;
    for (const btn of buttons.slice(0, maxPerBatch)) {
      try {
        const label = btn.getAttribute('aria-label') || '';
        console.log(`[Delete] Clicking: ${label.slice(0, 120)}…`);
        realClick(btn);
        await sleep(300); // wait for dialog
        const confirm = findConfirmDeleteButton();
        if (confirm) {
          realClick(confirm);
          await sleep(900); // allow request + DOM update
          count++;
        } else {
          console.warn('[Delete] Confirm button not found; skipping.');
          await sleep(300);
        }
      } catch (e) {
        console.warn('[Delete] Error:', e);
      }
    }
    console.log(`[Delete] Deleted ${count} item(s) in this batch.`);
    return count;
  };

for (let pass = 1; pass <= 20; pass++) {
    console.log(`\n=== PASS ${pass} ===`);
    await clickLoadMoreUntilDone();
    const deleted = await deleteBatch();
    if (deleted === 0) {
      // One last attempt in case new items attached after DOM settled
      await clickLoadMoreUntilDone();
      const deleted2 = await deleteBatch();
      if (deleted2 === 0) {
        console.log('[Done] No more items to delete. Exiting.');
        break;
      }
    }
    await sleep(1500); // settle time before next pass
  }
})();


