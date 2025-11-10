import google.generativeai as genai
from typing import Dict, List
import os
import logging
from .market_data import MarketDataService
from .umk_data import get_umk_for_location, calculate_umk_compliance

logger = logging.getLogger(__name__)

class SalaryAnalyzer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.market_service = MarketDataService()

    async def analyze_offer(self, offer_data: Dict) -> Dict:
        """
        Comprehensive analysis of job offer using AI and market data
        """
        try:
            logger.info(f"Analyzing offer for {offer_data.get('job_title', 'Unknown position')}")

            # Get market data
            market_data = await self.market_service.get_market_data(
                job_title=offer_data.get('job_title', ''),
                location=offer_data.get('location', ''),
                years_experience=offer_data.get('years_experience', 0),
                tech_stack=offer_data.get('tech_stack', [])
            )

            # Calculate total compensation
            total_comp = self._calculate_total_comp(offer_data)

            # Check UMK compliance
            umk_data = get_umk_for_location(offer_data.get('location', ''))
            umk_compliance = calculate_umk_compliance(
                offer_data.get('base_salary', 0),
                umk_data
            )

            # Determine verdict (consider UMK compliance)
            verdict = self._determine_verdict_umk(total_comp, market_data, umk_compliance)

            # Generate AI analysis using Gemini
            ai_analysis = await self._generate_ai_analysis(
                offer_data,
                market_data,
                verdict,
                umk_compliance
            )

            analysis_result = {
                'offer_data': offer_data,
                'market_data': market_data,
                'total_compensation': total_comp,
                'verdict': verdict,
                'analysis': ai_analysis,
                'negotiation_room': self._calculate_negotiation_room(
                    total_comp,
                    market_data
                ),
                'leverage_points': self._extract_leverage_points(
                    offer_data,
                    market_data
                ),
                'recommendations': await self._generate_recommendations(
                    offer_data,
                    market_data,
                    verdict
                ),
                'umk_data': umk_data,
                'umk_compliance': umk_compliance
            }

            logger.info(f"Analysis complete. Verdict: {verdict}, Total comp: Rp {total_comp:,}".replace(',', '.'))
            return analysis_result

        except Exception as e:
            logger.error(f"Error analyzing offer: {str(e)}")
            raise ValueError(f"Failed to analyze offer: {str(e)}")

    def _calculate_total_comp(self, offer_data: Dict) -> int:
        """
        Calculate total annual compensation
        """
        base = offer_data.get('base_salary', 0) or 0
        bonus = offer_data.get('bonus', 0) or 0
        equity = offer_data.get('equity_value', 0) or 0

        return base + bonus + equity

    def _determine_verdict(self, total_comp: int, market_data: Dict) -> str:
        """
        Determine if offer is competitive based on market data
        """
        p25 = market_data.get('p25', 0) or 0
        p50 = market_data.get('p50', 0) or 0
        p75 = market_data.get('p75', 0) or 0
        p90 = market_data.get('p90', 0) or 0

        # If no market data, use default ranges
        if p50 == 0:
            if total_comp < 70000:
                return "SIGNIFICANTLY_UNDERPAID"
            elif total_comp < 90000:
                return "UNDERPAID"
            elif total_comp < 120000:
                return "FAIR"
            elif total_comp < 150000:
                return "COMPETITIVE"
            else:
                return "EXCELLENT"

        if total_comp < p25:
            return "SIGNIFICANTLY_UNDERPAID"
        elif total_comp < p50:
            return "UNDERPAID"
        elif total_comp < p75:
            return "FAIR"
        elif total_comp < p90:
            return "COMPETITIVE"
        else:
            return "EXCELLENT"

    def _determine_verdict_umk(self, total_comp: int, market_data: Dict, umk_compliance: Dict) -> str:
        """
        Determine verdict considering UMK compliance
        """
        # If offer is below UMK, immediately mark as problematic
        if umk_compliance and not umk_compliance['complies']:
            return "BELOW_UMK"

        # Otherwise use original market-based verdict
        return self._determine_verdict(total_comp, market_data)

    async def _generate_ai_analysis(
        self,
        offer_data: Dict,
        market_data: Dict,
        verdict: str,
        umk_compliance: Dict
    ) -> str:
        """
        Generate detailed AI analysis using Gemini
        """
        try:
            company_tier = self._get_company_tier(offer_data.get('company', ''))

            prompt = f"""
You are an expert tech compensation analyst and career coach. Analyze this job offer comprehensively and provide actionable insights.

**Offer Details:**
- Position: {offer_data.get('job_title', 'Not specified')}
- Company: {offer_data.get('company', 'Not specified')} ({company_tier})
- Location: {offer_data.get('location', 'Not specified')}
- Base Salary: ${offer_data.get('base_salary', 0):,}
- Bonus: ${offer_data.get('bonus', 0):,}
- Equity: {offer_data.get('equity', 'Not specified')}
- Years of Experience: {offer_data.get('years_experience', 'Not specified')}
- Tech Stack: {', '.join(offer_data.get('tech_stack', []))}

**Market Data:**
- Market P25: ${market_data.get('p25', 0):,}
- Market P50 (median): ${market_data.get('p50', 0):,}
- Market P75: ${market_data.get('p75', 0):,}
- Market P90: ${market_data.get('p90', 0):,}
- Sample Size: {market_data.get('sample_size', 0)} data points
- Data Confidence: {market_data.get('confidence', 'unknown')}

**UMK (Upah Minimum) Compliance:**
- Location UMK: {umk_compliance.get('umk_amount_formatted', 'N/A')}
- Offer vs UMK: {umk_compliance.get('message', 'Not available')}
- UMK Status: {'✅ COMPLIES' if umk_compliance.get('complies') else '❌ BELOW MINIMUM'}

**Assessment: {verdict}**

Provide a detailed analysis covering these specific sections:

1. **OVERALL ASSESSMENT**
   - Is this offer competitive? Why or why not?
   - How does it compare to market rates?

2. **STRENGTHS**
   - What are the strong points of this offer?
   - Any standout benefits or opportunities?

3. **AREAS OF CONCERN**
   - What are potential red flags or weak points?
   - Where does this offer fall short?

4. **MARKET POSITIONING**
   - Percentile ranking (bottom 25%, 25-50%, 50-75%, top 25%)
   - How does experience level affect this assessment?

5. **NEGOTIATION LEVERAGE**
   - What specific points can be used to negotiate?
   - Market-based arguments you can make

6. **NON-SALARY OPPORTUNITIES**
   - What else could be negotiated besides base salary?
   - Benefits, perks, sign-on bonuses, equity adjustments

7. **RISK ASSESSMENT**
   - Any risks with this offer (company stability, equity value, etc.)?
   - Long-term career implications

Be specific, data-driven, and provide actionable advice. Use clear section headers. Format your response professionally with specific numbers and recommendations.
"""

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"AI analysis generation failed: {str(e)}")
            return self._get_fallback_analysis(offer_data, market_data, verdict)

    def _get_fallback_analysis(self, offer_data: Dict, market_data: Dict, verdict: str) -> str:
        """
        Fallback analysis when AI generation fails
        """
        total_comp = self._calculate_total_comp(offer_data)
        p50 = market_data.get('p50', 0) or total_comp

        analysis = f"""**OVERALL ASSESSMENT**
This offer is classified as {verdict.replace('_', ' ').title()}.

**COMPENSATION BREAKDOWN**
- Base Salary: ${offer_data.get('base_salary', 0):,}
- Bonus: ${offer_data.get('bonus', 0):,}
- Equity: ${offer_data.get('equity_value', 0):,}
- Total Compensation: ${total_comp:,}

**MARKET COMPARISON**
- Market Median (P50): ${p50:,}
- Your Position: {((total_comp / p50 - 1) * 100):+.1f}% from market median

**RECOMMENDATIONS**
- This offer appears to be in the {verdict.replace('_', ' ')} range
- Consider negotiating based on market data
- Focus on total compensation package
"""

        return analysis

    def _calculate_negotiation_room(
        self,
        current_comp: int,
        market_data: Dict
    ) -> Dict:
        """
        Calculate realistic negotiation targets
        """
        if current_comp == 0:
            return {
                'conservative': 0,
                'realistic': 0,
                'aggressive': 0,
                'percentage_increase': {'conservative': 0, 'realistic': 0, 'aggressive': 0}
            }

        p75 = market_data.get('p75', current_comp * 1.1) or current_comp * 1.1
        p90 = market_data.get('p90', current_comp * 1.2) or current_comp * 1.2

        # Conservative target: 5% increase or P75, whichever is higher
        conservative = max(current_comp * 1.05, p75)

        # Aggressive target: P90
        aggressive = p90

        # Realistic target: midpoint
        realistic = (conservative + aggressive) / 2

        return {
            'conservative': int(conservative),
            'realistic': int(realistic),
            'aggressive': int(aggressive),
            'percentage_increase': {
                'conservative': round(((conservative / current_comp) - 1) * 100, 1),
                'realistic': round(((realistic / current_comp) - 1) * 100, 1),
                'aggressive': round(((aggressive / current_comp) - 1) * 100, 1)
            }
        }

    def _extract_leverage_points(
        self,
        offer_data: Dict,
        market_data: Dict
    ) -> List[Dict]:
        """
        Extract specific leverage points for negotiation
        """
        leverage_points = []

        # Market data leverage
        p50 = market_data.get('p50', 0)
        current_base = offer_data.get('base_salary', 0) or 0

        if p50 > current_base:
            difference = p50 - current_base
            leverage_points.append({
                'type': 'market_rate',
                'description': f"Market median base salary is ${difference:,} higher",
                'strength': 'strong'
            })

        # Tech stack premium
        hot_tech = [
            'rust', 'golang', 'kubernetes', 'ai', 'ml', 'blockchain',
            'tensorflow', 'pytorch', 'aws', 'azure', 'gcp'
        ]
        user_tech = [tech.lower() for tech in offer_data.get('tech_stack', [])]

        matching_hot_tech = [tech for tech in hot_tech if tech in user_tech]
        if matching_hot_tech:
            leverage_points.append({
                'type': 'tech_premium',
                'description': f"Specialized in high-demand technologies: {', '.join(matching_hot_tech[:3])}",
                'strength': 'medium' if len(matching_hot_tech) < 3 else 'strong'
            })

        # Experience leverage
        years_exp = offer_data.get('years_experience', 0)
        if years_exp >= 10:
            leverage_points.append({
                'type': 'experience',
                'description': f"{years_exp}+ years of extensive experience",
                'strength': 'strong'
            })
        elif years_exp >= 5:
            leverage_points.append({
                'type': 'experience',
                'description': f"{years_exp}+ years of solid experience",
                'strength': 'medium'
            })

        # Missing equity/bonus leverage
        if not offer_data.get('equity_value') and offer_data.get('company'):
            leverage_points.append({
                'type': 'missing_equity',
                'description': "No equity component in current offer",
                'strength': 'medium'
            })

        if not offer_data.get('bonus') and offer_data.get('base_salary', 0) > 80000:
            leverage_points.append({
                'type': 'missing_bonus',
                'description': "No performance bonus structure",
                'strength': 'weak'
            })

        # Competing offers
        if offer_data.get('has_competing_offers'):
            leverage_points.append({
                'type': 'competition',
                'description': "Multiple offers in hand provides leverage",
                'strength': 'strong'
            })

        return leverage_points

    async def _generate_recommendations(
        self,
        offer_data: Dict,
        market_data: Dict,
        verdict: str
    ) -> List[Dict]:
        """
        Generate actionable recommendations based on analysis
        """
        recommendations = []

        # High priority recommendations
        if verdict in ['SIGNIFICANTLY_UNDERPAID', 'UNDERPAID']:
            recommendations.append({
                'priority': 'high',
                'action': 'negotiate_base',
                'description': 'Base salary is below market rates - negotiate for market alignment',
                'target': market_data.get('p75')
            })

        if not offer_data.get('equity_value'):
            recommendations.append({
                'priority': 'medium',
                'action': 'clarify_equity',
                'description': 'Request equity grant details and valuation',
                'target': None
            })

        if not offer_data.get('bonus') and offer_data.get('base_salary', 0) > 75000:
            recommendations.append({
                'priority': 'medium',
                'action': 'negotiate_bonus',
                'description': 'Negotiate performance bonus or sign-on bonus',
                'target': int(offer_data.get('base_salary', 0) * 0.15)
            })

        # Benefits recommendations
        if not offer_data.get('benefits'):
            recommendations.append({
                'priority': 'low',
                'action': 'review_benefits',
                'description': 'Review and negotiate comprehensive benefits package',
                'target': None
            })

        # Always add research recommendation
        recommendations.append({
            'priority': 'low',
            'action': 'continue_research',
            'description': 'Continue researching market rates and company culture',
            'target': None
        })

        return recommendations

    def _get_company_tier(self, company: str) -> str:
        """
        Determine company tier for context in analysis
        """
        if not company:
            return 'Unknown'

        faang = ['google', 'alphabet', 'amazon', 'meta', 'facebook', 'apple', 'netflix', 'microsoft']
        top_tech = ['uber', 'lyft', 'airbnb', 'spotify', 'twitter', 'linkedin', 'salesforce', 'oracle', 'adobe']

        company_lower = company.lower()

        if any(f in company_lower for f in faang):
            return 'FAANG/Big Tech'
        elif any(t in company_lower for t in top_tech):
            return 'Top Tech'
        else:
            return 'Standard'