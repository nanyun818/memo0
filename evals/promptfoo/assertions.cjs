// Structural/label checks only. A passing result does NOT prove factual accuracy.
module.exports = (output, context) => {
  const fail = (reason) => ({pass: false, score: 0, reason});
  let result;
  try { result = JSON.parse(output); } catch { return fail('Not a plain JSON response'); }
  if (!result || typeof result !== 'object' || Array.isArray(result)) return fail('Expected an object');
  if (Object.keys(result).sort().join(',') !== 'answer,source_ids,supported') return fail('Unexpected JSON fields');
  if (typeof result.answer !== 'string' || !result.answer.trim()) return fail('Missing nonempty answer');
  if (typeof result.supported !== 'boolean') return fail('supported must be boolean');
  if (!Array.isArray(result.source_ids) || result.source_ids.some(id => typeof id !== 'string')) return fail('source_ids must be a string array');
  if (new Set(result.source_ids).size !== result.source_ids.length) return fail('Duplicate source IDs');
  if (result.supported !== context.test.metadata.expected_supported) return fail('Evidence sufficiency label does not match the case');
  const expected = context.test.metadata.expected_sources;
  if (result.source_ids.length !== expected.length || result.source_ids.some(id => !expected.includes(id))) {
    return fail('Source IDs do not match the required supporting documents');
  }
  return {pass: true, score: 1, reason: 'Format, support label and source IDs pass; answer meaning still needs review'};
};
