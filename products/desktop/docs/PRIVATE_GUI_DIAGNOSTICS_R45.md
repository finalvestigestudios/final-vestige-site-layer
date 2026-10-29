# R45 — Fixed-text GUI error privacy for six local-first desktop apps

**Development / release HOLD.** User-controlled CSV headers, invoice IDs, paths,
report names, reviewer fields and OS error details may be embedded in exceptions.
The R44 main window displayed raw exception strings in two places, and the human
premium review workbench displayed raw exception strings in five error dialogs.
R45 replaces all seven with **fixed diagnostic text**. Neither exception
strings nor repr are accessed by the new renderer; it branches on exception
type only and supplies fixed operation-specific recovery guidance.

## Changed behavior

- All four free and two premium launchers use the same error renderer on report
  generation. The main status line and error modal show the same safe text.
- A premium review-window construction error is caught and safely presented
  instead of surfacing as an unhandled Tk callback traceback. Entitlement
  checks remain enforced inside the reviewer and immediately before launch.
- The premium workbench uses safe messages for loading reports, recording human
  decisions, exporting, sealing encrypted evidence, and restoring vaults.
- No telemetry, network logging, automatic approval, original-file editing,
  or changes to the exact Decimal financial engines are introduced.
- Deliberately, this means some detailed CSV validation reasons are no longer
  visible in dialogs. Users should check known schema/docs; an eventual
  structured, privacy-safe error-code system can restore granular guidance
  without echoing user-controlled strings.

## Regression proof

Run in a full checkout:

```shell
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -m unittest discover -s products/desktop/tests -p test_ui_error_privacy_r45.py -v
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -OO -m unittest discover -s products/desktop/tests -p test_ui_error_privacy_r45.py -v
```

Tests inject private Windows/Linux paths, customer identifiers, multiline
payloads, formula-like text, massive error strings, hostile exceptions whose
`__str__`/`__repr__` raise, and platform filesystem exception types. They also
statically inspect both GUI modules for unsafe raw `str(exc)` rendering.
When only the focused helper/tests subset is available, the full-checkout
GUI-module inspection is skipped; it must pass in a real CI/Windows checkout.

## Release prerequisites

Complete full repository tests, native Windows 11 x64 six-EXE packaging and
manual GUI acceptance, anti-malware scans, checksum verification, private premium
entitlement/download testing, and independent human QD signoff. Do not publish
untested or unrestricted premium binaries.
