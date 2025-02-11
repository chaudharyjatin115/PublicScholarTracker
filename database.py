from models import PublicServant, Politician, PoliticianFamily, OfficerFamily, SessionLocal
from data_generator import generate_public_servant_data, generate_politician_data, generate_family_data
import pandas as pd
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

def seed_database():
    """Seed the database with initial mock data"""
    db = SessionLocal()

    try:
        # Check if database is already seeded
        if db.query(PublicServant).first() is None:
            # Generate and add public servants
            mock_data = generate_public_servant_data(200)
            records = mock_data.to_dict('records')
            servants = [PublicServant(**record) for record in records]
            db.bulk_save_objects(servants)
            db.commit()

            # Generate and add politicians
            politician_data = generate_politician_data(50)
            politician_records = politician_data.to_dict('records')
            politicians = [Politician(**record) for record in politician_records]
            db.bulk_save_objects(politicians)
            db.commit()

            # Get politician IDs and generate family members
            politician_ids = [p.id for p in db.query(Politician).all()]
            family_data = generate_family_data(politician_ids)
            family_records = family_data.to_dict('records')
            family_members = [PoliticianFamily(**record) for record in family_records]
            db.bulk_save_objects(family_members)
            db.commit()

    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        db.rollback()
    finally:
        db.close()

def get_all_servants():
    """Get all public servants with their family members from database"""
    db = SessionLocal()
    try:
        servants = db.query(PublicServant).all()

        servant_data = [{
            'id': s.id,
            'name': s.name,
            'department': s.department,
            'joining_year': s.joining_year,
            'education_location': s.education_location,
            'university': s.university,
            'degree_level': s.degree_level
        } for s in servants]

        family_data = []
        for s in servants:
            for fm in s.family_members:
                family_data.append({
                    'id': fm.id,
                    'officer_id': s.id,
                    'officer_name': s.name,
                    'name': fm.name,
                    'relation_type': fm.relation_type,
                    'education_location': fm.education_location,
                    'university': fm.university,
                    'degree_level': fm.degree_level
                })

        return (
            pd.DataFrame(servant_data) if servant_data else pd.DataFrame(),
            pd.DataFrame(family_data) if family_data else pd.DataFrame()
        )
    finally:
        db.close()

def get_all_politicians():
    """Get all politicians with their family members from database"""
    db = SessionLocal()
    try:
        # Use distinct to prevent duplicates
        politicians = db.query(Politician).distinct().all()

        politician_data = [{
            'id': p.id,  # Include ID for better tracking
            'name': p.name,
            'party': p.party,
            'position': p.position,
            'education_location': p.education_location,
            'university': p.university,
            'degree_level': p.degree_level
        } for p in politicians]

        family_data = []
        for p in politicians:
            for fm in p.family_members:
                family_data.append({
                    'id': fm.id,  # Added id field for family members
                    'politician_id': p.id,  # Include politician ID for relationship
                    'politician_name': p.name,
                    'name': fm.name,
                    'relation_type': fm.relation_type,
                    'education_location': fm.education_location,
                    'university': fm.university,
                    'degree_level': fm.degree_level
                })

        return (
            pd.DataFrame(politician_data) if politician_data else pd.DataFrame(),
            pd.DataFrame(family_data) if family_data else pd.DataFrame()
        )
    finally:
        db.close()

def add_servant(data, family_members=None):
    """Add a new public servant with optional family members to database"""
    db = SessionLocal()
    try:
        servant = PublicServant(**data)
        db.add(servant)
        db.commit()
        db.refresh(servant)

        if family_members:
            add_children_to_officer(servant.id, family_members)

        return servant
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def add_politician(data, family_members=None):
    """Add a new politician with optional family members to database"""
    db = SessionLocal()
    try:
        if check_politician_exists(data['name'], data['party']):
            raise ValueError(f"Politician {data['name']} from party {data['party']} already exists.")
        politician = Politician(**data)
        db.add(politician)
        db.commit()
        db.refresh(politician)

        if family_members:
            add_children_to_politician(politician.id, family_members)

        return politician
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def check_politician_exists(name, party):
    """Check if a politician with given name and party exists"""
    db = SessionLocal()
    try:
        return db.query(Politician).filter(
            and_(Politician.name == name, Politician.party == party)
        ).first()
    finally:
        db.close()

def check_child_exists(politician_id, child_name):
    """Check if a child already exists for the politician"""
    db = SessionLocal()
    try:
        return db.query(PoliticianFamily).filter(
            and_(
                PoliticianFamily.politician_id == politician_id,
                PoliticianFamily.name == child_name
            )
        ).first()
    finally:
        db.close()

def check_officer_child_exists(officer_id, child_name):
    """Check if a child already exists for the officer"""
    db = SessionLocal()
    try:
        return db.query(OfficerFamily).filter(
            and_(
                OfficerFamily.officer_id == officer_id,
                OfficerFamily.name == child_name
            )
        ).first()
    finally:
        db.close()

def delete_politician(politician_id):
    """Delete a politician and their family members"""
    db = SessionLocal()
    try:
        politician = db.query(Politician).filter(Politician.id == politician_id).first()
        if politician:
            db.delete(politician)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def delete_servant(servant_id):
    """Delete a public servant"""
    db = SessionLocal()
    try:
        servant = db.query(PublicServant).filter(PublicServant.id == servant_id).first()
        if servant:
            db.delete(servant)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def add_children_to_politician(politician_id, family_data):
    """Add new children to an existing politician"""
    db = SessionLocal()
    try:
        for child_data in family_data:
            if not check_child_exists(politician_id, child_data['name']):
                child_data['politician_id'] = politician_id
                family_member = PoliticianFamily(**child_data)
                db.add(family_member)
            else:
                raise ValueError(f"Child {child_data['name']} already exists for this politician")
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def add_children_to_officer(officer_id, family_data):
    """Add new children to an existing officer"""
    db = SessionLocal()
    try:
        for child_data in family_data:
            if not check_officer_child_exists(officer_id, child_data['name']):
                child_data['officer_id'] = officer_id
                family_member = OfficerFamily(**child_data)
                db.add(family_member)
            else:
                raise ValueError(f"Child {child_data['name']} already exists for this officer")
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()