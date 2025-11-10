#!/usr/bin/env python3
"""
Simple PDF Debugging Tool
"""

import PyPDF2
import re
import sys
import os
from pathlib import Path

def analyze_pdf(pdf_path):
    """
    Analyze PDF file structure and content
    """
    print(f"Analyzing PDF: {pdf_path}")
    print("=" * 50)

    if not Path(pdf_path).exists():
        print(f"ERROR: File not found: {pdf_path}")
        return False

    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            print(f"PDF Info:")
            print(f"  Pages: {len(reader.pages)}")
            if reader.metadata:
                print(f"  Title: {reader.metadata.get('title', 'N/A')}")
                print(f"  Author: {reader.metadata.get('author', 'N/A')}")
                print(f"  Creator: {reader.metadata.get('creator', 'N/A')}")

            print("\nAnalyzing pages:")
            total_text = ""

            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    text_length = len(page_text.strip())

                    print(f"  Page {i+1}: {text_length} characters")

                    if text_length > 10:
                        print(f"    First 100 chars: {page_text[:100]}")
                        total_text += f"\n--- Page {i+1} ---\n{page_text}\n"

                except Exception as e:
                    print(f"    ERROR extracting page {i+1}: {e}")

            print(f"\nTotal extracted text: {len(total_text)} characters")

            # Look for salary patterns
            if total_text:
                print("\nSearching for patterns:")

                # Indonesian patterns
                id_keywords = ['gaji', 'upah', 'penghasilan', 'rp', 'juta', 'ribu', 'tunjangan']
                found_id = [kw for kw in id_keywords if kw.lower() in total_text.lower()]
                print(f"  Indonesian keywords found: {found_id}")

                # English patterns
                en_keywords = ['salary', 'compensation', 'bonus', 'benefit', '$', 'annual']
                found_en = [kw for kw in en_keywords if kw.lower() in total_text.lower()]
                print(f"  English keywords found: {found_en}")

                # Money patterns
                money_regex = r'([Rp$]?\s*[0-9.,]+\s*(?:jt|juta|million|thousand|ribu)?)'
                money_matches = re.findall(money_regex, total_text, re.IGNORECASE)
                print(f"  Money patterns found: {len(money_matches)}")
                for match in money_matches[:3]:
                    print(f"    - {match}")

            # Save extracted text
            output_path = Path(pdf_path).with_suffix('.txt')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(total_text)
            print(f"\nExtracted text saved to: {output_path}")

            return True

    except Exception as e:
        print(f"ERROR reading PDF: {e}")
        return False

def test_pdf_parsing(pdf_path):
    """
    Test PDF with actual offer parser
    """
    print("\n" + "=" * 50)
    print("Testing with Offer Parser:")

    try:
        from services.offer_parser import OfferLetterParser
        parser = OfferLetterParser()

        with open(pdf_path, 'rb') as file:
            file_bytes = file.read()

        text = parser._extract_pdf_text(file_bytes)
        print(f"Text extraction: {'SUCCESS' if text else 'FAILED'}")
        print(f"Extracted length: {len(text)} characters")

        if text and len(text) > 50:
            try:
                # Try AI parsing
                print("Testing AI parsing...")
                result = parser._extract_with_ai(text)
                print(f"AI parsing: {'SUCCESS' if result else 'FAILED'}")
                if result:
                    print(f"Extracted keys: {list(result.keys())}")
            except Exception as e:
                print(f"AI parsing failed: {e}")

            # Try fallback parsing
            print("Testing fallback parsing...")
            result = parser._fallback_parse(text)
            print(f"Fallback parsing: {'SUCCESS' if result else 'FAILED'}")
            if result:
                print(f"Extracted keys: {list(result.keys())}")
                if result.get('base_salary'):
                    print(f"  Base salary: {result['base_salary']}")
                if result.get('job_title'):
                    print(f"  Job title: {result['job_title']}")

    except Exception as e:
        print(f"ERROR: {e}")

def main():
    pdf_path = r"C:\Users\User\Downloads\offering_letter_PT_PerKasa_Pilar_Utama_Imam_Fahrudin.pdf"

    print("PDF Debugging Tool")
    print("=" * 50)

    # Change directory to project root
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    success = analyze_pdf(pdf_path)

    if success:
        test_pdf_parsing(pdf_path)
    else:
        print("\nSuggestions:")
        print("1. Check if file exists and is accessible")
        print("2. Verify PDF is not password protected")
        print("3. Try opening the PDF manually first")
        print("4. Check file size (should not be 0 bytes)")

if __name__ == "__main__":
    main()