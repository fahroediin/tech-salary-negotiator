import google.generativeai as genai
import os
import re
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class NegotiationScriptGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    async def generate_scripts(
        self,
        analysis_result: Dict,
        user_profile: Dict
    ) -> Dict:
        """
        Generate personalized negotiation email templates using Gemini
        """
        try:
            logger.info("Generating negotiation scripts")

            offer = analysis_result['offer_data']
            market = analysis_result['market_data']
            verdict = analysis_result['verdict']
            target_salary = analysis_result['negotiation_room']['realistic']

            prompt = self._build_prompt(
                offer, market, verdict, target_salary, user_profile
            )

            response = self.model.generate_content(prompt)
            scripts_text = response.text.strip()

            # Parse the three scripts
            scripts = self._parse_scripts(scripts_text)

            # Generate additional tips
            tips = await self._generate_negotiation_tips(analysis_result)

            result = {
                'assertive': scripts.get('assertive', ''),
                'balanced': scripts.get('balanced', ''),
                'humble': scripts.get('humble', ''),
                'tips': tips,
                'talking_points': self._generate_talking_points(analysis_result)
            }

            logger.info("Successfully generated negotiation scripts")
            return result

        except Exception as e:
            logger.error(f"Error generating scripts: {str(e)}")
            # Return fallback scripts
            return self._get_fallback_scripts(analysis_result, user_profile)

    def _build_prompt(
        self,
        offer: Dict,
        market: Dict,
        verdict: str,
        target_salary: int,
        user_profile: Dict
    ) -> str:
        """
        Build comprehensive prompt for script generation
        """
        current_base = offer.get('base_salary', 0)
        current_bonus = offer.get('bonus', 0)
        current_equity = offer.get('equity', 'Not specified')

        return f"""
You are an expert salary negotiation coach. Generate 3 professional negotiation email templates for this tech job offer.

**CURRENT OFFER DETAILS:**
- Position: {offer.get('job_title', 'Senior Software Engineer')}
- Company: {offer.get('company', 'Tech Company')}
- Location: {offer.get('location', 'San Francisco, CA')}
- Current Base Salary: ${current_base:,}
- Current Bonus: ${current_bonus:,}
- Current Equity: {current_equity}

**MARKET DATA:**
- Market Median (P50): ${market.get('p50', 0):,}
- Market P75: ${market.get('p75', 0):,}
- Market P90: ${market.get('p90', 0):,}
- Sample Size: {market.get('sample_size', 0)} data points
- Market Assessment: {verdict}

**CANDIDATE PROFILE:**
- Years of Experience: {user_profile.get('years_experience', 'Not specified')}
- Current/Previous Salary: ${user_profile.get('current_salary', 0):,}
- Key Skills: {', '.join(user_profile.get('tech_stack', []))}
- Has Competing Offers: {user_profile.get('has_competing_offers', False)}

**NEGOTIATION TARGET:**
- Target Total Compensation: ${target_salary:,}

Generate 3 distinct email templates with these negotiation styles:

**1. ASSERTIVE TEMPLATE** (Strong negotiating position)
- Confident and direct tone
- Clear data-driven justification
- Asks for market rates or higher
- Emphasizes value and market fit
- Higher target number (closer to P90)

**2. BALANCED TEMPLATE** (Standard professional negotiation)
- Professional, friendly, and respectful
- Balanced approach with solid reasoning
- Reasonable ask aligned with market data
- Win-win mindset
- Target number around P75

**3. HUMBLE TEMPLATE** (Weaker position or early career)
- Grateful and enthusiastic tone
- Gentle and respectful ask
- Lower, more reasonable target
- Focuses on learning and growth
- Target around P60-P70

**REQUIREMENTS FOR EACH TEMPLATE:**

Each template must include:
1. **Professional subject line** that gets opened
2. **Enthusiastic opening** expressing genuine interest
3. **Clear gratitude** for the opportunity
4. **Data-driven justification** referencing market rates
5. **Specific compensation request** with clear numbers
6. **Flexibility statement** showing willingness to discuss
7. **Professional closing** that maintains relationship
8. **Length**: 150-250 words

**FORMAT GUIDELINES:**
- Write each template as a complete email
- Include "Subject:" line
- Use professional but approachable language
- Make each template distinct in tone and approach
- Reference specific market data
- Keep company and position details consistent

**SEPARATION:**
Separate each template with exactly: "---TEMPLATE BREAK---"

Generate compelling, realistic templates that candidates can actually use.
"""

    def _parse_scripts(self, text: str) -> Dict:
        """
        Parse the three templates from AI response
        """
        scripts = {}

        # Split by template separator
        parts = re.split(r'-{3,}TEMPLATE\s*BREAK-{3,}', text, flags=re.IGNORECASE)

        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue

            # Determine script type based on position or content
            if i == 0 or 'ASSERTIVE' in part.upper() or any(word in part.upper()[:200] for word in ['CONFIDENT', 'STRONG', 'DIRECT']):
                scripts['assertive'] = self._extract_template(part)
            elif i == 1 or 'BALANCED' in part.upper() or any(word in part.upper()[:200] for word in ['BALANCED', 'REASONABLE', 'FAIR']):
                scripts['balanced'] = self._extract_template(part)
            elif i == 2 or 'HUMBLE' in part.upper() or any(word in part.upper()[:200] for word in ['HUMBLE', 'GRATEFUL', 'RESPECTFUL']):
                scripts['humble'] = self._extract_template(part)
            elif 'assertive' not in scripts:
                scripts['assertive'] = self._extract_template(part)
            elif 'balanced' not in scripts:
                scripts['balanced'] = self._extract_template(part)
            elif 'humble' not in scripts:
                scripts['humble'] = self._extract_template(part)

        # Ensure we have all three scripts
        for script_type in ['assertive', 'balanced', 'humble']:
            if script_type not in scripts:
                scripts[script_type] = self._generate_basic_template(script_type)

        return scripts

    def _extract_template(self, text: str) -> str:
        """
        Extract clean template from text
        """
        lines = text.split('\n')
        template_lines = []

        for i, line in enumerate(lines):
            line = line.strip()

            # Skip numbering or headers that aren't part of email
            if i < 5 and (re.match(r'^\d+\.', line) or line.upper() in ['ASSERTIVE', 'BALANCED', 'HUMBLE']):
                continue

            # Look for actual email content
            if line and not line.startswith('Subject:') and not line.startswith('**'):
                template_lines.append(line)
            elif line.startswith('Subject:'):
                template_lines.append(line)
                # Add the rest of the lines after finding Subject
                template_lines.extend([l for l in lines[i+1:] if l.strip()])
                break

        # Join and clean up
        template = '\n'.join(template_lines)

        # Remove any remaining markdown or formatting
        template = re.sub(r'\*\*(.*?)\*\*', r'\1', template)  # Bold
        template = re.sub(r'\*(.*?)\*', r'\1', template)      # Italic
        template = re.sub(r'_{2,}(.*?)_{2,}', r'\1', template) # Underline

        return template.strip()

    def _generate_basic_template(self, script_type: str) -> str:
        """
        Generate a basic template as fallback
        """
        templates = {
            'assertive': '''Subject: Following up on the {job_title} offer

Dear Hiring Manager,

Thank you for extending the offer for the {job_title} position. I'm very excited about the opportunity to join {company} and contribute to your team.

After reviewing the compensation package and researching market rates for similar positions in {location}, I'd like to discuss the base salary. Based on my {years_experience} years of experience and expertise in {tech_stack}, I'm confident in bringing significant value to your team.

Would you be open to adjusting the base salary to be more aligned with market rates, around ${target_base}? I believe this would better reflect the value and experience I bring to the role.

I'm very enthusiastic about this opportunity and believe we can find a compensation package that works for both of us.

Best regards,
[Your Name]''',

            'balanced': '''Subject: Quick question about the {job_title} offer

Dear Hiring Manager,

Thank you so much for the offer for the {job_title} position at {company}! I'm really excited about the possibility of joining your team.

I've had a chance to review the compensation details, and I wanted to discuss the salary component. Based on my research of market rates for similar roles in {location} and considering my experience with {tech_stack}, I was hoping we could discuss a base salary closer to ${target_base}.

I'm very flexible and would love to find a package that works for both of us. Would you be open to having a conversation about this?

Looking forward to hearing from you!

Best regards,
[Your Name]''',

            'humble': '''Subject: Thank you for the {job_title} offer!

Dear Hiring Manager,

Thank you so much for the generous offer for the {job_title} position! I'm truly honored and excited about the opportunity to potentially join {company}.

I really appreciate the compensation package you've put together. I did want to gently ask if there might be any flexibility on the base salary. Based on market research for similar positions in {location}, I was wondering if we could possibly discuss a base salary closer to ${target_base}.

Of course, I understand if this isn't possible, and I'm grateful for the offer as presented. I'm really excited about this role regardless!

Thank you again for this wonderful opportunity.

Best regards,
[Your Name]'''
        }

        return templates.get(script_type, templates['balanced'])

    async def _generate_negotiation_tips(self, analysis_result: Dict) -> list:
        """
        Generate specific negotiation tips based on analysis
        """
        verdict = analysis_result['verdict']
        leverage_points = analysis_result.get('leverage_points', [])

        tips = [
            {
                'title': 'Do Your Research',
                'description': 'Have specific market data ready to justify your request.'
            },
            {
                'title': 'Be Specific',
                'description': f"Ask for a specific number (${analysis_result['negotiation_room']['realistic']:,}) rather than a range."
            },
            {
                'title': 'Stay Positive',
                'description': 'Express genuine enthusiasm while negotiating - companies want to hire people who want to be there.'
            },
            {
                'title': 'Consider Total Package',
                'description': 'If base salary is inflexible, negotiate bonus, equity, sign-on bonus, or benefits.'
            },
            {
                'title': 'Timing Matters',
                'description': 'Negotiate within 24-48 hours of receiving the offer while maintaining momentum.'
            },
            {
                'title': 'Have a Walkaway Point',
                'description': 'Know your minimum acceptable salary before entering negotiations.'
            }
        ]

        # Add specific tips based on leverage points
        for leverage in leverage_points:
            if leverage.get('type') == 'market_rate':
                tips.append({
                    'title': 'Leverage Market Data',
                    'description': 'Your offer is below market rates - use specific market percentiles to justify your ask.'
                })
            elif leverage.get('type') == 'competition':
                tips.append({
                    'title': 'Use Competing Offers',
                    'description': 'Mention other offers strategically to create urgency and demonstrate value.'
                })

        # Add verdict-specific tips
        if verdict in ['SIGNIFICANTLY_UNDERPAID', 'UNDERPAID']:
            tips.append({
                'title': 'Strong Negotiation Position',
                'description': 'Your offer is significantly below market - you have strong grounds for negotiation.'
            })
        elif verdict == 'EXCELLENT':
            tips.append({
                'title': 'Great Offer',
                'description': 'This is already an excellent offer - consider small adjustments or focus on non-salary benefits.'
            })

        return tips

    def _generate_talking_points(self, analysis_result: Dict) -> list:
        """
        Generate key talking points for negotiation conversations
        """
        talking_points = []
        market_data = analysis_result['market_data']
        leverage_points = analysis_result.get('leverage_points', [])

        # Market data points
        p50 = market_data.get('p50', 0)
        p75 = market_data.get('p75', 0)
        if p50:
            talking_points.append(f"Market median for this role is ${p50:,}")

        if p75:
            talking_points.append(f"Top 25% of the market earns ${p75:,}")

        # Experience points
        offer_data = analysis_result['offer_data']
        years_exp = offer_data.get('years_experience', 0)
        if years_exp >= 5:
            talking_points.append(f"{years_exp} years of relevant experience")

        # Tech stack points
        tech_stack = offer_data.get('tech_stack', [])
        if tech_stack:
            talking_points.append(f"Expertise in in-demand technologies: {', '.join(tech_stack[:3])}")

        # Leverage points
        for leverage in leverage_points:
            if leverage.get('strength') in ['strong', 'medium']:
                talking_points.append(leverage['description'])

        # Verdict-based points
        verdict = analysis_result['verdict']
        if 'UNDERPAID' in verdict:
            talking_points.append("Current offer is below market rates")

        return talking_points

    def _get_fallback_scripts(self, analysis_result: Dict, user_profile: Dict) -> Dict:
        """
        Generate fallback scripts when AI generation fails
        """
        offer = analysis_result.get('offer_data', {})
        negotiation_room = analysis_result.get('negotiation_room', {})
        target_salary = negotiation_room.get('realistic', 0)

        job_title = offer.get('job_title', 'Senior Software Engineer') or 'Senior Software Engineer'
        company = offer.get('company', 'the company') or 'the company'
        location = offer.get('location', 'this location') or 'this location'
        years_experience = user_profile.get('years_experience', '5') or '5'
        tech_stack = user_profile.get('tech_stack', ['relevant technologies']) or ['relevant technologies']
        target_base = int(target_salary * 0.8) if target_salary > 0 else 100000  # Estimate base salary portion

        try:
            return {
                'assertive': self._generate_basic_template('assertive').format(
                    job_title=job_title, company=company, location=location,
                    years_experience=years_experience, tech_stack=', '.join(tech_stack[:3]),
                    target_base=target_base
                ),
                'balanced': self._generate_basic_template('balanced').format(
                    job_title=job_title, company=company, location=location,
                    years_experience=years_experience, tech_stack=', '.join(tech_stack[:3]),
                    target_base=target_base
                ),
                'humble': self._generate_basic_template('humble').format(
                    job_title=job_title, company=company, location=location,
                    years_experience=years_experience, tech_stack=', '.join(tech_stack[:3]),
                    target_base=target_base
                ),
            'tips': [
                {'title': 'Be Prepared', 'description': 'Research market rates before negotiating.'},
                {'title': 'Stay Professional', 'description': 'Maintain positive relationships throughout the process.'},
                {'title': 'Consider Total Package', 'description': 'Look at salary, bonus, equity, and benefits together.'}
            ],
            'talking_points': [
                f"Market rate for this position is ${target_salary:,}",
                f"My experience deserves competitive compensation",
                "I'm excited about this opportunity and want to make it work"
            ]
        }
        except Exception as e:
            logger.error(f"Error formatting fallback scripts: {str(e)}")
            # Return basic scripts without formatting
            return {
                'assertive': 'Subject: Following up on the offer\n\nDear Hiring Manager,\n\nThank you for extending the offer. I would like to discuss the compensation package based on market research.\n\nBest regards,\n[Your Name]',
                'balanced': 'Subject: Quick question about the offer\n\nDear Hiring Manager,\n\nThank you for the offer. I was hoping we could discuss the compensation to better align with market rates.\n\nBest regards,\n[Your Name]',
                'humble': 'Subject: Thank you for the offer!\n\nDear Hiring Manager,\n\nI appreciate the offer. I was wondering if there might be any flexibility on the base salary?\n\nThank you,\n[Your Name]',
                'tips': [
                    {'title': 'Be Prepared', 'description': 'Research market rates before negotiating.'},
                    {'title': 'Stay Professional', 'description': 'Maintain positive relationships throughout the process.'}
                ],
                'talking_points': [
                    "Market research supports salary adjustment",
                    "Experience and skills deserve fair compensation",
                    "Excited about the opportunity"
                ]
            }