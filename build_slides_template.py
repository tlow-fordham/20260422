"""
Build slides from slides.yaml using a U.S. Bank template.

Usage:
    1. Place your template as usbank_template.pptx in the same directory
    2. Run: python build_slides_template.py
    3. Open the output and verify layout/font inheritance

Before first run:
    Run this to inspect your template's available layouts and placeholders:
        python build_slides_template.py --inspect

Dependencies:
    pip install python-pptx pyyaml
"""

import yaml
import sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR


TEMPLATE_PATH = "usbank_template.pptx"
YAML_PATH = "slides.yaml"
OUTPUT_PATH = "20260423_Agentic_AI_Validation_Best_Practices.pptx"


# -----------------------------------------------------------------------------
# Inspect mode: run with --inspect to see what layouts and placeholders exist
# -----------------------------------------------------------------------------

def inspect_template(path):
    """Print all layouts and their placeholders so you can pick the right indices."""
    prs = Presentation(path)
    print(f"\nTemplate: {path}")
    print(f"Slide size: {prs.slide_width / 914400:.1f}\" x {prs.slide_height / 914400:.1f}\"\n")
    for i, layout in enumerate(prs.slide_layouts):
        print(f"Layout {i}: \"{layout.name}\"")
        for ph in layout.placeholders:
            print(f"    Placeholder {ph.placeholder_format.idx}: "
                  f"\"{ph.name}\" ({ph.placeholder_format.type}) "
                  f"@ ({ph.left/914400:.1f}\", {ph.top/914400:.1f}\") "
                  f"w={ph.width/914400:.1f}\" h={ph.height/914400:.1f}\"")
        print()


# -----------------------------------------------------------------------------
# Helpers — all use template fonts/colors, no hardcoded styles
# -----------------------------------------------------------------------------

def set_text(placeholder, text):
    """Set text on a placeholder, inheriting the template's formatting."""
    placeholder.text = text


def add_textbox(slide, left, top, width, height, text,
                font_size=None, bold=None, italic=None,
                alignment=PP_ALIGN.LEFT):
    """
    Add a text box. Only set formatting properties that are explicitly passed.
    Everything else inherits from the template/theme.
    """
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = alignment
    if font_size is not None:
        p.font.size = Pt(font_size)
    if bold is not None:
        p.font.bold = bold
    if italic is not None:
        p.font.italic = italic
    return txBox


def add_multiline(slide, left, top, width, height, lines,
                  font_size=None, bold=None):
    """Add a text box with multiple paragraphs."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)

    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.space_after = Pt(4)
        if font_size is not None:
            p.font.size = Pt(font_size)
        if bold is not None:
            p.font.bold = bold
    return txBox


# -----------------------------------------------------------------------------
# Configuration — UPDATE THESE after running --inspect on your template
# -----------------------------------------------------------------------------

# Layout indices — map to your template's layouts
LAYOUT_TITLE = 0         # Typically "Title Slide"
LAYOUT_CONTENT = 1       # Typically "Title and Content" or similar
LAYOUT_BLANK = 6         # Typically "Blank"

# Placeholder indices — map to your template's placeholders
PH_TITLE = 0             # Title placeholder index
PH_SUBTITLE = 1          # Subtitle placeholder index
PH_BODY = 1              # Body/content placeholder index (often same as subtitle)


# -----------------------------------------------------------------------------
# Slide builders
# -----------------------------------------------------------------------------

def build_slide_1(prs, data):
    """Regulatory Foundation — title + subtitle via placeholders, quotes as textboxes."""
    layout = prs.slide_layouts[LAYOUT_CONTENT]
    slide = prs.slides.add_slide(layout)

    # Use placeholders for title and subtitle
    if PH_TITLE in slide.placeholders:
        set_text(slide.placeholders[PH_TITLE], data["title"])

    # Build quote content as body text
    body_lines = []
    for q in data["quotes"]:
        body_lines.append(f"[{q['label']}]")
        body_lines.append(q["text"])
        body_lines.append(f"— {q['source']}")
        body_lines.append("")  # blank line separator

    if data.get("footer"):
        body_lines.append(data["footer"])

    if PH_BODY in slide.placeholders:
        tf = slide.placeholders[PH_BODY].text_frame
        tf.clear()
        for i, line in enumerate(body_lines):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = line
            p.space_after = Pt(2)

            # Make labels and sources slightly smaller
            if line.startswith("[") and line.endswith("]"):
                p.font.bold = True
                p.font.size = Pt(10)
            elif line.startswith("—"):
                p.font.italic = True
                p.font.size = Pt(9)
            else:
                p.font.size = Pt(11)


def build_slide_2(prs, data):
    """Proposed Template Changes — title via placeholder, cards as textboxes."""
    layout = prs.slide_layouts[LAYOUT_CONTENT]
    slide = prs.slides.add_slide(layout)

    # Title
    if PH_TITLE in slide.placeholders:
        set_text(slide.placeholders[PH_TITLE], data["title"])

    # Build all cards as body text
    body_lines = []
    for card in data["cards"]:
        body_lines.append(card["heading"])
        body_lines.append(f"({card['section']})")
        body_lines.append(card["body"])
        body_lines.append("")

    if data.get("callout"):
        body_lines.append("Core Principle:")
        body_lines.append(data["callout"])

    if PH_BODY in slide.placeholders:
        tf = slide.placeholders[PH_BODY].text_frame
        tf.clear()
        for i, line in enumerate(body_lines):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = line
            p.space_after = Pt(2)

            # Headings bold, section refs small, body normal
            if line in [c["heading"] for c in data["cards"]] or line == "Core Principle:":
                p.font.bold = True
                p.font.size = Pt(11)
            elif line.startswith("(Section"):
                p.font.italic = True
                p.font.size = Pt(9)
            else:
                p.font.size = Pt(10)


def build_slide_3(prs, data):
    """Best Practices — title via placeholder, two-column content as body text."""
    layout = prs.slide_layouts[LAYOUT_CONTENT]
    slide = prs.slides.add_slide(layout)

    # Title
    if PH_TITLE in slide.placeholders:
        set_text(slide.placeholders[PH_TITLE], data["title"])

    # Combine left and right columns into sequential body text
    body_lines = []

    # Left column
    body_lines.append(data["left_header"])
    body_lines.append("")
    for sec in data["left_sections"]:
        body_lines.append(sec["heading"])
        for bullet in sec["bullets"]:
            body_lines.append(f"  - {bullet}")
        body_lines.append("")

    # Right column
    body_lines.append(data["right_header"])
    body_lines.append("")
    for sec in data["right_sections"]:
        body_lines.append(sec["heading"])
        body_lines.append(f"  {sec['body']}")
        body_lines.append("")

    if PH_BODY in slide.placeholders:
        tf = slide.placeholders[PH_BODY].text_frame
        tf.clear()
        for i, line in enumerate(body_lines):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = line
            p.space_after = Pt(1)

            # Section headers bold, bullets normal, column headers bold+larger
            if line in [data["left_header"], data["right_header"]]:
                p.font.bold = True
                p.font.size = Pt(11)
            elif line in [s["heading"] for s in data["left_sections"]] + \
                         [s["heading"] for s in data["right_sections"]]:
                p.font.bold = True
                p.font.size = Pt(10)
            elif line.startswith("  - "):
                p.font.size = Pt(9)
            elif line.startswith("  "):
                p.font.size = Pt(9)
            else:
                p.font.size = Pt(10)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

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
        layout = slide_data["layout"]
        builder = builders.get(layout)
        if builder:
            builder(prs, slide_data)
        else:
            print(f"Warning: unknown layout '{layout}', skipping.")

    prs.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")
    print(f"\nNext steps:")
    print(f"  1. Open {OUTPUT_PATH} in PowerPoint")
    print(f"  2. Check that fonts and colors match your template theme")
    print(f"  3. If placeholders are wrong, run: python {sys.argv[0]} --inspect")
    print(f"     and update LAYOUT_*/PH_* constants at the top of the script")


if __name__ == "__main__":
    main()
