#!/usr/bin/env python3
"""Apollo R118 student-print custody lint. SOURCE-ONLY; not Chromium, axe or rights clearance."""
from __future__ import annotations
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class PrintIntegrityError(ValueError):
    pass

class WorksheetParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sheet = False
        self.prompts = False
        self.sheet_count = 0
        self.prompt_count = 0
        self.response_lines = 0
        self.links = []
        self.sheet_text = []
        self.ctas = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "data-fv-primary-cta" in a:
            self.ctas += 1
        if tag == "article" and "data-fv-student-print" in a:
            if self.sheet:
                raise PrintIntegrityError("NESTED_WORKSHEET")
            self.sheet = True
            self.sheet_count += 1
        if self.sheet and tag == "ol" and "data-fv-student-prompts" in a:
            self.prompts = True
        if self.prompts and tag == "li":
            self.prompt_count += 1
        if self.sheet and tag == "span":
            self.response_lines += 1
        if self.sheet and tag == "a":
            self.links.append(a.get("href", ""))
    def handle_data(self, data):
        if self.sheet:
            self.sheet_text.append(data)
    def handle_endtag(self, tag):
        if self.prompts and tag == "ol":
            self.prompts = False
        if self.sheet and tag == "article":
            self.sheet = False

def require(condition: bool, message: str) -> None:
    if not condition:
        raise PrintIntegrityError(message)

def validate(source: str) -> dict:
    p = WorksheetParser()
    p.feed(source)
    require(p.sheet_count == 1, "ONE_PRINT_WORKSHEET")
    require(p.prompt_count == 3, "THREE_STUDENT_PROMPTS")
    require(p.response_lines == 9, "NINE_WRITING_LINES")
    require(p.ctas == 1, "EXACTLY_ONE_PRIMARY_CTA")
    require(source.count("<script>") == 1 and source.count("<style>") == 1,
            "EXISTING_PROGRESSIVE_ENHANCEMENT_BOUNDARY")
    require(".print-custody,.student-print-sheet{display:none}" in source,
            "WORKSHEET_SCREEN_VISIBILITY")
    media = source.partition("@media print{")[2].partition("</style>")[0]
    require(bool(media), "PRINT_STYLES_MISSING")
    require("#classroom-preview .callout{display:none!important}" in media,
            "PRIVATE_TEACHER_ANSWERS_MAY_PRINT")
    require(".student-print-sheet{display:block!important" in media,
            "STUDENT_SHEET_NOT_PRINTED")
    require("#classroom-preview{break-before:page}" in media,
            "PRINT_READING_ORDER")
    expected = {
        "https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/",
        "https://www.nasa.gov/apollo-1-resources/",
    }
    require(set(p.links) == expected, "WORKSHEET_SOURCE_LINKS")
    text = " ".join(" ".join(p.sheet_text).split())
    for phrase in (
        "Central question", "Apollo 204 Review Board",
        "hatch", "ignition source", "photograph", "January 27",
        "Two independently identified sources",
        "Suggested answer and teaching notes are intentionally excluded from print",
    ):
        require(phrase in text, "WORKSHEET_REQUIRED_TEXT:" + phrase)
    require("0/6" in source and "S67-19766 (provisional)" in source,
            "PHOTOGRAPHIC_RIGHTS_PROVISIONAL")
    return {
        "classification": "SOURCE_CONTRACT_ONLY_NOT_BROWSER_OR_MERCHANT_ACCEPTANCE",
        "sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "student_prompts": p.prompt_count,
        "writing_lines": p.response_lines,
        "official_sources": len(p.links),
        "primary_ctas": p.ctas,
        "production_status": "STAGING_HOLD",
    }

if __name__ == "__main__":
    print(json.dumps(validate((ROOT / "landing-preview.html").read_text(encoding="utf-8")),
                     indent=2, sort_keys=True))
