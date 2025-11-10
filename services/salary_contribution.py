import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, List
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

class SalaryContributionService:
    def __init__(self, db_url: str):
        self.db_url = db_url

    async def submit_salary_data(self, data: Dict) -> Dict:
        """
        Accept anonymous salary contribution with validation and deduplication
        """
        try:
            logger.info("Processing salary contribution")

            # Validate data
            validation = self._validate_submission(data)
            if not validation['is_valid']:
                logger.warning(f"Invalid submission: {validation['error']}")
                return {
                    'success': False,
                    'error': validation['error']
                }

            # Generate submission hash to detect duplicates
            submission_hash = self._generate_submission_hash(data)

            from database import SessionLocal

            db = SessionLocal()

            try:
                # Check for recent duplicate submissions
                duplicate_query = text("""
                SELECT id FROM salary_data
                WHERE submission_hash = :submission_hash
                AND submitted_date > :cutoff_date
                """)

                cutoff_date = datetime.now() - timedelta(hours=24)

                duplicate = db.execute(duplicate_query, {
                    'submission_hash': submission_hash,
                    'cutoff_date': cutoff_date
                }).fetchone()

                if duplicate:
                    logger.info("Duplicate submission detected")
                    return {
                        'success': False,
                        'error': 'This exact salary data was recently submitted. Thank you for your contribution!'
                    }

                # Calculate confidence score
                confidence = self._calculate_confidence_score(data)

                # Normalize job title
                normalized_title = self._normalize_title(data['job_title'])

                # Get location tier
                location_tier = self._get_location_tier(data['location'])

                # Calculate total compensation
                total_comp = (
                    data.get('base_salary', 0) +
                    data.get('bonus', 0) +
                    data.get('equity_value', 0)
                )

                # Get company tier
                company_tier = self._get_company_tier(data.get('company', ''))

                # Parse benefits if provided
                benefits = data.get('benefits', {})
                if isinstance(benefits, str):
                    try:
                        import json
                        benefits = json.loads(benefits)
                    except:
                        benefits = {'description': benefits}

                # Create new salary data record
                from database import SalaryData

                salary_record = SalaryData(
                    job_title=data['job_title'],
                    normalized_title=normalized_title,
                    company=data.get('company', 'Anonymous'),
                    company_tier=company_tier,
                    location=data['location'],
                    location_tier=location_tier,
                    base_salary=data['base_salary'],
                    bonus=data.get('bonus', 0),
                    equity_value=data.get('equity_value', 0),
                    total_comp=total_comp,
                    years_experience=data['years_experience'],
                    tech_stack=data.get('tech_stack', []),
                    benefits=benefits,
                    is_verified=confidence >= 0.7,  # Verified threshold
                    confidence_score=confidence,
                    submission_hash=submission_hash,
                    submitted_date=datetime.now()
                )

                db.add(salary_record)
                db.commit()

                logger.info(f"Successfully submitted salary data with confidence {confidence:.2f}")

                return {
                    'success': True,
                    'message': 'Thank you for your contribution! This helps others negotiate better salaries.',
                    'confidence_score': round(confidence, 2),
                    'data_quality': 'high' if confidence >= 0.8 else 'medium' if confidence >= 0.6 else 'low'
                }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error submitting salary data: {str(e)}")
            return {
                'success': False,
                'error': 'An error occurred while processing your submission. Please try again.'
            }

    def _validate_submission(self, data: Dict) -> Dict:
        """
        Validate salary submission data
        """
        required_fields = ['job_title', 'location', 'base_salary', 'years_experience']

        for field in required_fields:
            if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                return {
                    'is_valid': False,
                    'error': f'Missing required field: {field.replace("_", " ").title()}'
                }

        # Validate base salary range
        base_salary = data['base_salary']
        try:
            base_salary = int(base_salary)
        except (ValueError, TypeError):
            return {
                'is_valid': False,
                'error': 'Base salary must be a valid number'
            }

        if base_salary < 20000:
            return {
                'is_valid': False,
                'error': 'Base salary seems too low (minimum: $20,000)'
            }

        if base_salary > 1000000:
            return {
                'is_valid': False,
                'error': 'Base salary seems too high (maximum: $1,000,000)'
            }

        # Validate years experience
        try:
            years_exp = int(data['years_experience'])
            if years_exp < 0 or years_exp > 50:
                return {
                    'is_valid': False,
                    'error': 'Years of experience must be between 0 and 50'
                }
        except (ValueError, TypeError):
            return {
                'is_valid': False,
                'error': 'Years of experience must be a valid number'
            }

        # Validate job title length
        if len(data['job_title'].strip()) < 3 or len(data['job_title'].strip()) > 200:
            return {
                'is_valid': False,
                'error': 'Job title must be between 3 and 200 characters'
            }

        # Validate location length
        if len(data['location'].strip()) < 2 or len(data['location'].strip()) > 100:
            return {
                'is_valid': False,
                'error': 'Location must be between 2 and 100 characters'
            }

        # Validate optional numeric fields
        for field in ['bonus', 'equity_value']:
            if field in data and data[field] is not None:
                try:
                    value = int(data[field])
                    if value < 0:
                        return {
                            'is_valid': False,
                            'error': f'{field.replace("_", " ").title()} cannot be negative'
                        }
                    if value > 1000000:
                        return {
                            'is_valid': False,
                            'error': f'{field.replace("_", " ").title()} seems too high'
                        }
                except (ValueError, TypeError):
                    return {
                        'is_valid': False,
                        'error': f'{field.replace("_", " ").title()} must be a valid number'
                    }

        return {'is_valid': True}

    def _calculate_confidence_score(self, data: Dict) -> float:
        """
        Calculate confidence score for submission based on completeness and reasonableness
        """
        score = 0.0
        max_score = 0.0

        # Company name (0.2 points)
        max_score += 0.2
        if data.get('company') and len(data['company'].strip()) > 2:
            score += 0.2

        # Salary reasonableness (0.3 points)
        max_score += 0.3
        if self._is_reasonable_salary(data['base_salary'], data['years_experience']):
            score += 0.3

        # Tech stack (0.2 points)
        max_score += 0.2
        tech_stack = data.get('tech_stack', [])
        if tech_stack and len(tech_stack) > 0:
            if len(tech_stack) >= 3:
                score += 0.2
            else:
                score += 0.1

        # Bonus and equity (0.15 points)
        max_score += 0.15
        if data.get('bonus') and data['bonus'] > 0:
            score += 0.075
        if data.get('equity_value') and data['equity_value'] > 0:
            score += 0.075

        # Benefits information (0.1 points)
        max_score += 0.1
        if data.get('benefits'):
            score += 0.1

        # Experience level detail (0.05 points)
        max_score += 0.05
        years_exp = data.get('years_experience', 0)
        if isinstance(years_exp, int) and 0 <= years_exp <= 50:
            score += 0.05

        return score / max_score if max_score > 0 else 0.0

    def _is_reasonable_salary(self, salary: int, years_exp: int) -> bool:
        """
        Check if salary is reasonable based on experience level
        """
        # Base minimum and maximum ranges by experience
        exp_ranges = {
            0: (40000, 120000),    # Entry level
            2: (50000, 150000),    # 2 years
            5: (70000, 200000),    # 5 years
            10: (100000, 300000),  # 10 years
            15: (120000, 400000),  # 15 years
            20: (130000, 500000),  # 20+ years
        }

        # Find the appropriate range
        for exp, (min_sal, max_sal) in sorted(exp_ranges.items(), reverse=True):
            if years_exp >= exp:
                return min_sal <= salary <= max_sal

        # Default to entry level range
        return 40000 <= salary <= 120000

    def _generate_submission_hash(self, data: Dict) -> str:
        """
        Generate hash to detect duplicate submissions
        """
        # Create a normalized string representation
        hash_data = {
            'job_title': data['job_title'].lower().strip(),
            'base_salary': str(data['base_salary']),
            'location': data['location'].lower().strip(),
            'years_experience': str(data['years_experience']),
            'company': data.get('company', '').lower().strip()
        }

        # Sort keys and create consistent string
        hash_string = '|'.join([f"{k}:{v}" for k, v in sorted(hash_data.items())])

        return hashlib.sha256(hash_string.encode()).hexdigest()

    def _normalize_title(self, title: str) -> str:
        """
        Normalize job title to standard format for database queries
        """
        if not title:
            return 'unknown'

        title_lower = title.lower().strip()

        # Software Engineer variants
        if any(term in title_lower for term in ['software engineer', 'swe', 'software developer', 'developer']):
            if any(term in title_lower for term in ['senior', 'sr', 'lead']):
                return 'senior_software_engineer'
            elif 'staff' in title_lower:
                return 'staff_software_engineer'
            elif 'principal' in title_lower:
                return 'principal_software_engineer'
            elif any(term in title_lower for term in ['junior', 'jr', 'associate']):
                return 'junior_software_engineer'
            else:
                return 'software_engineer'

        # Product Manager variants
        elif any(term in title_lower for term in ['product manager', 'pm']):
            if 'senior' in title_lower or 'sr' in title_lower:
                return 'senior_product_manager'
            elif any(term in title_lower for term in ['principal', 'lead']):
                return 'principal_product_manager'
            else:
                return 'product_manager'

        # Data Scientist variants
        elif any(term in title_lower for term in ['data scientist', 'data science']):
            if 'senior' in title_lower or 'sr' in title_lower:
                return 'senior_data_scientist'
            else:
                return 'data_scientist'

        # DevOps Engineer variants
        elif any(term in title_lower for term in ['devops', 'dev ops', 'platform engineer', 'sre']):
            return 'devops_engineer'

        # UX/UI Designer variants
        elif any(term in title_lower for term in ['ux designer', 'ui designer', 'product designer', 'ui/ux']):
            return 'ux_designer'

        # Backend/Frontend Engineer variants
        elif 'backend' in title_lower or 'back end' in title_lower:
            return 'backend_engineer'
        elif 'frontend' in title_lower or 'front end' in title_lower:
            return 'frontend_engineer'

        # Full Stack Engineer
        elif any(term in title_lower for term in ['full stack', 'fullstack']):
            return 'fullstack_engineer'

        # Default: normalize spaces and special chars
        normalized = title_lower.replace(' ', '_').replace('-', '_').replace('/', '_')
        normalized = normalized.replace(',', '_').replace('.', '_')
        # Remove multiple underscores
        while '__' in normalized:
            normalized = normalized.replace('__', '_')
        # Remove leading/trailing underscores
        normalized = normalized.strip('_')

        return normalized[:50]  # Limit length

    def _get_location_tier(self, location: str) -> str:
        """
        Get location tier for cost-of-living calculations
        """
        if not location:
            return 'tier3'

        location_lower = location.lower()

        # Tier 1: Highest cost of living
        tier1_cities = [
            'san francisco', 'sf', 'bay area', 'silicon valley', 'palo alto',
            'new york', 'nyc', 'manhattan', 'brooklyn', 'seattle',
            'los angeles', 'la', 'santa monica', 'boston',
            'washington dc', 'dc', 'san diego'
        ]

        # Tier 2: Medium-high cost of living
        tier2_cities = [
            'austin', 'denver', 'portland', 'chicago', 'miami',
            'philadelphia', 'atlanta', 'dallas', 'houston',
            'minneapolis', 'phoenix', 'salt lake city', 'raleigh'
        ]

        # Check for remote
        if any(term in location_lower for term in ['remote', 'work from home', 'wfh']):
            return 'remote'

        # Check tiers
        if any(city in location_lower for city in tier1_cities):
            return 'tier1'
        elif any(city in location_lower for city in tier2_cities):
            return 'tier2'
        else:
            return 'tier3'

    def _get_company_tier(self, company: str) -> str:
        """
        Determine company tier based on company name
        """
        if not company:
            return 'Unknown'

        company_lower = company.lower()

        # FAANG/Big Tech
        faang = ['google', 'alphabet', 'amazon', 'meta', 'facebook', 'apple', 'netflix', 'microsoft']

        # Top Tech Companies
        top_tech = [
            'uber', 'lyft', 'airbnb', 'spotify', 'twitter', 'linkedin',
            'salesforce', 'oracle', 'adobe', 'intuit', 'paypal', 'square',
            'stripe', 'coinbase', 'discord', 'slack', 'zoom', 'tiktok'
        ]

        # Well-funded startups
        startup_tech = [
            'stripe', 'plaid', 'robinhood', 'databricks', 'snowflake',
            'ui path', 'automation anywhere', 'freshworks', 'postman'
        ]

        if any(f in company_lower for f in faang):
            return 'FAANG'
        elif any(t in company_lower for t in top_tech):
            return 'Top Tech'
        elif any(s in company_lower for s in startup_tech):
            return 'Startup'
        else:
            return 'Standard'