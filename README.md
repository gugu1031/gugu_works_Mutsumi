# gugu_works_bsu

gugu-first-try

## Mutsumi Codex Pet

A quiet green-haired guitarist Codex custom pet.

This local version was rebuilt with the Hatch Pet workflow and image-generated polished chibi animation strips, using the supplied Mutsumi references. If this pet is later submitted publicly, make a more originalized version before publishing.

## Files

- `pet.json` - Codex custom pet manifest.
- `spritesheet.webp` - 8 x 9 spritesheet, `1536x1872`.
- `preview.png` - Hatch Pet contact sheet preview.
- `preview-*.gif` - per-state animation previews.
- `hatch-run/` - working files, validation JSON, source strips, contact sheet, and preview GIFs.

## Local Install

Copy this folder to:

```powershell
$env:USERPROFILE\.codex\pets\mutsumi
```

Then open Codex `Settings -> Appearance -> Pets`, refresh, and select the custom pet.

You can also run:

```powershell
powershell -ExecutionPolicy Bypass -File .\install-local.ps1
```

## Petdex Publish Flow

Petdex public install commands such as:

```bash
npx petdex install mutsumi
```

only work after the pet is submitted and approved by Petdex.

Submit with:

```bash
npx petdex login
npx petdex submit ./mutsumi
```

If the slug is already taken, use the slug returned by Petdex.
