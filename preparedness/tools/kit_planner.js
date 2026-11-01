/* Emergency kit and go-bag planner: pure logic. No DOM, no storage, no network.
   Items are rendered as static HTML (so the list works without JavaScript); these functions only decide which
   groups to show and format the visitor's own selections for printing or download. */
function kbVisibleGroups(groups, selected) {
  var sel = Array.isArray(selected) ? selected : [];
  return (Array.isArray(groups) ? groups : []).map(function (g) {
    var scen = g && typeof g.scenario === 'string' ? g.scenario : '';
    return { id: String(g && g.id || ''), visible: scen === '' || sel.indexOf(scen) !== -1 };
  });
}
function kbSummarize(items) {
  var total = 0, packed = 0;
  (Array.isArray(items) ? items : []).forEach(function (i) {
    if (!i || i.visible === false) return;
    total += 1; if (i.checked === true) packed += 1;
  });
  return { total: total, packed: packed, remaining: total - packed };
}
function kbSummaryText(s) {
  if (s.total === 0) return 'No items to show.';
  if (s.packed === 0) return s.total + ' items for your household. None ticked yet.';
  if (s.remaining === 0) return 'All ' + s.total + ' items ticked. Review the list again when your household or the seasons change.';
  return s.packed + ' of ' + s.total + ' items ticked; ' + s.remaining + ' still to do.';
}
function kbTextClean(s) { return String(s === null || s === undefined ? '' : s).replace(/[\u0000-\u001F\u007F]+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 400); }
function kbToText(opts) {
  opts = opts || {};
  var scen = (opts.scenarios || []).map(kbTextClean), L = [];
  L.push('EMERGENCY KIT AND GO-BAG CHECKLIST', 'Prepared with the Final Vestige Preparedness Archive. Kept on this device only.');
  L.push('For: ' + (scen.length ? scen.join('; ') : 'basic kit only'), '');
  var byGroup = {}, order = [];
  (opts.items || []).forEach(function (i) {
    if (!i || i.visible === false) return;
    var g = kbTextClean(i.groupTitle || i.group);
    if (!byGroup[g]) { byGroup[g] = []; order.push(g); }
    byGroup[g].push(i);
  });
  order.forEach(function (g) {
    L.push(g.toUpperCase());
    byGroup[g].forEach(function (i) { L.push('  [' + (i.checked === true ? 'x' : ' ') + '] ' + kbTextClean(i.label)); });
    L.push('');
  });
  L.push('This is a starting list. Customize it to your household, ask your pharmacist or prescriber about medicines, and follow local officials.');
  L.push('A completed checklist does not mean you are ready for any event.');
  return L.join('\n');
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { kbVisibleGroups: kbVisibleGroups, kbSummarize: kbSummarize, kbSummaryText: kbSummaryText, kbToText: kbToText, kbTextClean: kbTextClean };
}
