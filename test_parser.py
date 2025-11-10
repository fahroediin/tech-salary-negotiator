#!/usr/bin/env python3
"""
Test Offer Parser without Gemini API
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(Path(__file__).parent)

def test_fallback_parsing():
    """Test fallback parsing with Indonesian offer letter"""

    print("Testing Offer Parser - Indonesian Format")
    print("=" * 50)

    # Sample Indonesian offer text (from the PDF)
    sample_text = """Offering Letter – Middle OutSystems Developer
Tanggal: 1 Januari 2026
Kepada Yth,
Imam Fahrudin
di Tempat
Berdasarkan proses rekrutmen yang telah dilakukan, kami dengan senang hati menyampaikan bahwa
Anda dinyatakan diterima untuk bergabung sebagai Middle OutSystems Developer di PT. Perkasa Pilar
Utama.
Posisi
Middle OutSystems Developer
Status Karyawan
Kontrak
Tanggal Mulai
1 Januari 2026
Lokasi Kerja
Onsite
Gaji Take Home Pay
Rp 6.000.000
Kami berharap Anda dapat memberikan konfirmasi penerimaan penawaran ini paling lambat sebelum
tanggal mulai yang tercantum. Konfirmasi dapat dilakukan melalui email balasan atau menghubungi HR
terkait.
Hormat kami,
Human Resources Department
PT. Perkasa Pilar Utama"""

    try:
        from services.offer_parser import OfferLetterParser
        parser = OfferLetterParser()

        print("1. Testing fallback parsing...")
        result = parser._fallback_parse(sample_text)

        if result:
            print("SUCCESS: Fallback parsing successful!")
            print("Extracted data:")
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print("FAILED: Fallback parsing failed")

        print("\n2. Testing validation...")
        cleaned_data = parser._validate_and_clean_data(result)
        print("Cleaned data:")
        for key, value in cleaned_data.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_salary_patterns():
    """Test specific salary patterns"""

    print("\n" + "=" * 50)
    print("Testing Salary Patterns")
    print("=" * 50)

    import re

    test_cases = [
        "Gaji Take Home Pay\nRp 6.000.000",
        "Base Salary: Rp 10.000.000 per bulan",
        "Upah: Rp 8,500,000",
        "Compensation: $120,000 annually",
    ]

    salary_patterns = [
        # Indonesian patterns
        r'rp\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
        r'gaji.*?rp\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
        r'take\s+home\s+pay.*?rp\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
        r'penghasilan.*?([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
        r'upah.*?([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
        # English patterns
        r'\$([0-9]{1,3}(?:,[0-9]{3})*)',
    ]

    for test_case in test_cases:
        print(f"\nTesting: {test_case}")
        for pattern in salary_patterns:
            match = re.search(pattern, test_case, re.IGNORECASE)
            if match:
                salary_str = match.group(1)

                # Handle Indonesian format
                if '.' in salary_str and ',' in salary_str:
                    salary_str = salary_str.replace('.', '').replace(',', '.')
                elif '.' in salary_str and ',' not in salary_str:
                    if salary_str.count('.') > 1:
                        salary_str = salary_str.replace('.', '')
                elif ',' in salary_str and '.' not in salary_str:
                    if salary_str.count(',') > 1:
                        salary_str = salary_str.replace(',', '')

                try:
                    salary = int(float(salary_str))
                    print(f"  SUCCESS: Pattern '{pattern[:30]}...' matched: {salary}")
                except ValueError as e:
                    print(f"  FAILED: Pattern '{pattern[:30]}...' failed: {e}")
                break

if __name__ == "__main__":
    test_fallback_parsing()
    test_salary_patterns()