"""
Build slides from slides.yaml using U.S. Bank discussion template.

Uses Layout 13 ("Title and content 2") — white background.
Forces OBJECT placeholder (PH 10) into the slide XML since python-pptx
does not automatically materialize it.

Usage: python build_slides_template.py
Inspect: python build_slides_template.py --inspect
Dependencies: pip install python-pptx pyyaml
"""

import yaml
import sys
import copy
from pptx import Presentation
from pptx.util import Pt
from pptx.oxml.ns import qn


TEMPLATE_PATH = "U_S_Bank_standard_discussion_temp_cleaned.pptx"
YAML_PATH = "slides.yaml"
OUTPUT_PATH = "20260423_Agentic_AI_Validation_Best_Practices.pptx"

LAYOUT = 13


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


def ensure_placeholder(slide, layout, ph_idx):
    """
    If a placeholder exists in the layout but not on the slide,
    copy its XML element from the layout's spTree into the slide's spTree.
    This forces OBJECT placeholders to materialize.
    """
    # Check if already on slide
    if ph_idx in slide.placeholders:
        return slide.placeholders[ph_idx]

    # Find it in the layout XML
    layout_spTree = layout.element.find(qn("p:cSld")).find(qn("p:spTree"))
    for sp in layout_spTree.iter(qn("p:sp")):
        nvSpPr = sp.find(qn("p:nvSpPr"))
        if nvSpPr is None:
            continue
        nvPr = nvSpPr.find(qn("p:nvPr"))
        if nvPr is None:
            continue
        phElem = nvPr.find(qn("p:ph"))
        if phElem is not None:
            idx = phElem.get("idx")
            if idx is not None and int(idx) == ph_idx:
                # Found it in layout — copy into slide
                slide_spTree = slide.element.find(qn("p:cSld")).find(qn("p:spTree"))
                new_sp = copy.deepcopy(sp)
                slide_spTree.append(new_sp)
                # Re-read placeholders
                if ph_idx in slide.placeholders:
                    return slide.placeholders[ph_idx]
                else:
                    print(f"  Warning: copied PH {ph_idx} XML but still not found")
                    return None

    print(f"  Warning: PH {ph_idx} not found in layout XML either")
    return None


def fill_content(slide, layout, ph_idx, paragraphs):
    """Fill a placeholder, forcing it into existence if needed."""
    if not paragraphs:
        return

    ph = ensure_placeholder(slide, layout, ph_idx)
    if ph is None:
        return

    # Activate by setting .text
    ph.text = paragraphs[0].get("text", "")

    # Format first paragraph
    tf = ph.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    first = paragraphs[0]
    p.space_after = Pt(first.get("space_after", 2))
    if "size" in first:
        p.font.size = Pt(first["size"])
    if "bold" in first:
        p.font.bold = first["bold"]
    if "italic" in first:
        p.font.italic = first["italic"]

    # Add remaining
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


def build_slide_1(prs, data):
    layout = prs.slide_layouts[LAYOUT]
    slide = prs.slides.add_slide(layout)
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

    fill_content(slide, layout, 10, body)


def build_slide_2(prs, data):
    layout = prs.slide_layouts[LAYOUT]
    slide = prs.slides.add_slide(layout)
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

    fill_content(slide, layout, 10, body)


def build_slide_3(prs, data):
    layout = prs.slide_layouts[LAYOUT]
    slide = prs.slides.add_slide(layout)
    slide.placeholders[0].text = data["title"]

    body = []
    body.append({"text": data["subtitle"], "italic": True, "size": 11,
                 "space_after": 6})
    body.append({"text": data["left_header"], "bold": True, "size": 10,
                 "space_after": 2})
    for sec in data["left_sections"]:
        body.append({"text": sec["heading"], "bold": True, "size": 9,
                     "space_after": 0})
        for bullet in sec["bullets"]:
            body.append({"text": f"- {bullet}", "size": 8,
                         "space_after": 1})
        body.append({"text": "", "size": 4, "space_after": 2})
    body.append({"text": data["right_header"], "bold": True, "size": 10,
                 "space_after": 2})
    for sec in data["right_sections"]:
        body.append({"text": sec["heading"], "bold": True, "size": 9,
                     "space_after": 0})
        body.append({"text": sec["body"], "size": 8, "space_after": 4})
    if data.get("footer"):
        body.append({"text": "", "size": 4, "space_after": 2})
        body.append({"text": data["footer"], "italic": True, "size": 8})

    fill_content(slide, layout, 10, body)


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


if __name__ == "__main__":
    main()
