from typing import Union
from helpers.session import SessionKey, Slot

import discord
import re
from helpers.exceptions import SESSION_EXISTS, SLOT_FULL, SLOT_NOT_FOUND, SESSION_NOT_FOUND, IMPOSSIBLE_EXCEPTION, \
    MULTIPLE_SIGN_UP

LEVELS = ['Rookie / Amateur', 'Intermediate / Advanced']

SLOT_MESSAGE = '''
Slot {slot_idx}: 
Level: {level}
**Status:** Awaiting more players
'''

SESSION_MESSAGE = '\\*\\*\\_\\_{date}\\_\\_\\*\\*, {start_time} to {end_time} at {location}'

SCHEDULE_MESSAGE = '''
**__{date}__**, {start_time} to {end_time} at {location}
Slot 1: 
Level: Rookie / Amateur
**Status:** Awaiting more players
Slot 2: 
Level: Intermediate / Advanced
**Status:** Awaiting more players
'''


# Helper class for creating and tracking scheduling messages
class Scheduler:
    def __init__(self):
        self.sessions = dict()

    @staticmethod
    def __get_schedule_key(content):
        session_data = content.split('\n')[0]
        regex = re.sub(r'{(.+?)}', r'(?P<_\1>.+)', SESSION_MESSAGE)
        return list(re.search(regex, session_data).groups())

    def create_schedule(self, date: str, start_time: str, end_time: str, location: str):
        content = SCHEDULE_MESSAGE.format(date=date, start_time=start_time, end_time=end_time, location=location)
        key = SessionKey(date=date, start_time=start_time, end_time=end_time, location=location)
        if key in self.sessions:
            raise Exception(SESSION_EXISTS
                            .format(date=date, start_time=start_time, end_time=end_time, location=location))

        self.sessions[key] = [Slot(LEVELS[0]), Slot(LEVELS[1])]
        return content

    def delete_schedule(self, content):
        date, start_time, end_time, location = self.__get_schedule_key(content)
        key = SessionKey(date=date, start_time=start_time, end_time=end_time, location=location)
        if key in self.sessions:
            self.sessions[key] = None
            del self.sessions[key]

    # Add user mention to a specific slot in schedule
    def add_schedule_mention(self, content: str, slot_idx: int, user: Union[discord.Member, discord.User]):
        date, start_time, end_time, location = self.__get_schedule_key(content)
        key = SessionKey(date=date, start_time=start_time, end_time=end_time, location=location)
        if key not in self.sessions:
            raise Exception(SESSION_NOT_FOUND
                            .format(date=date, start_time=start_time, end_time=end_time, location=location))

        if user.mention in content:
            raise Exception(MULTIPLE_SIGN_UP.format(user=user.mention, date=date, location=location))

        slots = self.sessions[key]
        if slot_idx <= 0 or slot_idx > len(slots):
            raise Exception(SLOT_NOT_FOUND.format(slot_idx=slot_idx, date=date, location=location))
        slot = slots[slot_idx - 1]
        if slot.count == 6:
            raise Exception(SLOT_FULL.format(slot_idx=slot_idx, date=date, location=location))

        # Add user mention
        content_lines = content.split('\n')
        for i in range(len(content_lines)):
            if content_lines[i].startswith("Slot {slot_idx}".format(slot_idx=slot_idx)):
                if slot.count > 0:
                    content_lines[i] += ', '
                content_lines[i] += user.mention
                slot.count += 1
                # If slot has 4 players and is not currently booked, update status to "To be booked"
                if slot.count == 4 and not slot.booked:
                    content_lines[i+2] = '**Status**: To be booked'
        content = '\n'.join(content_lines)

        # Add another slot if attendees in a slot is 4.
        if slot.count == 4 and not slot.slot_added:
            if not slot.slot_added:
                slot.slot_added = True
                slots.append(Slot(level=slot.level))
                slot_idx = len(slots)
                content += SLOT_MESSAGE.format(level=slot.level, slot_idx=slot_idx)
        return content

    # Remove user mention from schedule
    def remove_schedule_mention(self, content: str, slot_idx: int, user: Union[discord.Member, discord.User]):
        date, start_time, end_time, location = self.__get_schedule_key(content)
        key = SessionKey(date=date, start_time=start_time, end_time=end_time, location=location)
        if slot_idx <= 0:
            raise Exception(SLOT_NOT_FOUND.format(slot_idx=slot_idx, date=date, location=location))
        if key not in self.sessions:
            raise Exception(IMPOSSIBLE_EXCEPTION)
        slots = self.sessions[key]
        if slot_idx > len(slots) or slots[slot_idx - 1].count == 0:
            raise Exception(IMPOSSIBLE_EXCEPTION)

        slot = slots[slot_idx - 1]
        slot.count -= 1
        if slot.count == 3 and not slot.booked:
            content_lines = content.split('\n')
            for i in range(len(content_lines)):
                if content_lines[i].startswith("Slot {slot_idx}".format(slot_idx=slot_idx)):
                    content_lines[i+2] = '**Status**: Awaiting more players'

        content = content.replace(user.mention, '')
        return content

    # Book a slot under a user specifying the court number
    def book_slot(self, content: str, slot_idx: str, court_no: str, user: Union[discord.Member, discord.User]):
        slot_idx = int(slot_idx)
        date, start_time, end_time, location = self.__get_schedule_key(content)
        key = SessionKey(date=date, start_time=start_time, end_time=end_time, location=location)
        if int(slot_idx) > len(self.sessions[key]) or slot_idx <= 0:
            raise Exception(SLOT_NOT_FOUND.format(slot_idx=slot_idx, date=date, location=location))

        slots = self.sessions[key]
        slots[slot_idx - 1].booked = True
        content_lines = content.split('\n')
        for i in range(len(content_lines)):
            if content_lines[i].startswith("Slot {slot_idx}".format(slot_idx=slot_idx)):
                content_lines[i + 2] = '**Status**: Court #{court_no} booked by {user}.'\
                    .format(court_no=court_no, user=user.mention)
        content = '\n'.join(content_lines)
        return content
