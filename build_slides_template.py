"""
Build slides from slides.yaml using U.S. Bank template.

Layout mapping:
  - "title"      -> Layout 13 (Title and content 2): PH0=title, textbox for subtitle
  - "single"     -> Layout 13 (Title and content 2): PH0=title, textbox for body
  - "two_column" -> Layout 21 (Title two subtitle and two content 1):
                     PH0=title, PH10=left subtitle, PH1=left content,
                     PH11=right subtitle, PH2=right content

Usage:
  python build_slides.py [template.pptx] [slides.yaml] [output.pptx]
"""

import sys
import yaml
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

TEMPLATE_PATH = sys.argv[1] if len(sys.argv) > 1 else "U_S_Bank_standard_discussion_temp_cleaned.pptx"
YAML_PATH = sys.argv[2] if len(sys.argv) > 2 else "slides.yaml"
OUTPUT_PATH = sys.argv[3] if len(sys.argv) > 3 else "20260424_Agentic_AI_Validation_Best_Practices.pptx"

LAYOUT_SINGLE = 13   # Title and content 2
LAYOUT_TWO_COL = 21  # Title two subtitle and two content 1

# Content area for Layout 13 textbox (matches PH 10 position)
CONTENT_LEFT = Inches(0.5)
CONTENT_TOP = Inches(2.1)
CONTENT_WIDTH = Inches(9.0)
CONTENT_HEIGHT = Inches(4.9)

FONT_NAME = "Calibri"


def clean_text(text):
    """Replace em-dashes and other problem characters with plain equivalents."""
    if not text:
        return ""
    text = text.replace("\u2014", "-")   # em-dash
    text = text.replace("\u2013", "-")   # en-dash
    text = text.replace("\u2018", "'")   # left single quote
    text = text.replace("\u2019", "'")   # right single quote
    text = text.replace("\u201c", '"')   # left double quote
    text = text.replace("\u201d", '"')   # right double quote
    return text


def add_para(tf, text, size=9, bold=False, italic=False, space_after=2, indent=0, first=False):
    """Add a paragraph to a text frame."""
    text = clean_text(text)
    if first:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = FONT_NAME
    p.space_after = Pt(space_after)
    if indent:
        p.level = indent
    return p


def render_sections(tf, sections, first_para=True):
    """Render a list of section dicts (heading, body, bullets) into a text frame."""
    is_first = first_para
    for sec in sections:
        if isinstance(sec, dict):
            # Heading
            heading = sec.get("heading", "")
            if heading:
                add_para(tf, heading, size=9, bold=True, space_after=1, first=is_first)
                is_first = False
            
            # Body text
            body = sec.get("body", "")
            if body:
                add_para(tf, body, size=8, space_after=3, first=is_first)
                is_first = False
            
            # Bullets
            for bullet in sec.get("bullets", []):
                add_para(tf, bullet, size=8, space_after=1, indent=1, first=is_first)
                is_first = False
    return is_first


def build_title_slide(prs, data):
    """Title slide using Layout 13 with subtitle in a textbox."""
    slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT_SINGLE])
    slide.placeholders[0].text = clean_text(data["title"])
    
    txBox = slide.shapes.add_textbox(CONTENT_LEFT, CONTENT_TOP, CONTENT_WIDTH, CONTENT_HEIGHT)
    tf = txBox.text_frame
    tf.word_wrap = True
    
    subtitle = data.get("subtitle", "")
    if subtitle:
        add_para(tf, subtitle, size=12, italic=True, space_after=6, first=True)
    
    footer = data.get("footer", "")
    if footer:
        add_para(tf, "", size=6, space_after=2)
        add_para(tf, footer, size=8, italic=True)


def build_single_slide(prs, data):
    """Single-column content slide using Layout 13 with a textbox."""
    slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT_SINGLE])
    slide.placeholders[0].text = clean_text(data["title"])
    
    txBox = slide.shapes.add_textbox(CONTENT_LEFT, CONTENT_TOP, CONTENT_WIDTH, CONTENT_HEIGHT)
    tf = txBox.text_frame
    tf.word_wrap = True
    
    sections = data.get("sections", [])
    render_sections(tf, sections, first_para=True)


def build_two_column_slide(prs, data):
    """Two-column slide using Layout 21 with native placeholders."""
    slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT_TWO_COL])
    
    # Title
    slide.placeholders[0].text = clean_text(data["title"])
    
    # Left subtitle (PH 10)
    left_header = data.get("left_header", "")
    if left_header:
        slide.placeholders[10].text = clean_text(left_header)
    
    # Right subtitle (PH 11)
    right_header = data.get("right_header", "")
    if right_header:
        slide.placeholders[11].text = clean_text(right_header)
    
    # Left content (PH 1)
    left_tf = slide.placeholders[1].text_frame
    left_tf.clear()
    left_sections = data.get("left_sections", [])
    render_sections(left_tf, left_sections, first_para=True)
    
    # Right content (PH 2)
    right_tf = slide.placeholders[2].text_frame
    right_tf.clear()
    right_sections = data.get("right_sections", [])
    render_sections(right_tf, right_sections, first_para=True)
    
    # Footer as a separate small textbox at bottom
    footer = data.get("footer", "")
    if footer:
        ftBox = slide.shapes.add_textbox(
            Inches(0.5), Inches(6.7), Inches(9.0), Inches(0.3)
        )
        ft_tf = ftBox.text_frame
        ft_tf.word_wrap = True
        add_para(ft_tf, footer, size=7, italic=True, first=True)


# --- Main ---

with open(YAML_PATH, "r") as f:
    content = yaml.safe_load(f)

prs = Presentation(TEMPLATE_PATH)

builders = {
    "title": build_title_slide,
    "single": build_single_slide,
    "two_column": build_two_column_slide,
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
print(f"Slides: {len(prs.slides)}")
