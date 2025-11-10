#!/usr/bin/env python3
"""
Test UMK (Upah Minimum Kabupaten/Kota) functionality
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(Path(__file__).parent)

def test_umk_functionality():
    """Test UMK checking functionality"""

    print("Testing UMK Functionality")
    print("=" * 50)

    try:
        from services.umk_data import get_umk_for_location, calculate_umk_compliance, format_umk, format_umk

        # Test cases with different locations
        test_cases = [
            "Jakarta",
            "Bandung",
            "Surabaya",
            "Denpasar",
            "Medan",
            "Unknown Location"
        ]

        test_salaries = [3000000, 6000000, 12000000]  # 3M, 6M, 12M IDR per month

        for location in test_cases:
            print(f"\nTesting location: {location}")
            print("-" * 30)

            # Get UMK data
            umk_data = get_umk_for_location(location)
            if umk_data:
                print(f"UMK Data Found:")
                print(f"  Kabupaten/Kota: {umk_data['kabupaten_kota']}")
                print(f"  Provinsi: {umk_data['provinsi']}")
                print(f"  UMK Amount: {format_umk(umk_data['umk'])}")
                print(f"  Region: {umk_data['region']}")

                # Test compliance with different salaries
                for salary in test_salaries:
                    print(f"\n  Testing salary: {format_umk(salary)} per bulan")
                    compliance = calculate_umk_compliance(salary, umk_data)
                    print(f"    Annual Salary: {compliance['annual_salary_formatted']}")
                    print(f"    Annual UMK: {compliance['annual_umk_formatted']}")
                    print(f"    Compliance: {'PASS' if compliance['complies'] else 'FAIL'}")
                    print(f"    Percentage Above UMK: {compliance['percentage_above_umk']}%")
                    print(f"    Message: {compliance['message']}")
            else:
                print(f"UMK Data: NOT FOUND for {location}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

def test_actual_offer_letter():
    """Test with actual offer letter data"""
    print("\n" + "=" * 50)
    print("Testing with Actual Offer Letter Data")
    print("=" * 50)

    try:
        from services.umk_data import get_umk_for_location, calculate_umk_compliance, format_umk

        # Test with Imam's offer letter data
        offer_data = {
            'job_title': 'Middle OutSystems Developer',
            'company': 'PT. Perkasa Pilar Utama',
            'location': 'Jakarta',  # or could be more specific location
            'base_salary': 6000000,  # Rp 6.000.000 per month
            'bonus': 0,
            'equity_value': 0
        }

        print(f"Offer Data:")
        print(f"  Job Title: {offer_data['job_title']}")
        print(f"  Company: {offer_data['company']}")
        print(f"  Location: {offer_data['location']}")
        print(f"  Base Salary: {format_umk(offer_data['base_salary'])}")
        print(f"  Annual Salary: {format_umk(offer_data['base_salary'] * 12)}")

        # Get UMK data
        umk_data = get_umk_for_location(offer_data['location'])

        if umk_data:
            print(f"\nUMK Analysis:")
            print(f"  Location UMK: {format_umk(umk_data['umk'])} per month")
            print(f"  Annual UMK: {format_umk(umk_data['umk'] * 12)}")

            # Check compliance
            compliance = calculate_umk_compliance(offer_data['base_salary'], umk_data)

            print(f"\nCompliance Results:")
            print(f"  Meets UMK: {'YES' if compliance['complies'] else 'NO'}")
            print(f"  Difference: {compliance['difference_formatted']}")
            print(f"  Annual Difference: {format_umk(compliance['difference'] * 12)}")
            print(f"  Percentage: {compliance['percentage_above_umk']}%")
            print(f"  Risk Level: {compliance['risk_level']}")
            print(f"  Message: {compliance['message']}")

            # Analysis verdict
            annual_salary = offer_data['base_salary'] * 12
            annual_umk = umk_data['umk'] * 12

            if annual_salary < annual_umk:
                verdict = "BELOW_UMK"
            elif annual_salary < annual_umk * 1.2:
                verdict = "FAIR"
            elif annual_salary < annual_umk * 1.5:
                verdict = "COMPETITIVE"
            else:
                verdict = "EXCELLENT"

            print(f"\nSuggested Verdict: {verdict}")

        else:
            print(f"UMK Data: NOT FOUND for {offer_data['location']}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

def test_location_matching():
    """Test various location formats"""
    print("\n" + "=" * 50)
    print("Testing Location Matching")
    print("=" * 50)

    try:
        from services.umk_data import get_umk_for_location

        test_locations = [
            "Jakarta",
            "DKI Jakarta",
            "Jakarta Pusat",
            "Kota Bandung",
            "Bandung",
            "Kabupaten Bandung",
            "Surabaya",
            "Medan",
            "Palembang",
            "Makassar",
            "Unknown City",
            "Remote",
            ""
        ]

        for location in test_locations:
            result = get_umk_for_location(location)
            status = "Found" if result else "Not Found"
            umk_value = result['umk'] if result else 0
            print(f"{status:20} {location:20} -> Rp {umk_value:,}".replace(',', '.'))
            if result:
                print(f"           {result['kabupaten_kota']}, {result['provinsi']}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_umk_functionality()
    test_actual_offer_letter()
    test_location_matching()