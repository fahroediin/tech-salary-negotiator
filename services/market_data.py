from typing import Dict, List
from sqlalchemy import text
from sqlalchemy.orm import Session
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

    async def get_market_data(
        self,
        job_title: str,
        location: str,
        years_experience: int,
        tech_stack: List[str]
    ) -> Dict:
        """
        Query salary database for market data based on job title, location, experience, and tech stack
        """
        try:
            # Normalize inputs
            normalized_title = self._normalize_job_title(job_title)
            location_tier = self._get_location_tier(location)
            col_multiplier = self._get_col_multiplier(location)

            logger.info(f"Getting market data for {normalized_title} in {location_tier} location")

            from database import SessionLocal

            # Connect to database
            db = SessionLocal()

            try:
                # Query market data with specific criteria
                query = text("""
                SELECT
                    percentile_cont(0.10) WITHIN GROUP (ORDER BY total_comp) as p10,
                    percentile_cont(0.25) WITHIN GROUP (ORDER BY total_comp) as p25,
                    percentile_cont(0.50) WITHIN GROUP (ORDER BY total_comp) as p50,
                    percentile_cont(0.75) WITHIN GROUP (ORDER BY total_comp) as p75,
                    percentile_cont(0.90) WITHIN GROUP (ORDER BY total_comp) as p90,
                    COUNT(*) as sample_size,
                    AVG(base_salary) as avg_base,
                    AVG(bonus) as avg_bonus,
                    AVG(equity_value) as avg_equity
                FROM salary_data
                WHERE
                    normalized_title = :normalized_title
                    AND years_experience BETWEEN :exp_min AND :exp_max
                    AND location_tier = :location_tier
                    AND submitted_date > :cutoff_date
                    AND is_verified = true
                """)

                cutoff_date = datetime.now() - timedelta(days=540)  # 18 months

                result = db.execute(query, {
                    'normalized_title': normalized_title,
                    'exp_min': years_experience - 2,
                    'exp_max': years_experience + 2,
                    'location_tier': location_tier,
                    'cutoff_date': cutoff_date
                }).fetchone()

                # Convert to dict format
                result_dict = dict(result) if result else {'sample_size': 0}

                # If not enough data, try fallback query
                if not result or result_dict['sample_size'] < 5:
                    logger.info(f"Insufficient specific data ({result_dict['sample_size']} samples), using fallback query")
                    result_dict = self._fallback_query(db, normalized_title, location_tier)

                # Calculate tech stack premium
                tech_premium = self._calculate_tech_stack_premium(tech_stack)

                # Adjust for cost of living and tech stack
                market_data = {
                    'p10': int(result_dict['p10'] * col_multiplier * tech_premium) if result_dict['p10'] else None,
                    'p25': int(result_dict['p25'] * col_multiplier * tech_premium) if result_dict['p25'] else None,
                    'p50': int(result_dict['p50'] * col_multiplier * tech_premium) if result_dict['p50'] else None,
                    'p75': int(result_dict['p75'] * col_multiplier * tech_premium) if result_dict['p75'] else None,
                    'p90': int(result_dict['p90'] * col_multiplier * tech_premium) if result_dict['p90'] else None,
                    'sample_size': result_dict['sample_size'],
                    'avg_base': int(result_dict['avg_base']) if result_dict['avg_base'] else None,
                    'avg_bonus': int(result_dict['avg_bonus']) if result_dict['avg_bonus'] else None,
                    'avg_equity': int(result_dict['avg_equity']) if result_dict['avg_equity'] else None,
                    'confidence': self._calculate_confidence(result_dict['sample_size']),
                    'data_freshness': 'recent' if result_dict['sample_size'] > 0 else 'limited'
                }

                logger.info(f"Market data retrieved: {result_dict['sample_size']} samples, confidence: {market_data['confidence']}")
                return market_data

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error getting market data: {str(e)}")
            # Return default market data on error
            return self._get_default_market_data()

    def _normalize_job_title(self, title: str) -> str:
        """
        Normalize job title to standard format for database queries
        """
        if not title:
            return 'unknown'

        title_lower = title.lower()

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
        elif any(term in title_lower for term in ['devops', 'dev ops', 'platform engineer']):
            return 'devops_engineer'

        # UX/UI Designer variants
        elif any(term in title_lower for term in ['ux designer', 'ui designer', 'product designer']):
            return 'ux_designer'

        # Default: lowercase and replace spaces/special chars
        normalized = title_lower.replace(' ', '_').replace('-', '_').replace('/', '_')
        # Remove multiple underscores
        while '__' in normalized:
            normalized = normalized.replace('__', '_')

        return normalized[:50]  # Limit length

    def _get_location_tier(self, location: str) -> str:
        """
        Categorize location into cost-of-living tiers
        """
        if not location:
            return 'tier3'

        location_lower = location.lower()

        # Tier 1: Highest cost of living
        tier1_cities = [
            'san francisco', 'sf', 'bay area', 'silicon valley', 'palo alto',
            'new york', 'nyc', 'manhattan', 'brooklyn',
            'seattle', 'los angeles', 'la', 'santa monica',
            'boston', 'washington dc', 'dc', 'san diego'
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

        # Check tier 1
        if any(city in location_lower for city in tier1_cities):
            return 'tier1'

        # Check tier 2
        if any(city in location_lower for city in tier2_cities):
            return 'tier2'

        # Default to tier 3
        return 'tier3'

    def _get_col_multiplier(self, location: str) -> float:
        """
        Get cost of living multiplier based on location
        """
        location_lower = location.lower() if location else ''

        col_multipliers = {
            # Tier 1 (Highest)
            'san francisco': 1.52, 'sf': 1.52, 'bay area': 1.52, 'silicon valley': 1.52,
            'new york': 1.48, 'nyc': 1.48, 'manhattan': 1.55,
            'seattle': 1.35, 'los angeles': 1.42, 'la': 1.42,
            'boston': 1.38, 'washington dc': 1.35, 'dc': 1.35,
            'san diego': 1.32,

            # Tier 2 (Medium-High)
            'austin': 1.18, 'denver': 1.15, 'portland': 1.12,
            'chicago': 1.08, 'miami': 1.10, 'philadelphia': 1.05,
            'atlanta': 1.03, 'dallas': 1.04, 'houston': 1.02,

            # Remote
            'remote': 1.00, 'work from home': 1.00, 'wfh': 1.00
        }

        for city, multiplier in col_multipliers.items():
            if city in location_lower:
                return multiplier

        # Default multiplier based on tier
        tier = self._get_location_tier(location)
        tier_multipliers = {
            'tier1': 1.4,
            'tier2': 1.1,
            'tier3': 1.0,
            'remote': 1.0
        }

        return tier_multipliers.get(tier, 1.0)

    def _calculate_tech_stack_premium(self, tech_stack: List[str]) -> float:
        """
        Calculate premium multiplier for in-demand technologies
        """
        if not tech_stack:
            return 1.0

        premium_tech = {
            # AI/ML (highest premium)
            'rust': 1.20, 'golang': 1.15, 'go': 1.15,
            'kubernetes': 1.18, 'k8s': 1.18, 'docker': 1.08,
            'ai': 1.25, 'ml': 1.25, 'machine learning': 1.25,
            'deep learning': 1.28, 'tensorflow': 1.22, 'pytorch': 1.22,

            # Cloud & Infrastructure
            'aws': 1.12, 'azure': 1.10, 'gcp': 1.15,
            'terraform': 1.15, 'ansible': 1.10,

            # Modern Frameworks
            'react': 1.08, 'vue': 1.06, 'angular': 1.05,
            'nodejs': 1.10, 'typescript': 1.12,

            # Data & Analytics
            'spark': 1.18, 'hadoop': 1.15, 'snowflake': 1.20,
            'tableau': 1.10, 'looker': 1.08,

            # Security
            'cryptography': 1.15, 'security': 1.12,

            # Blockchain
            'blockchain': 1.20, 'ethereum': 1.18, 'solidity': 1.22,

            # Mobile
            'react native': 1.12, 'flutter': 1.15, 'swift': 1.10
        }

        tech_stack_lower = [tech.lower() for tech in tech_stack]
        premiums = []

        for tech in tech_stack_lower:
            # Check for exact matches first
            premium = premium_tech.get(tech)
            if premium:
                premiums.append(premium)
                continue

            # Check for partial matches
            for premium_tech_name, premium_value in premium_tech.items():
                if premium_tech_name in tech or tech in premium_tech_name:
                    premiums.append(premium_value)
                    break

        if not premiums:
            return 1.0

        # Use the maximum premium for any matching tech, but don't exceed reasonable limits
        max_premium = max(premiums)
        return min(max_premium, 1.35)  # Cap at 35% premium

    def _calculate_confidence(self, sample_size: int) -> str:
        """
        Calculate confidence level based on sample size
        """
        if sample_size >= 100:
            return 'high'
        elif sample_size >= 30:
            return 'medium'
        elif sample_size >= 10:
            return 'low'
        else:
            return 'very_low'

    def _fallback_query(self, db: Session, normalized_title: str, location_tier: str):
        """
        Fallback query with broader criteria when specific data is limited
        """
        try:
            # Try with broader experience range and all locations
            query = text("""
            SELECT
                percentile_cont(0.25) WITHIN GROUP (ORDER BY total_comp) as p25,
                percentile_cont(0.50) WITHIN GROUP (ORDER BY total_comp) as p50,
                percentile_cont(0.75) WITHIN GROUP (ORDER BY total_comp) as p75,
                percentile_cont(0.90) WITHIN GROUP (ORDER BY total_comp) as p90,
                COUNT(*) as sample_size,
                AVG(base_salary) as avg_base,
                AVG(bonus) as avg_bonus,
                AVG(equity_value) as avg_equity
            FROM salary_data
            WHERE
                normalized_title = :normalized_title
                AND is_verified = true
                AND submitted_date > :cutoff_date
            """)

            cutoff_date = datetime.now() - timedelta(days=730)  # 2 years

            result = db.execute(query, {
                'normalized_title': normalized_title,
                'cutoff_date': cutoff_date
            }).fetchone()

            result_dict = dict(result) if result else {'sample_size': 0}

            if result_dict['sample_size'] >= 5:
                return result_dict

            # If still not enough data, try even broader query
            broader_query = text("""
            SELECT
                percentile_cont(0.25) WITHIN GROUP (ORDER BY total_comp) as p25,
                percentile_cont(0.50) WITHIN GROUP (ORDER BY total_comp) as p50,
                percentile_cont(0.75) WITHIN GROUP (ORDER BY total_comp) as p75,
                percentile_cont(0.90) WITHIN GROUP (ORDER BY total_comp) as p90,
                COUNT(*) as sample_size,
                AVG(base_salary) as avg_base,
                AVG(bonus) as avg_bonus,
                AVG(equity_value) as avg_equity
            FROM salary_data
            WHERE
                is_verified = true
                AND submitted_date > :cutoff_date
            """)

            result = db.execute(broader_query, {
                'cutoff_date': cutoff_date
            }).fetchone()

            return dict(result) if result else {
                'p25': None, 'p50': None, 'p75': None, 'p90': None,
                'sample_size': 0, 'avg_base': None, 'avg_bonus': None, 'avg_equity': None
            }

        except Exception as e:
            logger.error(f"Fallback query failed: {str(e)}")
            # Return empty result with sample_size 0
            return {
                'p25': None, 'p50': None, 'p75': None, 'p90': None,
                'sample_size': 0, 'avg_base': None, 'avg_bonus': None, 'avg_equity': None
            }

    def _get_default_market_data(self) -> Dict:
        """
        Return default market data when database queries fail
        """
        return {
            'p10': 60000,
            'p25': 75000,
            'p50': 95000,
            'p75': 120000,
            'p90': 150000,
            'sample_size': 0,
            'avg_base': 95000,
            'avg_bonus': 10000,
            'avg_equity': 5000,
            'confidence': 'very_low',
            'data_freshness': 'estimated'
        }