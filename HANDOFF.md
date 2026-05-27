# Mutsumi Pet Worklog

Paused on: 2026-05-25

## Current Status

2026-05-26 update: the pet has been rebuilt with the official cached Hatch Pet workflow instead of the earlier handmade pixel script.

- Hatch Pet skill source used:
  - `C:\Users\gujia\.codex\vendor_imports\skills\skills\.curated\hatch-pet\SKILL.md`
- Run directory:
  - `E:\ruoyemucodexpet\hatch-run`
- Final Hatch outputs:
  - `E:\ruoyemucodexpet\hatch-run\final\spritesheet.webp`
  - `E:\ruoyemucodexpet\hatch-run\qa\contact-sheet.png`
  - `E:\ruoyemucodexpet\hatch-run\qa\previews\*.gif`
- Root and `mutsumi/` have been refreshed from the Hatch outputs.
- `pet.json` is now the Codex custom pet manifest shape:
  - `id`
  - `displayName`
  - `description`
  - `spritesheetPath`

Validation from Hatch scripts:

- `inspect_frames.py`: ok, no errors, no warnings.
- `validate_atlas.py`: ok, `1536x1872`, `RGBA`, `transparent_rgb_residue_pixels: 0`.

Visual quality note:

- This version is no longer the handmade blocky pixel pet.
- It uses image-generated polished anime chibi strips with real state rows.
- The look is much closer to the Yachiyo reference style, though final taste review is still up to the user.

- Workspace root `E:\ruoyemucodexpet` is currently a Petdex/Codex pet pack.
- Current manifest format has been changed to official-style `codexpet.v1`.
- Current generated sprite source is:
  - `C:\Users\gujia\.codex\generated_images\019e4b29-42f1-7f22-b6e1-07273da2be12\ig_03a80af926a0745a016a14717a7b708191a8fd09ec4ee0d8b0.png`
- Current outputs:
  - `pet.json`
  - `spritesheet.webp`
  - `spritesheet.png`
  - `preview.png`
  - `preview-*.gif`
  - mirrored copy under `mutsumi/`

## Important Lesson

The earlier handmade pixel version was unacceptable. It looked like a rough self-drawn blocky sprite, not like a polished Petdex pet.

The target quality is the Yachiyo reference:

- polished chibi sprite art
- high-detail anime mini character
- soft outline and clean shading
- clear animation states
- 9 rows of states, with real pose changes
- transparent final spritesheet

Do not go back to hand-drawn geometric pixel blobs.

## Petdex / Manifest Notes

Use this manifest style, not the old `frameWidth` object-style manifest:

```json
{
  "schema_version": "codexpet.v1",
  "name": "Mutsumi",
  "atlas": {
    "image": "spritesheet.webp",
    "frame_width": 192,
    "frame_height": 208,
    "columns": 8,
    "rows": 9
  },
  "states": [
    { "id": "idle", "row": 0, "frames": 6 },
    { "id": "run_right", "row": 1, "frames": 8 },
    { "id": "run_left", "row": 2, "frames": 8 },
    { "id": "wave", "row": 3, "frames": 4 },
    { "id": "jump", "row": 4, "frames": 5 },
    { "id": "fail", "row": 5, "frames": 8 },
    { "id": "wait", "row": 6, "frames": 6 },
    { "id": "run", "row": 7, "frames": 6 },
    { "id": "review", "row": 8, "frames": 6 }
  ]
}
```

## Current Problem

The latest imagegen source is much better aesthetically, but it only generated 7 frames per row. The post-processing script duplicates/remaps to 8 columns.

Remaining issues visible in `preview.png`:

- Some rows are acceptable, especially idle, wave, jump, fail, wait, run, review.
- Run rows are still only approximated from 7 source frames.
- The current result is better than the handmade pixel version, but still not at Yachiyo polish because:
  - frame consistency can improve
  - exact state motion can improve
  - Petdex Hatch Pet skill was not available in this session

## Script

Main builder:

```text
tools/build_mutsumi_pet.py
```

Current builder does:

- reads the generated atlas
- detects 9 x 7 sprite components by alpha/color distance
- crops each sprite by connected component bounding box
- removes magenta chroma background
- keeps largest connected component
- fits to 192 x 208
- outputs 1536 x 1872 `spritesheet.webp`
- writes/copies root and `mutsumi/` outputs

Run it with:

```powershell
python tools/build_mutsumi_pet.py
```

## Next Session Plan

1. User will teach/guide the desired look.
2. Prefer using the real Petdex Hatch Pet skill if it becomes available.
3. If not available, use imagegen again with stricter prompt:
   - one row at a time or smaller batches
   - exact 8 frames per row
   - Yachiyo-like polish
   - Mutsumi visual traits
   - no text, no shadows, flat chroma key
4. Assemble from individually better row images rather than one large all-state image if needed.
5. Keep current `codexpet.v1` manifest structure.
