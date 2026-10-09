'use strict';
const {normalize}=require('./evaporator.cjs'),reference=require('./reference.json');
const copy=x=>JSON.parse(JSON.stringify(x));
function spec(heatKW=[4,4,4]){return {sectionCount:3,inletMinorK:1000,inlet:{p:4,h:500},outlet:{p:3.5,h:1700},initial:[{p:3.9,h:1000},{p:3.8,h:1400},{p:3.65,h:1650}],heatKW};}
function cases(engine){
 const dry=spec([6,6,6]);dry.initial=reference.steady[1].sections.map(v=>({p:v.p,h:v.h}));
 const cold=spec([6,6,6]);cold.initial=[{p:3.55,h:500},{p:3.53,h:500},{p:3.51,h:500}];
 const sealed=spec([.1,.1,.1]);sealed.initial=Array(3).fill({p:4,h:engine.statePX(4,.99).h});sealed.connections=normalize(sealed).connections.map(v=>({...v,closed:true}));
 const full=spec([1,1,1]);full.initial=[3.9,3.8,3.65].map(p=>({p,h:engine.statePT(p,engine.sat(p).T-2,'liquid').h}));
 const shutFaces=normalize(dry).connections.map((v,i)=>({...v,closed:i===0}));
 return [
  {name:'stiff startup',config:spec(),samples:[.05,.2,.6,1],changes:[]},
  {name:'cold wet startup',config:cold,samples:[1,5,20,60],changes:[]},
  {name:'heat loss and restoration',config:copy(dry),samples:[.1,.5,2,5,5.1,5.5,7,10],changes:[{seconds:0,patch:{heatKW:[4,4,4]}},{seconds:5,patch:{heatKW:[6,6,6]}}]},
  {name:'feed increase and decrease',config:copy(dry),samples:[.1,.5,2,5,5.1,5.5,7,10],changes:[{seconds:0,patch:{inlet:{p:4.3,h:500}}},{seconds:5,patch:{inlet:{p:4,h:500}}}]},
  {name:'feed isolation',config:copy(dry),samples:[.01,.05,.2,1,2],changes:[{seconds:0,patch:{connections:shutFaces,heatKW:[0,0,0]}}]},
  {name:'sealed boiling and condensation',config:sealed,samples:[1,5,10,11,15,20],changes:[{seconds:10,patch:{heatKW:[-.1,-.1,-.1]}}]},
  {name:'initial liquid-full transport',config:full,samples:[.001,.01,.1,1,10],changes:[]}
 ];
}
function accuracyOptions(relativeTolerance){return {relativeTolerance,massAbsoluteKg:relativeTolerance*1e-5,energyAbsoluteKJ:relativeTolerance*.01,pressureAbsoluteBar:Math.max(1e-6,relativeTolerance*.1),enthalpyAbsoluteKJkg:relativeTolerance*100};}
module.exports={spec,cases,accuracyOptions};
