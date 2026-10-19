'use strict';
// This module registers engines, never property results. No backend injection.
const {createEngine}=require('./engine.js');
const owned=new WeakSet();
function freeze(value){if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.values(value).forEach(freeze);Object.freeze(value);}return value;}
function createTableEngine(){
 const data=freeze(require('./properties.json'));
 const engine=Object.freeze(createEngine(data));owned.add(engine);return engine;
}
module.exports={createTableEngine,owns:engine=>owned.has(engine)};
