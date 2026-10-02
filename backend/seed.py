from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select

from backend.database import SessionLocal
from backend.models import (
    Equipment,
    Event,
    EventEquipment,
    EventPerson,
    EventVendor,
    Incident,
    Person,
    Reservation,
    Room,
    Team,
    Venue,
    Vendor,
)

IST = ZoneInfo("Asia/Kolkata")

def seed():
    with SessionLocal() as session:
        existing_event = session.scalar(
            select(Event).where(
                Event.name == "Opening Ceremony"
            )
        )

        if existing_event:
            print("Seed data already exists. Nothing to do.")
            return

        # 1. Create Venue (Removed 'capacity' attribute)
        venue = Venue(
            name="GITAM Hyderabad Campus",
            address="Rudraram, Hyderabad, Telangana",
            created_at=datetime.now(IST),
        )
        session.add(venue)
        session.flush()

        # 2. Create Rooms
        rooms = [
            Room(venue_id=venue.id, name="Main Auditorium", capacity=500, floor=1, status="AVAILABLE"),
            Room(venue_id=venue.id, name="C-204", capacity=60, floor=2, status="AVAILABLE"),
            Room(venue_id=venue.id, name="C-301", capacity=120, floor=3, status="AVAILABLE"),
            Room(venue_id=venue.id, name="AI Lab", capacity=40, floor=2, status="AVAILABLE"),
            Room(venue_id=venue.id, name="Seminar Hall", capacity=80, floor=1, status="AVAILABLE"),
        ]
        session.add_all(rooms)
        session.flush()

        auditorium = rooms[0]
        room_c204 = rooms[1]
        room_c301 = rooms[2]
        ai_lab = rooms[3]
        seminar_hall = rooms[4]

        # 3. Create People
        people = [
            Person(name="Ananya Rao", email="ananya.rao@nexcord.dev", phone="+919800000001", role="ORGANIZER"),
            Person(name="Arjun Mehta", email="arjun.mehta@nexcord.dev", phone="+919800000002", role="JUDGE"),
            Person(name="Priya Nair", email="priya.nair@nexcord.dev", phone="+919800000003", role="JUDGE"),
            Person(name="Rohan Kumar", email="rohan.kumar@nexcord.dev", phone="+919800000004", role="JUDGE"),
            Person(name="Sneha Patel", email="sneha.patel@nexcord.dev", phone="+919800000005", role="VOLUNTEER"),
            Person(name="Karthik Singh", email="karthik.singh@nexcord.dev", phone="+919800000006", role="VOLUNTEER"),
        ]
        session.add_all(people)
        session.flush()

        organizer = people[0]
        arjun = people[1]
        priya = people[2]
        rohan = people[3]
        sneha = people[4]
        karthik = people[5]

        # 4. Create Vendors
        vendors = [
            Vendor(name="Campus Caterers", vendor_type="CATERING", contact_name="Vikram Shah", phone="+919811111111", email="vikram@campuscaterers.test", status="ACTIVE"),
            Vendor(name="AV Solutions", vendor_type="AUDIO_VISUAL", contact_name="Meera Joshi", phone="+919822222222", email="meera@avsolutions.test", status="ACTIVE"),
            Vendor(name="SecureGuard Services", vendor_type="SECURITY", contact_name="Rakesh Verma", phone="+919833333333", email="rakesh@secureguard.test", status="ACTIVE"),
            Vendor(name="CityRide Transport", vendor_type="TRANSPORT", contact_name="Nikhil Rao", phone="+919844444444", email="nikhil@cityride.test", status="ACTIVE"),
        ]
        session.add_all(vendors)
        session.flush()

        caterer = vendors[0]
        av_vendor = vendors[1]
        security_vendor = vendors[2]
        transport_vendor = vendors[3]

        # 5. Create Equipment
        equipment = [
            Equipment(name="Projector", category="DISPLAY", quantity=10, available_quantity=7, status="AVAILABLE"),
            Equipment(name="Laptop", category="COMPUTING", quantity=50, available_quantity=38, status="AVAILABLE"),
            Equipment(name="Robotics Kit", category="ROBOTICS", quantity=20, available_quantity=15, status="AVAILABLE"),
            Equipment(name="PA System", category="AUDIO", quantity=4, available_quantity=3, status="AVAILABLE"),
        ]
        session.add_all(equipment)
        session.flush()

        projector = equipment[0]
        laptop = equipment[1]
        robotics_kit = equipment[2]
        pa_system = equipment[3]

        # 6. Create Events
        events = [
            Event(name="Opening Ceremony", description="Opening ceremony for GITAM TechFest 2026.", start_time=datetime(2026, 10, 10, 9, 0, tzinfo=IST), end_time=datetime(2026, 10, 10, 10, 30, tzinfo=IST), status="SCHEDULED"),
            Event(name="AI Workshop", description="Hands-on workshop covering practical AI engineering.", start_time=datetime(2026, 10, 10, 11, 0, tzinfo=IST), end_time=datetime(2026, 10, 10, 13, 0, tzinfo=IST), status="SCHEDULED"),
            Event(name="Robotics Final", description="Final round of the autonomous robotics competition.", start_time=datetime(2026, 10, 10, 11, 30, tzinfo=IST), end_time=datetime(2026, 10, 10, 13, 30, tzinfo=IST), status="SCHEDULED"),
            Event(name="Hackathon Demo", description="Final project demonstrations from hackathon teams.", start_time=datetime(2026, 10, 10, 16, 30, tzinfo=IST), end_time=datetime(2026, 10, 10, 18, 0, tzinfo=IST), status="SCHEDULED"),
            Event(name="Closing Ceremony", description="Closing ceremony and prize distribution.", start_time=datetime(2026, 10, 10, 18, 30, tzinfo=IST), end_time=datetime(2026, 10, 10, 19, 30, tzinfo=IST), status="SCHEDULED"),
        ]
        session.add_all(events)
        session.flush()

        opening = events[0]
        ai_workshop = events[1]
        robotics_final = events[2]
        hackathon_demo = events[3]
        closing = events[4]

        # 7. Create Teams
        teams = [
            Team(event_id=robotics_final.id, name="Team Alpha", status="CHECKED_IN"),
            Team(event_id=robotics_final.id, name="Team Beta", status="CHECKED_IN"),
            Team(event_id=robotics_final.id, name="Team Gamma", status="CHECKED_IN"),
            Team(event_id=robotics_final.id, name="Team Delta", status="CHECKED_IN"),
        ]
        session.add_all(teams)

        # 8. Assign People
        event_people = [
            EventPerson(event_id=opening.id, person_id=organizer.id, assignment_role="EVENT ORGANIZER"),
            EventPerson(event_id=robotics_final.id, person_id=arjun.id, assignment_role="ROBOTICS JUDGE"),
            EventPerson(event_id=robotics_final.id, person_id=priya.id, assignment_role="ROBOTICS JUDGE"),
            EventPerson(event_id=robotics_final.id, person_id=rohan.id, assignment_role="TECHNICAL JUDGE"),
            EventPerson(event_id=robotics_final.id, person_id=sneha.id, assignment_role="EVENT VOLUNTEER"),
            EventPerson(event_id=ai_workshop.id, person_id=priya.id, assignment_role="WORKSHOP MENTOR"),
            EventPerson(event_id=hackathon_demo.id, person_id=karthik.id, assignment_role="VOLUNTEER"),
        ]
        session.add_all(event_people)

        # 9. Assign Vendors
        event_vendors = [
            EventVendor(event_id=opening.id, vendor_id=caterer.id, service_type="CATERING", status="ASSIGNED"),
            EventVendor(event_id=opening.id, vendor_id=security_vendor.id, service_type="SECURITY", status="ASSIGNED"),
            EventVendor(event_id=robotics_final.id, vendor_id=av_vendor.id, service_type="AUDIO_VISUAL", status="ASSIGNED"),
            EventVendor(event_id=closing.id, vendor_id=transport_vendor.id, service_type="TRANSPORT", status="ASSIGNED"),
        ]
        session.add_all(event_vendors)

        # 10. Assign Equipment
        event_equipment = [
            EventEquipment(event_id=robotics_final.id, equipment_id=robotics_kit.id, quantity=12),
            EventEquipment(event_id=robotics_final.id, equipment_id=projector.id, quantity=2),
            EventEquipment(event_id=ai_workshop.id, equipment_id=laptop.id, quantity=30),
            EventEquipment(event_id=ai_workshop.id, equipment_id=projector.id, quantity=1),
            EventEquipment(event_id=opening.id, equipment_id=pa_system.id, quantity=1),
            EventEquipment(event_id=opening.id, equipment_id=projector.id, quantity=1),
        ]
        session.add_all(event_equipment)

        # 11. Create Reservations
        reservations = [
            Reservation(event_id=opening.id, room_id=auditorium.id, start_time=datetime(2026, 10, 10, 9, 0, tzinfo=IST), end_time=datetime(2026, 10, 10, 10, 30, tzinfo=IST), status="ACTIVE"),
            Reservation(event_id=ai_workshop.id, room_id=room_c204.id, start_time=datetime(2026, 10, 10, 11, 0, tzinfo=IST), end_time=datetime(2026, 10, 10, 13, 0, tzinfo=IST), status="ACTIVE"),
            Reservation(event_id=robotics_final.id, room_id=room_c204.id, start_time=datetime(2026, 10, 10, 11, 30, tzinfo=IST), end_time=datetime(2026, 10, 10, 13, 30, tzinfo=IST), status="ACTIVE"),
            Reservation(event_id=hackathon_demo.id, room_id=room_c301.id, start_time=datetime(2026, 10, 10, 16, 30, tzinfo=IST), end_time=datetime(2026, 10, 10, 18, 0, tzinfo=IST), status="ACTIVE"),
            Reservation(event_id=closing.id, room_id=auditorium.id, start_time=datetime(2026, 10, 10, 18, 30, tzinfo=IST), end_time=datetime(2026, 10, 10, 19, 30, tzinfo=IST), status="ACTIVE"),
        ]
        session.add_all(reservations)

        # 12. Create Incidents (Renamed 'extra_data' to 'extra_data')
        incidents = [
            Incident(event_id=opening.id, vendor_id=caterer.id, type="VENDOR_CANCELLED", severity="HIGH", status="OPEN", source="EXTERNAL_API", title="Catering vendor cancelled", description="Campus Caterers cancelled the opening-day catering assignment.", extra_data={"cancellation_reason": "Staffing shortage", "notice_hours": 4}),
            Incident(event_id=robotics_final.id, room_id=room_c204.id, type="ROOM_DOUBLE_BOOKED", severity="HIGH", status="OPEN", source="SYSTEM", title="Room C-204 is double booked", description="The Robotics Final overlaps with the AI Workshop reservation.", extra_data={"conflicting_event": "AI Workshop"}),
            Incident(event_id=robotics_final.id, room_id=room_c204.id, equipment_id=projector.id, type="EQUIPMENT_FAILURE", severity="HIGH", status="OPEN", source="USER", title="Projector failure in C-204", description="The primary projector is not displaying an image.", extra_data={"device": "Projector", "observed_status": "OFFLINE"}),
            Incident(event_id=robotics_final.id, person_id=arjun.id, type="PERSON_UNAVAILABLE", severity="MEDIUM", status="OPEN", source="USER", title="Robotics judge unavailable", description="Arjun Mehta reported that he cannot attend the Robotics Final.", extra_data={"replacement_required": True, "expertise": "Robotics"}),
            Incident(event_id=robotics_final.id, room_id=room_c204.id, type="CROWDING", severity="HIGH", status="OPEN", source="COMPUTER_VISION", title="C-204 exceeds expected occupancy", description="Computer vision detected more people than the room capacity.", extra_data={"observed_occupancy": 62, "room_capacity": 60, "confidence": 0.94}),
        ]
        session.add_all(incidents)

        session.commit()

    print("NexCord seed data created successfully.")

if __name__ == "__main__":
    seed()