'use strict';
/**
 * Integrity-sensitive images (technical PNG diagrams, GIF animations, vector SVG)
 * are not automatically the same image after output-format negotiation.
 * This only controls URL source identity. It grants no reproduction rights.
 */
const isFormatSensitive = value => /\.(?:png|gif|svg)$/i.test(String(value || '').split(/[?#]/, 1)[0]);
const isFormatSelector = key => ['format', 'fm', 'auto'].includes(String(key).toLowerCase());
function materialSelectors(pathOrTitle, params) {
  if (!isFormatSensitive(pathOrTitle)) return [];
  return [...params].filter(pair => Array.isArray(pair) && isFormatSelector(pair[0]));
}
module.exports = {isFormatSensitive, isFormatSelector, materialSelectors};
