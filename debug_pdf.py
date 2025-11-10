#!/usr/bin/env python3
"""
PDF Debugging Tool
Analyzes PDF files to identify parsing issues
"""

import PyPDF2
import re
import json
from io import BytesIO
from pathlib import Path

def analyze_pdf_structure(pdf_path):
    """
    Analyze PDF structure and content
    """
    print(f"🔍 Analyzing PDF: {pdf_path}")
    print("=" * 50)

    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            print(f"📄 PDF Info:")
            print(f"   Pages: {len(reader.pages)}")
            print(f"   Title: {reader.metadata.title if reader.metadata else 'N/A'}")
            print(f"   Author: {reader.metadata.author if reader.metadata else 'N/A'}")
            print(f"   Creator: {reader.metadata.creator if reader.metadata else 'N/A'}")
            print(f"   Producer: {reader.metadata.producer if reader.metadata else 'N/A'}")
            print()

            print("📋 Page Analysis:")
            total_text = ""

            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    text_length = len(page_text.strip())

                    print(f"   Page {i+1}: {text_length} characters")

                    if text_length > 50:  # Only show substantial text
                        print(f"   First 200 chars: {page_text[:200]}...")
                        total_text += f"\n--- Page {i+1} ---\n{page_text}\n"

                    # Check for common salary patterns on each page
                    salary_patterns = find_salary_patterns(page_text)
                    if salary_patterns:
                        print(f"   💰 Found {len(salary_patterns)} salary patterns")

                except Exception as e:
                    print(f"   ❌ Error extracting page {i+1}: {e}")

            print()
            print("🔍 Full Text Analysis:")
            print(f"   Total characters: {len(total_text)}")

            # Search for key terms
            key_terms = [
                'salary', 'gaji', 'upah', 'penghasilan', 'base', 'bonus',
                'benefit', 'tunjangan', 'allowance', 'compensation', 'kompetensi',
                'position', 'jabatan', 'job', 'pekerjaan'
            ]

            found_terms = []
            for term in key_terms:
                if term.lower() in total_text.lower():
                    count = total_text.lower().count(term.lower())
                    found_terms.append(f"{term}: {count}")

            if found_terms:
                print("   🔑 Key terms found:", ", ".join(found_terms))
            else:
                print("   ❌ No key terms found")

            # Search for money patterns
            money_patterns = find_money_patterns(total_text)
            print(f"   💰 Money patterns found: {len(money_patterns)}")
            for pattern in money_patterns[:5]:  # Show first 5
                print(f"      - {pattern}")

            # Save full text for manual review
            output_file = Path(pdf_path).with_suffix('.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(total_text)
            print(f"   💾 Full text saved to: {output_file}")

            return total_text

    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return None

def find_salary_patterns(text):
    """
    Find potential salary information in text
    """
    patterns = []

    # Indonesian salary patterns
    id_patterns = [
        r'gaji\s+(?:pokok|dasar)?\s*[:.]?\s*([0-9.,]+)',
        r'upah\s+(?:bulanan|per\s+bulan)\s*[:.]?\s*([0-9.,]+)',
        r'penghasilan\s+(?:bulanan|per\s+bulan)\s*[:.]?\s*([0-9.,]+)',
        r'rp\.?\s*([0-9.,]+)\s*(?:per\s+bulan|bulanan)',
        r'([0-9.,]+)\s*(?:per\s+bulan|bulan)',
    ]

    # English salary patterns
    en_patterns = [
        r'salary\s*(?:base|basic)?\s*[:.]?\s*([0-9.,]+)',
        r'base\s+salary\s*[:.]?\s*([0-9.,]+)',
        r'annual\s+salary\s*[:.]?\s*([0-9.,]+)',
        r'\$([0-9.,]+)\s*(?:per\s+year|annually)',
        r'compensation\s*[:.]?\s*\$?([0-9.,]+)',
    ]

    all_patterns = id_patterns + en_patterns

    for pattern in all_patterns:
        matches = re.findall(pattern, text.lower(), re.IGNORECASE)
        if matches:
            patterns.extend(matches)

    return list(set(patterns))

def find_money_patterns(text):
    """
    Find money/amount patterns in text
    """
    patterns = []

    # Various currency patterns
    money_regex = r'([Rp$]?\s*[0-9.,]+\s*(?:jt|juta|million|thousand|ribu)?)'
    matches = re.findall(money_regex, text, re.IGNORECASE)

    for match in matches:
        # Get context around the match
        index = text.lower().find(match.lower())
        if index != -1:
            start = max(0, index - 50)
            end = min(len(text), index + len(match) + 50)
            context = text[start:end].strip()
            patterns.append(context)

    return patterns[:10]  # Return first 10 matches

def main():
    pdf_path = r"C:\Users\User\Downloads\offering_letter_PT_PerKasa_Pilar_Utama_Imam_Fahrudin.pdf"

    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        print("Please update the file path in the script")
        return

    print("🚀 PDF Analysis Tool")
    print("=" * 50)

    # Analyze PDF structure
    text = analyze_pdf_structure(pdf_path)

    if text:
        print("\n🔧 Suggestions:")
        print("1. Check if the PDF is scanned (text might be images)")
        print("2. Try converting PDF to text-based format")
        print("3. Check for password protection")
        print("4. Verify PDF is not corrupted")
        print("5. Consider using OCR if it's a scanned document")

        # Test with offer parser
        print("\n🧪 Testing with Offer Parser...")
        try:
            from services.offer_parser import OfferLetterParser
            parser = OfferLetterParser()

            with open(pdf_path, 'rb') as file:
                file_bytes = file.read()

            result = parser._extract_pdf_text(file_bytes)
            print(f"   Text extraction: {'SUCCESS' if result else 'FAILED'}")
            print(f"   Extracted characters: {len(result)}")

        except Exception as e:
            print(f"   ❌ Parser test failed: {e}")

if __name__ == "__main__":
    main()