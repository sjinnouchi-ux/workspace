# AI経営実装度診断WEBアプリ

経営者の前で営業マンが使う、AI実装度の限定URL診断アプリ。

## Current State

Project Git shell is ready. A structural implementation has started.

Before implementation, read both canonical specs:

1. `ai_keiei_shindan_app_spec.md`
2. `ai_keiei_shindan_web_impl_spec.md`

The web implementation spec v0.4 has been found. The logic spec is still pending confirmation, so current code intentionally avoids final question, choice, and result copy.

## Planned Structure

```text
ai-keiei-shindan/
├─ index.html
├─ gas/
│  ├─ Code.gs
│  └─ appsscript.json
├─ docs/
│  ├─ specs/
│  └─ SETUP.md
├─ tests/
│  └─ logic.test.js
└─ README.md
```

## Local Verification

```powershell
node tests/logic.test.js
```
