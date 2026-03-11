"""
Job Service - Scrape and parse job descriptions
Handles URLs from LinkedIn, Indeed, and plain text
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional
import re


class JobService:
    """Handle job description scraping and parsing"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def get_job_description(
        self,
        job_url: Optional[str] = None,
        job_text: Optional[str] = None
    ) -> str:
        """
        Get job description from URL or text
        
        Args:
            job_url: URL to job posting
            job_text: Plain text job description
            
        Returns:
            Job description text
        """
        
        if job_text:
            # User provided text directly
            return job_text.strip()
        
        if job_url:
            # Scrape from URL
            return await self.scrape_job(job_url)
        
        raise ValueError("Must provide either job_url or job_text")
    
    async def scrape_job(self, url: str) -> str:
        """
        Scrape job description from URL
        Handles LinkedIn, Indeed, and generic sites
        """
        
        try:
            # Make request
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to identify job site and use specific parsing
            if 'linkedin.com' in url:
                return self._parse_linkedin(soup)
            elif 'indeed.com' in url:
                return self._parse_indeed(soup)
            elif 'greenhouse.io' in url:
                return self._parse_greenhouse(soup)
            else:
                return self._parse_generic(soup)
                
        except requests.Timeout:
            raise ValueError("Request timed out. The job site took too long to respond.")
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch job posting: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse job posting: {str(e)}")
    
    def _parse_linkedin(self, soup: BeautifulSoup) -> str:
        """Parse LinkedIn job posting"""
        # LinkedIn specific selectors (these may change over time)
        
        # Try multiple selectors
        selectors = [
            {'class': 'description__text'},
            {'class': 'show-more-less-html__markup'},
            {'id': 'job-details'}
        ]
        
        for selector in selectors:
            content = soup.find('div', selector)
            if content:
                return self._clean_html_text(content.get_text())
        
        # Fallback to generic parsing
        return self._parse_generic(soup)
    
    def _parse_indeed(self, soup: BeautifulSoup) -> str:
        """Parse Indeed job posting"""
        # Indeed specific selectors
        
        selectors = [
            {'id': 'jobDescriptionText'},
            {'class': 'jobsearch-jobDescriptionText'}
        ]
        
        for selector in selectors:
            content = soup.find('div', selector)
            if content:
                return self._clean_html_text(content.get_text())
        
        return self._parse_generic(soup)
    
    def _parse_greenhouse(self, soup: BeautifulSoup) -> str:
        """Parse Greenhouse job posting"""
        content = soup.find('div', {'id': 'content'})
        if content:
            return self._clean_html_text(content.get_text())
        
        return self._parse_generic(soup)
    
    def _parse_generic(self, soup: BeautifulSoup) -> str:
        """
        Generic HTML parser for unknown job sites
        Tries to extract main content
        """
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer']):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up
        text = self._clean_html_text(text)
        
        if len(text) < 100:
            raise ValueError(
                "Could not extract enough text from the page. "
                "This site may not be supported. "
                "Please copy-paste the job description instead."
            )
        
        return text
    
    def _clean_html_text(self, text: str) -> str:
        """Clean up extracted HTML text"""
        # Remove extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove common noise
        noise_patterns = [
            r'Share\s*Save',
            r'Apply\s*Now',
            r'Easy\s*Apply',
            r'Sign\s*in',
            r'Cookie\s*Policy',
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def extract_key_requirements(self, job_description: str) -> dict:
        """
        Extract key requirements from job description
        Used for focused analysis
        """
        
        requirements = {
            "required_skills": [],
            "preferred_skills": [],
            "experience_years": None,
            "education": [],
            "responsibilities": []
        }
        
        # Simple keyword extraction (can be improved with NLP)
        lines = job_description.lower().split('\n')
        
        current_section = None
        for line in lines:
            # Detect sections
            if 'requirement' in line or 'qualification' in line:
                current_section = 'required'
            elif 'preferred' in line or 'nice to have' in line:
                current_section = 'preferred'
            elif 'responsibilit' in line:
                current_section = 'responsibilities'
            
            # Extract years of experience
            years_match = re.search(r'(\d+)\+?\s*years?', line)
            if years_match:
                requirements['experience_years'] = int(years_match.group(1))
            
            # Extract skills (simple approach)
            if current_section == 'required' and any(char in line for char in ['•', '-', '*']):
                skill = line.strip('•-* ').strip()
                if skill:
                    requirements['required_skills'].append(skill)
            elif current_section == 'preferred' and any(char in line for char in ['•', '-', '*']):
                skill = line.strip('•-* ').strip()
                if skill:
                    requirements['preferred_skills'].append(skill)
        
        return requirements


# Singleton
_job_service: Optional[JobService] = None


def get_job_service() -> JobService:
    """Get job service instance"""
    global _job_service
    if _job_service is None:
        _job_service = JobService()
    return _job_service