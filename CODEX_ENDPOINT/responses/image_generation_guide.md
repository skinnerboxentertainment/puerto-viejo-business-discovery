# Image Generation Guide

This workspace can generate the image in two practical ways:

1. **Codex built-in image generation tool**: available in this session, no `OPENAI_API_KEY` required. Best for asking Codex to generate a one-off preview or project asset.
2. **OpenAI API from Python**: repeatable from Windows/PowerShell, but requires an OpenAI Platform API key and the `openai` Python package.

Current local findings:

- Python is installed: `Python 3.13.5`
- Pillow is installed: `pillow 11.3.0`
- OpenAI Python SDK is **not** installed yet.
- `OPENAI_API_KEY` is **not** set in Process, User, or Machine environment variables.
- The `openai` CLI is not currently available because the SDK is not installed.

Official docs checked:

- Image generation guide: https://platform.openai.com/docs/guides/image-generation
- Images API reference: https://platform.openai.com/docs/api-reference/images/create

## Recommended Approach

Use the **OpenAI API from Python** for a repeatable workflow, and use the **Codex built-in image generation tool** when you want Codex itself to generate a quick image from the prompt.

For API generation, use the current GPT image model path first:

- Recommended model: `gpt-image-2`
- Portrait size for this prompt: `1024x1536`
- Output: PNG written locally

The older `dall-e-3` model is still listed in the Images API model enum, but the current OpenAI image generation guide shows `gpt-image-2` as the primary example model. Use `dall-e-3` only as a fallback if your account does not have access to the GPT image models.

## Option 1: Ask Codex To Generate It

Codex has a built-in `image_gen` channel available in this session. It does **not** use your local `OPENAI_API_KEY`.

Use this when you want the assistant to generate the image directly:

```text
Generate an image using the prompt in:
C:\Users\oscar\OneDrive\Documents\Zenescope Pin Up Art\openCodeEndpoint\CODEX_ENDPOINT\responses\reconciled_composition.md

Save the final image into:
C:\Users\oscar\OneDrive\Documents\Zenescope Pin Up Art\openCodeEndpoint\CODEX_ENDPOINT\responses\dark_fairy_tale_glamour.png
```

Notes:

- Codex can read the prompt file, generate the image, then copy the result into the workspace.
- This is convenient, but less repeatable than a script because the built-in image tool is exposed through the assistant session rather than your shell.
- If exact text inside the image matters, expect possible retries. Image models can still misspell speech bubbles and title text.

## Option 2: Python Script Using OpenAI API

### 1. Install the OpenAI SDK

From PowerShell:

```powershell
py -m pip install --upgrade openai
```

Optional, but useful:

```powershell
py -m pip install --upgrade pillow
```

### 2. Create An OpenAI API Key

Create an API key here:

```text
https://platform.openai.com/api-keys
```

Do not paste the key into chat or commit it to a file.

### 3. Set The API Key On Windows

For the current PowerShell session only:

```powershell
$env:OPENAI_API_KEY = "sk-your-key-here"
```

For your Windows user account permanently:

```powershell
setx OPENAI_API_KEY "sk-your-key-here"
```

After `setx`, open a new PowerShell window before running the script.

Verify without printing the secret:

```powershell
if ($env:OPENAI_API_KEY) { "OPENAI_API_KEY is set" } else { "OPENAI_API_KEY is missing" }
```

### 4. Save This Script

Create this file:

```text
C:\Users\oscar\OneDrive\Documents\Zenescope Pin Up Art\openCodeEndpoint\CODEX_ENDPOINT\generate_image.py
```

Script:

```python
from pathlib import Path
import argparse
import base64

from openai import OpenAI


def extract_final_prompt(markdown: str) -> str:
    marker = "## 7. Final Unified Prompt"
    negative_marker = "## 8. Negative Prompt"

    if marker in markdown:
        section = markdown.split(marker, 1)[1]
        if negative_marker in section:
            section = section.split(negative_marker, 1)[0]
        prompt = section.strip()
    else:
        prompt = markdown.strip()

    if negative_marker in markdown:
        negative = markdown.split(negative_marker, 1)[1].strip()
        prompt += "\n\nAvoid:\n" + negative

    return prompt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prompt-file",
        default=r"C:\Users\oscar\OneDrive\Documents\Zenescope Pin Up Art\openCodeEndpoint\CODEX_ENDPOINT\responses\reconciled_composition.md",
    )
    parser.add_argument(
        "--out",
        default=r"C:\Users\oscar\OneDrive\Documents\Zenescope Pin Up Art\openCodeEndpoint\CODEX_ENDPOINT\responses\dark_fairy_tale_glamour.png",
    )
    parser.add_argument("--model", default="gpt-image-2")
    parser.add_argument("--size", default="1024x1536")
    parser.add_argument("--quality", default="high")
    args = parser.parse_args()

    prompt_path = Path(args.prompt_file)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    markdown = prompt_path.read_text(encoding="utf-8")
    prompt = extract_final_prompt(markdown)

    client = OpenAI()

    result = client.images.generate(
        model=args.model,
        prompt=prompt,
        size=args.size,
        quality=args.quality,
    )

    image_base64 = result.data[0].b64_json
    out_path.write_bytes(base64.b64decode(image_base64))

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
```

### 5. Run It

From the workspace:

```powershell
cd "C:\Users\oscar\OneDrive\Documents\Zenescope Pin Up Art\openCodeEndpoint\CODEX_ENDPOINT"
py .\generate_image.py
```

Output file:

```text
C:\Users\oscar\OneDrive\Documents\Zenescope Pin Up Art\openCodeEndpoint\CODEX_ENDPOINT\responses\dark_fairy_tale_glamour.png
```

### 6. Run A Draft First

For a faster/cheaper draft:

```powershell
py .\generate_image.py --quality low --out ".\responses\dark_fairy_tale_glamour_draft.png"
```

For the final:

```powershell
py .\generate_image.py --quality high --out ".\responses\dark_fairy_tale_glamour_final.png"
```

## DALL-E 3 Fallback

If `gpt-image-2` is unavailable for your API key, try `dall-e-3`.

Run:

```powershell
py .\generate_image.py --model dall-e-3 --size 1024x1792 --out ".\responses\dark_fairy_tale_glamour_dalle3.png"
```

If the SDK rejects `quality=high` for `dall-e-3`, change the script call to omit `quality`, or edit the script so the `quality=args.quality` line is only used for GPT image models.

Important differences:

- GPT image models return base64 image data by default.
- `dall-e-3` may return a temporary image URL by default unless `response_format` is set to `b64_json`.
- The script above is optimized for GPT image models.

## Option 3: OpenAI CLI

After installing the Python SDK, an `openai` CLI may become available.

Check:

```powershell
where.exe openai
openai --help
```

The current OpenAI docs show this general pattern:

```powershell
openai images generate --model gpt-image-2 --prompt "your prompt here"
```

For this project, the Python script is better because the prompt is long and already lives in a Markdown file.

## Troubleshooting

If you get `ModuleNotFoundError: No module named 'openai'`:

```powershell
py -m pip install --upgrade openai
```

If you get an authentication error:

```powershell
if ($env:OPENAI_API_KEY) { "OPENAI_API_KEY is set" } else { "OPENAI_API_KEY is missing" }
```

If the generated image has garbled title or speech-bubble text:

- Generate the illustration without text.
- Add the title and speech bubbles afterward in Photoshop, Krita, GIMP, Canva, or a small Python/Pillow overlay script.
- This is usually more reliable for exact typography.

If the model refuses or weakens the prompt:

- Keep the character clearly adult.
- Avoid explicit nudity or sexual framing.
- Keep the prompt in dark fantasy comic-cover territory rather than erotic content.

## Exact Prompt File Used

Input prompt:

```text
C:\Users\oscar\OneDrive\Documents\Zenescope Pin Up Art\openCodeEndpoint\CODEX_ENDPOINT\responses\reconciled_composition.md
```

The script extracts:

- `## 7. Final Unified Prompt`
- appends `## 8. Negative Prompt` as an `Avoid:` section

That means you can keep editing `reconciled_composition.md` and rerun:

```powershell
py .\generate_image.py
```
