"""
Build slides from slides.yaml using U.S. Bank discussion template.

Usage: python build_slides_template.py
Debug: python build_slides_template.py --debug  (prints available placeholders)
Inspect: python build_slides_template.py --inspect

Dependencies: pip install python-pptx pyyaml
"""

import yaml
import sys
from pptx import Presentation
from pptx.util import Pt


TEMPLATE_PATH = "U_S_Bank_standard_discussion_temp_cleaned.pptx"
YAML_PATH = "slides.yaml"
OUTPUT_PATH = "20260423_Agentic_AI_Validation_Best_Practices.pptx"

# Layout 12: "Title and content 1"
#   PH 0 = Title (TITLE type 1)
#   PH 1 = Content (OBJECT type 7)
LAYOUT = 12

DEBUG = "--debug" in sys.argv


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


def debug_slide(slide, label):
    """Print what placeholders actually exist on a created slide."""
    if not DEBUG:
        return
    print(f"\n  [{label}] Available placeholders on slide:")
    for ph in slide.placeholders:
        print(f"    PH {ph.placeholder_format.idx}: "
              f"\"{ph.name}\" type={ph.placeholder_format.type}")
    print()


def fill_content(slide, paragraphs):
    """
    Find the content placeholder (not the title) and fill it.
    Instead of looking up by index, find the first non-title placeholder.
    """
    if not paragraphs:
        return

    # Find content placeholder: any placeholder that is not the title (idx 0)
    content_ph = None
    for ph in slide.placeholders:
        if ph.placeholder_format.idx != 0:
            content_ph = ph
            break

    if content_ph is None:
        print("  ERROR: No content placeholder found on slide!")
        return

    if DEBUG:
        print(f"  Using placeholder {content_ph.placeholder_format.idx}: "
              f"\"{content_ph.name}\"")

    # Activate by setting .text
    content_ph.text = paragraphs[0].get("text", "")

    # Format first paragraph
    tf = content_ph.text_frame
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

    # Add remaining paragraphs
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
    slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT])
    debug_slide(slide, "Slide 1")
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

    fill_content(slide, body)


def build_slide_2(prs, data):
    slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT])
    debug_slide(slide, "Slide 2")
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

    fill_content(slide, body)


def build_slide_3(prs, data):
    slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT])
    debug_slide(slide, "Slide 3")
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

    fill_content(slide, body)


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
    print(f"\nRun with --debug to see which placeholders exist on each slide")


if __name__ == "__main__":
    main()
