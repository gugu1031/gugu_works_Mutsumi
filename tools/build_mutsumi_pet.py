from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
PET_DIR = ROOT / "mutsumi"
SOURCE_ATLAS = Path(
    r"C:\Users\gujia\.codex\generated_images\019e4b29-42f1-7f22-b6e1-07273da2be12\ig_03a80af926a0745a016a14717a7b708191a8fd09ec4ee0d8b0.png"
)

FRAME_W = 192
FRAME_H = 208
OUT_COLS = 8
OUT_ROWS = 9
SRC_COLS = 7
SRC_ROWS = 9


STATES = [
    {
        "id": "idle",
        "label": "Idle",
        "row": 0,
        "frames": 6,
        "description": "Neutral breathing and blink loop.",
    },
    {
        "id": "run_right",
        "label": "Run Right",
        "row": 1,
        "frames": 8,
        "description": "Directional movement to the right.",
    },
    {
        "id": "run_left",
        "label": "Run Left",
        "row": 2,
        "frames": 8,
        "description": "Directional movement to the left.",
    },
    {
        "id": "wave",
        "label": "Wave",
        "row": 3,
        "frames": 4,
        "description": "A reserved greeting or attention gesture.",
    },
    {
        "id": "jump",
        "label": "Jump",
        "row": 4,
        "frames": 5,
        "description": "Prep, lift, apex, drop, and landing.",
    },
    {
        "id": "fail",
        "label": "Fail",
        "row": 5,
        "frames": 8,
        "description": "Readable error or sad reaction.",
    },
    {
        "id": "wait",
        "label": "Wait",
        "row": 6,
        "frames": 6,
        "description": "Patient waiting loop with guitar.",
    },
    {
        "id": "run",
        "label": "Run",
        "row": 7,
        "frames": 6,
        "description": "Generic energetic running loop.",
    },
    {
        "id": "review",
        "label": "Review",
        "row": 8,
        "frames": 6,
        "description": "Focused code review or thinking loop.",
    },
]


def write_manifest() -> dict:
    manifest = {
        "schema_version": "codexpet.v1",
        "name": "Mutsumi",
        "description": "A quiet green-haired guitarist Codex pet inspired by Mutsumi Wakaba, with sleepy golden eyes, mint hair, a navy sailor uniform, and a pink guitar.",
        "author": "gujia",
        "atlas": {
            "image": "spritesheet.webp",
            "frame_width": FRAME_W,
            "frame_height": FRAME_H,
            "columns": OUT_COLS,
            "rows": OUT_ROWS,
        },
        "states": STATES,
    }
    for path in (PET_DIR / "pet.json", ROOT / "pet.json"):
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def chroma_key(img: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
    pix = rgba.load()
    w, h = rgba.size
    corners = [
        rgba.getpixel((0, 0)),
        rgba.getpixel((w - 1, 0)),
        rgba.getpixel((0, h - 1)),
        rgba.getpixel((w - 1, h - 1)),
    ]
    key = max(corners, key=lambda p: p[0] + p[2] - p[1])
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            dist = abs(r - key[0]) + abs(g - key[1]) + abs(b - key[2])
            if dist < 70:
                pix[x, y] = (r, g, b, 0)
            elif dist < 145:
                pix[x, y] = (r, g, b, int(a * (dist - 70) / 75))
    return rgba


def trim(img: Image.Image) -> Image.Image:
    bbox = img.getchannel("A").getbbox()
    if not bbox:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    return img.crop(bbox)


def keep_largest_component(img: Image.Image) -> Image.Image:
    arr = np.array(img)
    mask = arr[:, :, 3] > 12
    h, w = mask.shape
    seen = np.zeros((h, w), dtype=bool)
    best: list[tuple[int, int]] = []

    for y in range(h):
        for x in range(w):
            if not mask[y, x] or seen[y, x]:
                continue
            stack = [(x, y)]
            seen[y, x] = True
            comp: list[tuple[int, int]] = []
            while stack:
                cx, cy = stack.pop()
                comp.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((nx, ny))
            if len(comp) > len(best):
                best = comp

    if not best:
        return img

    keep = np.zeros((h, w), dtype=bool)
    for x, y in best:
        keep[y, x] = True
    arr[:, :, 3] = np.where(keep, arr[:, :, 3], 0)
    return Image.fromarray(arr, "RGBA")


def detect_sprite_boxes(source: Image.Image) -> list[list[tuple[int, int, int, int]]]:
    arr = np.array(source.convert("RGB"))
    key = arr[0, 0, :3].astype(int)
    mask = np.abs(arr.astype(int) - key).sum(axis=2) > 80
    h, w = mask.shape
    seen = np.zeros((h, w), dtype=bool)
    comps: list[tuple[int, int, int, int, int, int, int]] = []

    for y in range(h):
        for x in range(w):
            if not mask[y, x] or seen[y, x]:
                continue
            stack = [(x, y)]
            seen[y, x] = True
            xs: list[int] = []
            ys: list[int] = []
            while stack:
                cx, cy = stack.pop()
                xs.append(cx)
                ys.append(cy)
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((nx, ny))
            area = len(xs)
            if area > 5000:
                x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
                comps.append((area, x1, y1, x2, y2, (x1 + x2) // 2, (y1 + y2) // 2))

    comps.sort(key=lambda c: c[6])
    rows: list[list[tuple[int, int, int, int, int, int, int]]] = []
    for comp in comps:
        if rows and abs(comp[6] - rows[-1][0][6]) < 45:
            rows[-1].append(comp)
        else:
            rows.append([comp])

    if len(rows) != SRC_ROWS or any(len(row) != SRC_COLS for row in rows):
        raise ValueError(f"expected {SRC_ROWS}x{SRC_COLS} components, got {[len(row) for row in rows]}")

    sprite_rows: list[list[tuple[int, int, int, int]]] = []
    for row in rows:
        row.sort(key=lambda c: c[5])
        sprite_rows.append([(c[1], c[2], c[3], c[4]) for c in row])
    return sprite_rows


def fit_to_frame(img: Image.Image, state_id: str) -> Image.Image:
    cutout = trim(keep_largest_component(chroma_key(img)))
    frame = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    max_w = 184
    max_h = 198
    if state_id in {"run_right", "run_left", "fail"}:
        max_w = 188
        max_h = 202
    scale = min(max_w / cutout.width, max_h / cutout.height)
    sprite = cutout.resize(
        (max(1, int(cutout.width * scale)), max(1, int(cutout.height * scale))),
        Image.Resampling.LANCZOS,
    )
    x = (FRAME_W - sprite.width) // 2
    y = FRAME_H - sprite.height - 6
    if state_id in {"jump"}:
        y = max(3, (FRAME_H - sprite.height) // 2)
    frame.alpha_composite(sprite, (x, y))
    return frame


def frame_source_index(state_id: str, out_col: int) -> int:
    if state_id in {"idle", "wait", "run", "review"}:
        return [0, 1, 2, 3, 4, 5, 4, 3][out_col]
    if state_id == "wave":
        return [0, 1, 2, 3, 2, 1, 0, 1][out_col]
    if state_id == "jump":
        return [0, 1, 2, 3, 4, 3, 1, 0][out_col]
    return [0, 1, 2, 3, 4, 5, 6, 5][out_col]


def build_sheet(source: Path, manifest: dict) -> Image.Image:
    src = Image.open(source).convert("RGB")
    sprite_boxes = detect_sprite_boxes(src)
    sheet = Image.new("RGBA", (FRAME_W * OUT_COLS, FRAME_H * OUT_ROWS), (0, 0, 0, 0))

    for state in manifest["states"]:
        row = state["row"]
        for out_col in range(OUT_COLS):
            src_col = frame_source_index(state["id"], out_col)
            x1, y1, x2, y2 = sprite_boxes[row][src_col]
            margin = 8
            if state["id"] in {"run_right", "run_left", "run", "wait"}:
                margin = 12
            box = (x1 - margin, y1 - margin, x2 + margin, y2 + margin)
            box = (
                max(0, box[0]),
                max(0, box[1]),
                min(src.width, box[2]),
                min(src.height, box[3]),
            )
            source_cell = src.crop(box)
            frame = fit_to_frame(source_cell, state["id"])
            sheet.alpha_composite(frame, (out_col * FRAME_W, row * FRAME_H))

    return sheet


def make_preview(sheet: Image.Image) -> Image.Image:
    bg = Image.new("RGBA", sheet.size, (40, 45, 52, 255))
    draw = ImageDraw.Draw(bg)
    block = 24
    for y in range(0, sheet.height, block):
        for x in range(0, sheet.width, block):
            color = (55, 62, 70, 255) if (x // block + y // block) % 2 else (47, 53, 61, 255)
            draw.rectangle((x, y, min(x + block, sheet.width), min(y + block, sheet.height)), fill=color)
    bg.alpha_composite(sheet)
    return bg.convert("RGB")


def export_gifs(sheet: Image.Image, manifest: dict) -> None:
    for state in manifest["states"]:
        frames = []
        for col in range(state["frames"]):
            frame = sheet.crop((col * FRAME_W, state["row"] * FRAME_H, (col + 1) * FRAME_W, (state["row"] + 1) * FRAME_H))
            bg = Image.new("RGBA", (FRAME_W, FRAME_H), (30, 34, 39, 255))
            bg.alpha_composite(frame)
            frames.append(bg.convert("P", palette=Image.Palette.ADAPTIVE))
        frames[0].save(
            PET_DIR / f"preview-{state['id']}.gif",
            save_all=True,
            append_images=frames[1:],
            duration=120,
            loop=0,
            disposal=2,
        )


def validate(sheet: Image.Image, manifest: dict) -> None:
    assert sheet.size == (1536, 1872), sheet.size
    assert sheet.mode == "RGBA"
    assert manifest["schema_version"] == "codexpet.v1"
    assert manifest["atlas"]["frame_width"] == FRAME_W
    assert manifest["atlas"]["frame_height"] == FRAME_H
    assert manifest["atlas"]["columns"] == OUT_COLS
    assert manifest["atlas"]["rows"] == OUT_ROWS
    assert [state["row"] for state in manifest["states"]] == list(range(OUT_ROWS))


def copy_outputs() -> None:
    for name in ["spritesheet.webp", "spritesheet.png", "preview.png", "README.md"]:
        shutil.copy2(PET_DIR / name, ROOT / name)
    for gif in PET_DIR.glob("preview-*.gif"):
        shutil.copy2(gif, ROOT / gif.name)


def main() -> int:
    if not SOURCE_ATLAS.exists():
        raise FileNotFoundError(SOURCE_ATLAS)
    PET_DIR.mkdir(exist_ok=True)
    shutil.copy2(SOURCE_ATLAS, PET_DIR / "source-imagegen-atlas.png")

    manifest = write_manifest()
    sheet = build_sheet(SOURCE_ATLAS, manifest)
    validate(sheet, manifest)

    sheet.save(PET_DIR / "spritesheet.webp", "WEBP", lossless=True, quality=100, method=6)
    sheet.save(PET_DIR / "spritesheet.png", "PNG")
    make_preview(sheet).save(PET_DIR / "preview.png")
    export_gifs(sheet, manifest)
    copy_outputs()

    print(f"wrote {PET_DIR / 'spritesheet.webp'}")
    print(f"size {sheet.width}x{sheet.height}, mode {sheet.mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
