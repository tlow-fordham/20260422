"""
Build slides from slides.yaml using U.S. Bank discussion template.

All three slides use a single layout: title (PH 0) + content (PH 10).
If the background is wrong, change LAYOUT below to 12 or 14.

Usage:
    python build_slides_template.py

Dependencies: pip install python-pptx pyyaml
"""

import yaml
import sys
from pptx import Presentation
from pptx.util import Pt
from pptx.oxml.ns import qn


TEMPLATE_PATH = "U_S_Bank_standard_discussion_temp_cleaned.pptx"
YAML_PATH = "slides.yaml"
OUTPUT_PATH = "20260423_Agentic_AI_Validation_Best_Practices.pptx"

# Try 13 first. If still blue, change to 14.
# Layout 12: PH 0 (title) + PH 1  (content)
# Layout 13: PH 0 (title) + PH 10 (content)
# Layout 14: PH 0 (title) + PH 10 (content)
LAYOUT = 13
CONTENT_PH = 10   # PH index for content. Use 1 if LAYOUT = 12.


def inspect_template(path):
    prs = Presentation(path)
    print(f"\nTemplate: {path}")
    print(f"Slide size: {prs.slide_width / 914400:.1f}\" x "
          f"{prs.slide_height / 914400:.1f}\"\n")
    for i, layout in enumerate(prs.slide_layouts):
        print(f"Layout {i}: \"{layout.name}\"")
        for ph in layout.placeholders:
            print(f"    Placeholder {ph.placeholder_format.idx}: "
                  f"\"{ph.name}\" ({ph.placeholder_format.type}) "
                  f"@ ({ph.left/914400:.1f}\", {ph.top/914400:.1f}\") "
                  f"w={ph.width/914400:.1f}\" h={ph.height/914400:.1f}\"")
        print()


def fill_placeholder(slide, ph_idx, paragraphs):
    """Fill a placeholder with structured paragraphs. Handles OBJECT type."""
    if ph_idx not in slide.placeholders:
        print(f"  Warning: placeholder {ph_idx} not found, skipping")
        return
    tf = slide.placeholders[ph_idx].text_frame
    if not paragraphs:
        return

    # Write first paragraph to activate
    first = paragraphs[0]
    p = tf.paragraphs[0]
    p.text = first.get("text", "")
    p.space_after = Pt(first.get("space_after", 2))
    if "size" in first:
        p.font.size = Pt(first["size"])
    if "bold" in first:
        p.font.bold = first["bold"]
    if "italic" in first:
        p.font.italic = first["italic"]

    # Remove extra default paragraphs
    p_elements = tf._txBody.findall(qn("a:p"))
    for extra in p_elements[1:]:
        tf._txBody.remove(extra)

    # Add rest
    for para in paragraphs[1:]:
        p = tf.add_paragraph()
        p.text = para.get("text", "")
        p.space_after = Pt(para.get("space_after", 2))
        if "size" in para:
            p.font.size = Pt(para["size"])
        if "bold" in para:
            p.font.bold = para["bold"]
        if "italic" in para:
            p.font.italic = para["italic"]


# ---------------------------------------------------------------------------
# Slide 1: Regulatory Foundation
# ---------------------------------------------------------------------------

def build_slide_1(prs, data):
    slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT])
    slide.placeholders[0].text = data["title"]

    body = []
    body.append({"text": data["subtitle"], "italic": True, "size": 11,
                 "space_after": 8})

    for q in data["quotes"]:
        body.append({"text": q["label"], "bold": True, "size": 10,
                     "space_after": 0})
        body.append({"text": q["text"], "size": 10, "space_after": 0})
        body.append({"text": q["source"], "italic": True, "size": 9,
                     "space_after": 6})

    if data.get("footer"):
        body.append({"text": "", "size": 6, "space_after": 4})
        body.append({"text": data["footer"], "italic": True, "size": 9})

    fill_placeholder(slide, CONTENT_PH, body)


# ---------------------------------------------------------------------------
# Slide 2: Proposed Template Changes
# ---------------------------------------------------------------------------

def build_slide_2(prs, data):
    slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT])
    slide.placeholders[0].text = data["title"]

    body = []
    body.append({"text": data["subtitle"], "italic": True, "size": 11,
                 "space_after": 8})

    for card in data["cards"]:
        body.append({"text": card["heading"], "bold": True, "size": 10,
                     "space_after": 0})
        body.append({"text": card["section"], "italic": True, "size": 8,
                     "space_after": 0})
        body.append({"text": card["body"], "size": 9, "space_after": 6})

    if data.get("callout"):
        body.append({"text": "", "size": 6, "space_after": 2})
        body.append({"text": "Core Principle", "bold": True, "size": 10,
                     "space_after": 0})
        body.append({"text": data["callout"], "italic": True, "size": 9})

    fill_placeholder(slide, CONTENT_PH, body)


# ---------------------------------------------------------------------------
# Slide 3: Best Practices (single column — left then right sequentially)
# ---------------------------------------------------------------------------

def build_slide_3(prs, data):
    slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT])
    slide.placeholders[0].text = data["title"]

    body = []
    body.append({"text": data["subtitle"], "italic": True, "size": 11,
                 "space_after": 6})

    # Left column content
    body.append({"text": data["left_header"], "bold": True, "size": 10,
                 "space_after": 2})
    for sec in data["left_sections"]:
        body.append({"text": sec["heading"], "bold": True, "size": 9,
                     "space_after": 0})
        for bullet in sec["bullets"]:
            body.append({"text": f"- {bullet}", "size": 8, "space_after": 1})
        body.append({"text": "", "size": 4, "space_after": 2})

    # Right column content
    body.append({"text": data["right_header"], "bold": True, "size": 10,
                 "space_after": 2})
    for sec in data["right_sections"]:
        body.append({"text": sec["heading"], "bold": True, "size": 9,
                     "space_after": 0})
        body.append({"text": sec["body"], "size": 8, "space_after": 4})

    if data.get("footer"):
        body.append({"text": "", "size": 4, "space_after": 2})
        body.append({"text": data["footer"], "italic": True, "size": 8})

    fill_placeholder(slide, CONTENT_PH, body)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if "--inspect" in sys.argv:
        inspect_template(TEMPLATE_PATH)
        return

    with open(YAML_PATH, "r") as f:
        content = yaml.safe_load(f)

    prs = Presentation(TEMPLATE_PATH)

    builders = {
        "title": build_slide_1,
        "cards": build_slide_2,
        "two_column": build_slide_3,
    }

    for slide_data in content["slides"]:
        layout_key = slide_data["layout"]
        builder = builders.get(layout_key)
        if builder:
            builder(prs, slide_data)
        else:
            print(f"Warning: unknown layout '{layout_key}', skipping.")

    prs.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")
    print(f"\nIf background is blue, edit LAYOUT to 14 (or 12 with CONTENT_PH = 1)")


if __name__ == "__main__":
    main()
