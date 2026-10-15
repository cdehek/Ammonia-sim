// Node-only execution bridge for the unchanged B1 loader and adapter.
// Browser measurements use the original loader directly.
import fs from 'node:fs';
import {loadEOS} from '../browser_eos_backend/loader.mjs';
import {createAdapter} from '../browser_eos_backend/adapter.mjs';
const ordinaryFetch=globalThis.fetch;
globalThis.fetch=async (url,...args)=>String(url).startsWith('file:')
 ?new Response(fs.readFileSync(new URL(url)),{headers:{'Content-Type':'application/wasm'}})
 :ordinaryFetch(url,...args);
export async function backend(build,guard){
 const eos=await loadEOS(build);
 return {eos,adapter:createAdapter(eos,guard)};
}
