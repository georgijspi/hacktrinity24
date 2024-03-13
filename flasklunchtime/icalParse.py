import os
from icalendar import Calendar
from datetime import datetime
from database import db, Event  # Adjust import path as needed

def process_ical_file(file_path, user_id):
    with open(file_path, 'rb') as ical_file:
        cal = Calendar.from_ical(ical_file.read())

        for component in cal.walk():
            if component.name == "VEVENT":
                event = Event(
                    title=component.get('summary'),
                    start=component.get('dtstart').dt,
                    end=component.get('dtend').dt,
                    user_id=user_id
                )
                db.session.add(event)
        db.session.commit()
