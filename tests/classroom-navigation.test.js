import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {classroomRoute,classroomGroups,outcomePath} from '../lib/classroom-navigation.js';

test('classroom and outcome routes distinguish landing, isolated practice and admin management',()=>{
 assert.deepEqual(classroomRoute('#/classrooms/10G3'),{classroom:'10G3',examWeek:9,validWeek:true,manage:false,outcomeId:null});
 assert.equal(classroomRoute('#/classrooms/10G3/exams/week-8').outcomeId,null);
 assert.equal(classroomRoute(outcomePath('9G3','one')).outcomeId,'one');
 assert.equal(classroomRoute('#/classrooms/10A1/manage').manage,true);
 assert.equal(classroomRoute('#/classrooms/unknown/outcomes/one').classroom,null);
});
test('outcome groups partition each classroom without mixing questions or losing unassigned practice',async()=>{
 const {questions}=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url)));
 const {outcomes,assignments}=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url)));
 for(const [classroom,count,written] of [['10A1',35,7],['10G3',48,10],['9G3',25,8]]){
  const groups=classroomGroups(classroom,questions,outcomes,assignments),all=groups.flatMap(g=>g.questions);
  assert.equal(all.length,count);assert.equal(new Set(all.map(q=>q.id)).size,count);
  assert.equal(all.filter(q=>q.type==='FRQ').length,written);
  assert(all.every(q=>q.classroom===classroom));
  assert(groups.every(g=>g.id==='unassigned'||g.classroom===classroom));
 }
 assert.equal(classroomGroups('10A1',questions,outcomes,assignments).find(g=>g.id==='unassigned').questions.length,15);
 assert(!classroomGroups('10G3',questions,outcomes,assignments).some(g=>g.classroom==='10A1'));
});
