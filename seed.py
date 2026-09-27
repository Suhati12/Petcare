from datetime import date, timedelta
from app import create_app
from models import db
from models.user import User
from models.pet import Pet
from models.vaccination import Vaccination
from models.deworming import Deworming
from models.medication import Medication
from models.grooming import Grooming
from models.vet_visit import VetVisit
from services.reminder_engine import run_reminder_scan

app = create_app()

def seed_database():
    with app.app_context():
        print("Recreating database tables...")
        db.drop_all()
        db.create_all()

        today = date.today()

        # 1. Create Users
        print("Seeding Users...")
        u1 = User(name='Alex Johnson', email='alex@petcare.com', phone='+1 555-0192')
        u1.set_password('password123')

        u2 = User(name='Sarah Miller', email='sarah@petcare.com', phone='+1 555-0144')
        u2.set_password('password123')

        u3 = User(name='David Smith', email='david@petcare.com', phone='+1 555-0188')
        u3.set_password('password123')

        db.session.add_all([u1, u2, u3])
        db.session.commit()

        # 2. Create Pets
        print("Seeding Pets...")
        p1 = Pet(
            user_id=u1.id,
            name='Max',
            species='Dog',
            breed='Golden Retriever',
            gender='Male',
            dob=today - timedelta(days=365 * 3),
            weight=28.5,
            color='Golden',
            microchip_id='985141002948123',
            allergies='Chicken protein, Dust mites',
            medical_conditions='Mild seasonal allergies',
            emergency_notes='Very friendly. If lost call Alex immediately.'
        )

        p2 = Pet(
            user_id=u1.id,
            name='Bella',
            species='Cat',
            breed='Persian',
            gender='Female',
            dob=today - timedelta(days=365 * 2),
            weight=4.2,
            color='White',
            microchip_id='985141002948456',
            allergies='None known',
            medical_conditions='None',
            emergency_notes='Indoor cat only. Requires daily eye cleaning.'
        )

        p3 = Pet(
            user_id=u2.id,
            name='Charlie',
            species='Dog',
            breed='Beagle',
            gender='Male',
            dob=today - timedelta(days=365 * 1),
            weight=12.0,
            color='Tricolor',
            microchip_id='985141002948789',
            allergies='Lactose',
            medical_conditions='Sensitive stomach',
            emergency_notes='Responds to whistle.'
        )

        p4 = Pet(
            user_id=u2.id,
            name='Luna',
            species='Cat',
            breed='Siamese',
            gender='Female',
            dob=today - timedelta(days=365 * 4),
            weight=3.8,
            color='Seal Point',
            microchip_id='985141002948999',
            allergies='None',
            medical_conditions='Feline Asthma (mild)',
            emergency_notes='Inhaler kept in pet emergency kit.'
        )

        p5 = Pet(
            user_id=u3.id,
            name='Coco',
            species='Rabbit',
            breed='Holland Lop',
            gender='Male',
            dob=today - timedelta(days=240),
            weight=1.8,
            color='Brown',
            microchip_id='985141002948111',
            allergies='None',
            medical_conditions='None',
            emergency_notes='Loves fresh Timothy hay.'
        )

        db.session.add_all([p1, p2, p3, p4, p5])
        db.session.commit()

        # 3. Create Vaccinations
        print("Seeding Vaccinations...")
        v1 = Vaccination(
            pet_id=p1.id,
            vaccine_name='Rabies 3-Year Vaccine',
            vaccine_type='Core',
            date_administered=today - timedelta(days=180),
            next_due_date=today + timedelta(days=500),
            veterinarian='Dr. Robert Hayes',
            clinic='City Pet Hospital',
            dose='1.0 mL',
            notes='Annual booster administered cleanly.'
        )

        v2 = Vaccination(
            pet_id=p1.id,
            vaccine_name='DHPP (Distemper, Hepatitis, Parvo, Parainfluenza)',
            vaccine_type='Core',
            date_administered=today - timedelta(days=360),
            next_due_date=today + timedelta(days=4),  # DUE SOON!
            veterinarian='Dr. Clara Evans',
            clinic='Valley Veterinary Care',
            dose='1.0 mL',
            notes='Booster required within 7 days.'
        )

        v3 = Vaccination(
            pet_id=p2.id,
            vaccine_name='FVRCP (Feline Viral Rhinotracheitis)',
            vaccine_type='Core',
            date_administered=today - timedelta(days=400),
            next_due_date=today - timedelta(days=35),  # OVERDUE!
            veterinarian='Dr. Clara Evans',
            clinic='Valley Veterinary Care',
            dose='1.0 mL',
            notes='Overdue for yearly booster!'
        )

        v4 = Vaccination(
            pet_id=p3.id,
            vaccine_name='Bordetella (Kennel Cough)',
            vaccine_type='Non-Core',
            date_administered=today - timedelta(days=90),
            next_due_date=today + timedelta(days=270),
            veterinarian='Dr. Mark Stevens',
            clinic='Paws & Claws Clinic',
            dose='0.5 mL',
            notes='Intranasal vaccine given.'
        )

        db.session.add_all([v1, v2, v3, v4])

        # 4. Create Dewormings
        print("Seeding Deworming Records...")
        d1 = Deworming(
            pet_id=p1.id,
            deworming_date=today - timedelta(days=85),
            medicine='Drontal Plus Taste Tabs',
            dose='2 Tablets',
            next_due_date=today + timedelta(days=5),  # DUE SOON!
            notes='Quarterly broad spectrum deworming.'
        )

        d2 = Deworming(
            pet_id=p2.id,
            deworming_date=today - timedelta(days=120),
            medicine='Broadline Spot-On for Cats',
            dose='0.9 mL Tube',
            next_due_date=today - timedelta(days=30),  # OVERDUE!
            notes='Topical treatment overdue.'
        )

        db.session.add_all([d1, d2])

        # 5. Create Medications
        print("Seeding Medication Schedules...")
        m1 = Medication(
            pet_id=p1.id,
            medicine_name='Apoquel 16mg',
            purpose='Seasonal Allergic Dermatitis',
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=5),
            frequency='Once daily',
            time='08:00 AM',
            dosage='1 Tablet (16mg)',
            instructions='Give with breakfast food.',
            notes='Reduces itching effectively.',
            status='Active'
        )

        m2 = Medication(
            pet_id=p2.id,
            medicine_name='Otomax Ear Drops',
            purpose='Outer ear yeast infection',
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=20),
            frequency='Twice daily',
            time='08:00 AM, 08:00 PM',
            dosage='4 drops left ear',
            instructions='Clean ear prior to drops.',
            notes='Course completed successfully.',
            status='Completed'
        )

        db.session.add_all([m1, m2])

        # 6. Create Grooming Records
        print("Seeding Grooming Schedules...")
        g1 = Grooming(
            pet_id=p1.id,
            care_type='Bath',
            last_date=today - timedelta(days=20),
            next_due_date=today + timedelta(days=1),  # DUE TOMORROW!
            notes='Hypoallergenic shampoo recommended.'
        )

        g2 = Grooming(
            pet_id=p1.id,
            care_type='Nail trimming',
            last_date=today - timedelta(days=25),
            next_due_date=today + timedelta(days=3),  # DUE SOON!
            notes='Trim front claws carefully.'
        )

        g3 = Grooming(
            pet_id=p2.id,
            care_type='Dental cleaning',
            last_date=today - timedelta(days=180),
            next_due_date=today - timedelta(days=10),  # OVERDUE!
            notes='Enzymatic toothpaste treatment.'
        )

        db.session.add_all([g1, g2, g3])

        # 7. Create Vet Visits
        print("Seeding Vet Visits...")
        vv1 = VetVisit(
            pet_id=p1.id,
            vet_name='Dr. Robert Hayes',
            clinic='City Pet Hospital',
            visit_date=today - timedelta(days=60),
            visit_time='10:30 AM',
            reason='Routine Wellness Examination',
            diagnosis='Healthy active dog. Slight tartar buildup on molars.',
            treatment='Prescribed dental chews. Weight check normal.',
            prescription='Oravet Dental Hygiene Chews',
            notes='Follow up in 6 months.',
            follow_up_date=today + timedelta(days=120)
        )

        vv2 = VetVisit(
            pet_id=p1.id,
            vet_name='Dr. Clara Evans',
            clinic='Valley Veterinary Care',
            visit_date=today + timedelta(days=6),  # UPCOMING VISIT!
            visit_time='02:00 PM',
            reason='Allergy Follow-up & Vaccine Booster',
            diagnosis='Pending evaluation',
            treatment='Pending',
            prescription='None yet',
            notes='Bring medical history log.'
        )

        db.session.add_all([vv1, vv2])
        db.session.commit()

        # 8. Run Smart Reminder Scanner to populate Reminders & Notifications
        print("Running Smart Reminder Scanner to build reminders & notifications...")
        run_reminder_scan()

        print("\n==========================================")
        print("DEMO DATA SEEDED SUCCESSFULLY!")
        print("==========================================")
        print("Demo Users Created:")
        print("1) Email: alex@petcare.com  | Password: password123 (Pets: Max, Bella)")
        print("2) Email: sarah@petcare.com | Password: password123 (Pets: Charlie, Luna)")
        print("3) Email: david@petcare.com | Password: password123 (Pets: Coco)")
        print("==========================================\n")

if __name__ == '__main__':
    seed_database()
