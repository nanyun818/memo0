const fs = require('node:fs');
const grade = require('./assertions.cjs');
const tests = JSON.parse(fs.readFileSync(__dirname + '/judge-cases.json', 'utf8'));
for (const test of tests) {
  const actual = grade(test.vars.candidate, {test});
  console.log(`${test.description} | 程序规则=${actual.pass ? '通过' : '失败'} | 助教参考语义=${test.metadata.reference_judge_pass ? '通过' : '不通过'}`);
  console.log(test.vars.candidate);
}
console.log('仅预览，未调用裁判模型。参考标签由 AI 助教提出，需学习者核对。');
