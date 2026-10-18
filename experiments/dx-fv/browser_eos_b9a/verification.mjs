import {exact,assert} from './values.mjs';
export async function verifyHash(value,expected){const raw=new TextEncoder().encode(JSON.stringify(exact(value))),hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',raw))].map(v=>v.toString(16).padStart(2,'0')).join('');assert(hash===expected,'STOP: original B9 scientific hash mismatch');return hash;}
