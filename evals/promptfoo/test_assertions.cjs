const assert = require('node:assert/strict');
const grade = require('./assertions.cjs');
const yes = {test: {metadata: {expected_supported: true, expected_sources: ['mem0']}}};
const no = {test: {metadata: {expected_supported: false, expected_sources: []}}};
const correct = {answer: 'Mem0 用于长期记忆。', supported: true, source_ids: ['mem0']};
assert.equal(grade(JSON.stringify(correct), yes).pass, true);
assert.equal(grade(JSON.stringify({answer: '资料不足', supported: false, source_ids: []}), no).pass, true);
assert.equal(grade('not json', yes).pass, false);
assert.equal(grade(JSON.stringify({...correct, source_ids: ['invented']}), yes).pass, false);
assert.equal(grade(JSON.stringify({...correct, supported: false}), yes).pass, false);
assert.equal(grade(JSON.stringify({...correct, source_ids: ['mem0', 'mem0']}), yes).pass, false);
// Demonstrate the evaluator's boundary: valid labels cannot verify answer meaning.
assert.equal(grade(JSON.stringify({...correct, answer: 'Mem0 是咖啡机。'}), yes).pass, true);
console.log('7 checks passed, including a known semantic false positive: manual review is still required.');
