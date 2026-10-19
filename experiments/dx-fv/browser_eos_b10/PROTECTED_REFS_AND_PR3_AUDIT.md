# Preservation audit

Exact B9D start: 20ddac46423a7a742af19ac415ef8796cf3a429f. All 2,958 starting tracked files retain SHA-256 identity. Accepted A2 be9eb35a, B9C b67afb32, B9D, C1/C2, B6/B7 and all other historical artifacts remain unchanged. The operator feature branch remains at 262b6092; production main, demo release candidate and every starting remote head/tag are protected. No tags existed in the starting ls-remote inventory.

evidence/remote-refs-before.txt and remote-refs-final.txt record every protected branch identity; local-refs-before.txt and preservation-final.json record local preservation. The only permitted new remote ref is research/b10-operator-workstation-shadow-hookup-20261018. PR #3 stays open at head d4422425750a1d3c4e432cc103ac42ead40b7cc6 and base 0473d32f62db992fde0f581d116e1bd0c8e7d8ed, with identity/body/status unchanged. Full snapshots are pr3-before.json and pr3-final.json. No PR comments or mutations are made.

All committed differences from B9D are additions under this B10 directory. No historical checkpoint, main/feature/release branch, original training/history/Assist, scientific source, deployment configuration or production artifact is modified. Final publication receipts refer to the preceding audited commit to avoid a self-referential commit hash. Re-run preservation.py with fresh connector/remote receipts to verify the final branch.
