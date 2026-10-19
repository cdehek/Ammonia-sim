"""Credential metadata only: never reads auth configuration or secret values.

Candidate presence is not authentication. If one appears, use supported Wrangler
whoami privately; do not infer success from this probe. No account network calls.
"""
import json
import os
from pathlib import Path
import shutil

keys = ['CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_API_KEY', 'CLOUDFLARE_EMAIL',
        'CLOUDFLARE_ACCOUNT_ID', 'CF_API_TOKEN', 'CF_API_KEY', 'CF_ACCOUNT_ID']
paths = [Path.home() / '.wrangler/config/default.toml',
         Path.home() / '.config/.wrangler/config/default.toml']
if os.environ.get('XDG_CONFIG_HOME'):
    paths.append(Path(os.environ['XDG_CONFIG_HOME']) / '.wrangler/config/default.toml')
metadata = {'credentialEnvironmentPresence': {k: bool(os.environ.get(k)) for k in keys},
            'knownWranglerConfigPresent': any(p.is_file() for p in paths),
            'wranglerExecutableAvailable': bool(shutil.which('wrangler')),
            'authenticationVerifiedByThisProbe': False,
            'networkCallsMade': False}
print(json.dumps(metadata, indent=2))
