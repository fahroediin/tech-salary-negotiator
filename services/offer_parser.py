import re
import PyPDF2
from io import BytesIO
from typing import Dict, Optional
import google.generativeai as genai
import os
import json
import logging

logger = logging.getLogger(__name__)

class OfferLetterParser:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    async def parse_pdf(self, file_bytes: bytes) -> Dict:
        """
        Extract text from PDF and parse key information using AI
        """
        try:
            # Extract text from PDF
            logger.info("Extracting text from PDF")
            text = await self._extract_pdf_text(file_bytes)

            if not text or len(text.strip()) < 50:
                raise ValueError("PDF appears to be empty or unreadable")

            # Use Gemini to extract structured data
            logger.info("Extracting structured data with AI")
            extracted_data = await self._extract_with_ai(text)

            # Validate and clean the extracted data
            cleaned_data = self._validate_and_clean_data(extracted_data)

            logger.info(f"Successfully parsed offer for {cleaned_data.get('company', 'Unknown company')}")
            return cleaned_data

        except Exception as e:
            logger.error(f"Failed to parse PDF: {str(e)}")
            raise ValueError(f"Failed to parse PDF: {str(e)}")

    async def _extract_pdf_text(self, file_bytes: bytes) -> str:
        """
        Extract text from PDF bytes
        """
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
            text = ""

            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                except Exception as e:
                    logger.warning(f"Could not extract text from page {page_num + 1}: {e}")
                    continue

            return text.strip()

        except Exception as e:
            raise ValueError(f"Failed to read PDF: {str(e)}")

    async def _extract_with_ai(self, text: str) -> Dict:
        """
        Use Gemini to extract structured information from offer text
        """
        try:
            prompt = f"""
You are an expert at parsing job offer letters. Extract the following information from this offer letter text and return it as valid JSON.

Offer letter text:
{text}

Extract ONLY these fields:
- company: Company name (exact spelling from document)
- job_title: Job title/position (exact spelling from document)
- location: Work location (city, state or remote)
- base_salary: Annual base salary (number only, no currency symbols or commas)
- bonus: Annual bonus or target bonus (number only, 0 if not mentioned)
- equity: Equity grant details text (RSUs, stock options, etc. as described in document)
- equity_value: Estimated annual equity value (number only, 0 if not mentioned or unclear)
- start_date: Expected start date (YYYY-MM-DD format or text as written)
- benefits: List of benefits mentioned (health insurance, 401k, PTO, etc.)

Rules:
1. Return ONLY valid JSON, no other text or markdown formatting
2. Use null for any field that cannot be found in the text
3. For salary/bonus numbers, extract only the numeric value (e.g., from "$120,000" extract 120000)
4. Be precise with company names and job titles - extract exactly as written
5. If multiple salary figures are mentioned, use the base salary figure
6. For equity_value, try to calculate annual value from vesting schedule if possible

JSON response:
"""

            response = self.model.generate_content(prompt)
            json_text = response.text.strip()

            # Clean up the response to extract JSON
            json_text = self._clean_json_response(json_text)

            try:
                return json.loads(json_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {json_text[:500]}...")
                # Fallback to basic parsing
                return self._fallback_parse(text)

        except Exception as e:
            logger.error(f"AI extraction failed: {str(e)}")
            # Fallback to basic regex-based parsing
            return self._fallback_parse(text)

    def _clean_json_response(self, text: str) -> str:
        """
        Clean the AI response to extract valid JSON
        """
        # Remove markdown code blocks
        text = re.sub(r'```json\n?', '', text)
        text = re.sub(r'\n?```', '', text)

        # Remove any leading/trailing text that's not JSON
        text = text.strip()

        # Find JSON object boundaries
        start_idx = text.find('{')
        end_idx = text.rfind('}')

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return text[start_idx:end_idx + 1]

        return text

    def _fallback_parse(self, text: str) -> Dict:
        """
        Fallback parsing using regex patterns
        """
        result = {
            'company': None,
            'job_title': None,
            'location': None,
            'base_salary': None,
            'bonus': None,
            'equity': None,
            'equity_value': None,
            'start_date': None,
            'benefits': None
        }

        try:
            # Extract salary patterns
            salary_patterns = [
                r'\$?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)\s*(?:per\s*year|annual|annually|salary)',
                r'salary.*?\$?([0-9]{1,3}(?:,[0-9]{3})*)',
                r'base\s+pay.*?\$?([0-9]{1,3}(?:,[0-9]{3})*)',
                r'compensation.*?\$?([0-9]{1,3}(?:,[0-9]{3})*)'
            ]

            for pattern in salary_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    salary_str = match.group(1).replace(',', '')
                    try:
                        result['base_salary'] = int(float(salary_str))
                        break
                    except ValueError:
                        continue

            # Extract bonus patterns
            bonus_patterns = [
                r'bonus.*?\$?([0-9]{1,3}(?:,[0-9]{3})*)',
                r'target\s+bonus.*?\$?([0-9]{1,3}(?:,[0-9]{3})*)',
                r'annual\s+bonus.*?\$?([0-9]{1,3}(?:,[0-9]{3})*)'
            ]

            for pattern in bonus_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    bonus_str = match.group(1).replace(',', '')
                    try:
                        result['bonus'] = int(float(bonus_str))
                        break
                    except ValueError:
                        continue

            # Extract company (look for common company name patterns)
            lines = text.split('\n')
            for i, line in enumerate(lines[:10]):  # Check first 10 lines
                line = line.strip()
                if len(line) > 3 and len(line) < 100:
                    # Skip common headers
                    if not any(word in line.lower() for word in ['offer', 'letter', 'employment', 'job', 'position', 'date']):
                        if not result['company']:
                            result['company'] = line
                            break

            # Extract job title
            title_patterns = [
                r'position:\s*(.+)',
                r'job title:\s*(.+)',
                r'role:\s*(.+)',
                r'as\s+(?:a\s+)?([A-Z][a-zA-Z\s]+)',
                r'(Senior|Junior|Lead|Principal|Staff).*?(Engineer|Developer|Manager|Director)'
            ]

            for pattern in title_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
                    if len(title) > 3 and len(title) < 100:
                        result['job_title'] = title
                        break

        except Exception as e:
            logger.error(f"Fallback parsing failed: {str(e)}")

        return result

    def _validate_and_clean_data(self, data: Dict) -> Dict:
        """
        Validate and clean the extracted data
        """
        # Convert numeric fields
        numeric_fields = ['base_salary', 'bonus', 'equity_value']

        for field in numeric_fields:
            if field in data and data[field] is not None:
                try:
                    # Handle string numbers with commas/symbols
                    if isinstance(data[field], str):
                        # Remove currency symbols and commas
                        cleaned = re.sub(r'[$,]', '', str(data[field]))
                        data[field] = int(float(cleaned))

                    # Validate reasonable ranges
                    if field == 'base_salary':
                        if not (20000 <= data[field] <= 1000000):
                            data[field] = None
                    elif field in ['bonus', 'equity_value']:
                        if not (0 <= data[field] <= 500000):
                            data[field] = 0

                except (ValueError, TypeError):
                    data[field] = None
            else:
                # Set default values for missing fields
                if field == 'bonus' or field == 'equity_value':
                    data[field] = 0

        # Ensure benefits is a list
        if 'benefits' in data and data['benefits']:
            if isinstance(data['benefits'], str):
                # Split by common delimiters
                benefits = re.split(r'[,;•\n]', data['benefits'])
                data['benefits'] = [b.strip() for b in benefits if b.strip()]
            elif not isinstance(data['benefits'], list):
                data['benefits'] = []
        else:
            data['benefits'] = []

        # Clean string fields
        string_fields = ['company', 'job_title', 'location', 'equity', 'start_date']
        for field in string_fields:
            if field in data and data[field]:
                data[field] = str(data[field]).strip()
                if not data[field] or len(data[field]) > 500:
                    data[field] = None
            else:
                data[field] = None

        return data