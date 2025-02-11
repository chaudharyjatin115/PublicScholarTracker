from typing import List, Dict
from models import PublicServant, Politician, SessionLocal
from scrapers.government_scraper import GovernmentDataScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIntegrator:
    def __init__(self):
        self.scraper = GovernmentDataScraper()
        
    def import_politicians(self):
        """Import politician data from scraper to database"""
        db = SessionLocal()
        try:
            # Fetch data from scraper
            politician_data = self.scraper.scrape_mp_data()
            
            # Process and insert each politician
            for data in politician_data:
                education_info = data.pop('education_info', {})
                politician = Politician(
                    name=data['name'],
                    party=data['party'],
                    position=data['position'],
                    education_location=education_info.get('education_location', 'India'),
                    university=education_info.get('university', 'Unknown'),
                    degree_level=education_info.get('degree_level', 'Unknown')
                )
                db.add(politician)
                logger.info(f"Added politician: {data['name']}")
            
            db.commit()
            return len(politician_data)
        except Exception as e:
            db.rollback()
            logger.error(f"Error importing politicians: {str(e)}")
            raise
        finally:
            db.close()
    
    def import_civil_servants(self):
        """Import civil servant data from scraper to database"""
        db = SessionLocal()
        try:
            # Fetch data from scraper
            servant_data = self.scraper.scrape_civil_servants()
            
            # Process and insert each civil servant
            for data in servant_data:
                education_info = data.pop('education_info', {})
                servant = PublicServant(
                    name=data['name'],
                    department=data['department'],
                    joining_year=data['joining_year'],
                    education_location=education_info.get('education_location', 'India'),
                    university=education_info.get('university', 'Unknown'),
                    degree_level=education_info.get('degree_level', 'Unknown')
                )
                db.add(servant)
                logger.info(f"Added civil servant: {data['name']}")
            
            db.commit()
            return len(servant_data)
        except Exception as e:
            db.rollback()
            logger.error(f"Error importing civil servants: {str(e)}")
            raise
        finally:
            db.close()
