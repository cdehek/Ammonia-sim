# Five complete exercise evidence comparisons

PASS in Chromium and desktop WebKit. All five B10 exports are byte-for-byte equal to the actual pinned workstation baseline files. Comparison includes the entire JSON: original SI histories, times, grading evidence, objective completion, quiz/actions, accepted boundaries, stop events, final state and interpretation. It does not compare only banners. Full candidate files are in evidence/training-{browser}; baseline files are in evidence/baseline-training.

| Browser | Exercise | Bytes | SI samples | Events | Completion s | SHA-256 |
|---|---|---|---|---|---|---|
| chromium | startup | 137362 | 70 | 10 | 60.00000000000058 | 732a8e158dcdb38df5c85db6fff0962421fccc37f7e8704f3c4b8849671adc80 |
| chromium | load | 138804 | 70 | 9 | 60.00000000000059 | 60472eb042775480fe1910b7dc8da2e53b8797c30ce3bc3fe89c7190bbf51a37 |
| chromium | restriction | 98190 | 48 | 7 | 40.00000000000004 | 87a81d2aac1b31e813efccb9ad1919411c7fe92b6c09d8aa2a6a83caee7b958d |
| chromium | tuning | 360025 | 191 | 12 | 178.0000000000037 | c048f882caadb9ecdf9aab02885407524f3ccd5b51ab86e167d9aaed8041fcf9 |
| chromium | hot | 182995 | 92 | 15 | 75.12500000000749 | 026abd33d113b5871e70374d7009ad818317830f3e7de23dfb70a3feb4f1bf6a |
| webkit | startup | 137356 | 70 | 10 | 60.00000000000058 | 2a442a0c295238800f81c139af9973c5c520eff6b9edf156099aaa1475930812 |
| webkit | load | 138792 | 70 | 9 | 60.00000000000059 | 6cd9eea812aeff6286247e1ef27b623b5832bdde4f08caa440e91cdea43321dd |
| webkit | restriction | 98175 | 48 | 7 | 40.00000000000004 | 2eedff6eba6cc4c46d06585cbf81ce196c652383d753127a7615aaf40149e72b |
| webkit | tuning | 359978 | 191 | 12 | 178.0000000000037 | 5fb66490212a9eb03a39392a4fdc2e2c5ef0736c9be5bc7616f67bbccb3aa9bd |
| webkit | hot | 183031 | 92 | 15 | 75.12500000000749 | bc86fc75a8ca71673878bb41bed7024895e35350d69099ed95dbaa85b56a15a8 |

The startup exercise also completes with A2 uninitialized on a fresh workstation. All five complete after an independent A2 session has existed; A2 session/snapshot/history hashes remain unchanged during training. Hot Condenser Air uses the genuine original equipment trip, off-state restoration, clearing and accepted continuation. Existing original console tests independently compare the entire exports against their historical contract in both browsers. Retained reading/timestamp tests and original frozen-report assertions pass. No training, scoring, recipe, accepted-history or Assist source is modified.
