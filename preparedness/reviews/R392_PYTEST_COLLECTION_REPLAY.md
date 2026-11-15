# R392 Preparedness review — deterministic Python collection repair

**DRAFT / HARD HOLD. Source/citation and fixture gates only. No publication authorization.**

On the isolated available R381–R389/R391 source-test assembly, `python -m pytest -q preparedness/tests` originally reported **1,023 passed, 62 subtests passed, 2 errors**. Both errors were false global function collection: the R388 source URL alias test generator and R391 frozen export race test generator leave a module-level function named `test(self,...)` bound after their class method registration. Under pytest, the stray function is collected with an unknown `self` fixture.

This PR renames ONLY those generator-local functions to `_case` and updates their `setattr` references, retaining the full set of actual synthetic tests and their assertions. It does not change the validators, the seven Claude source branches, nine Shelter variants, original 35 manuscripts, sources, metadata, URLs, safety states, WordPress files, or test fixtures. The same local assembly after the fixes reports **1,023 passed, 62 subtests passed, 0 errors** in 12.46 s, Python 3.13.5 (isolated assembly only).

These local results are NOT an authenticated native repository validate/build, hosted CI PASS, real 50+ WordPress and private preview export verification, qualified emergency/medical/food/water/privacy review, merchant validation, or QD approval. All those remain unverified. Existing QA #157 and fixture #169 remain separate draft review lanes; dependent #2205 is untouched.

**Next review:** run hosted pytest collection and full native checks against the complete authenticated repository; keep five source collisions and nine Shelter forks unselected, reject false QD PASS.

References: #136 (technical), #820 (conversion), #818 (business).