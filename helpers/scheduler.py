from typing import Union

import discord
import re
from helpers.exceptions import SLOT_FULL, SLOT_NOT_FOUND, MULTIPLE_SIGN_UP

LEVELS = ['Rookie / Amateur', 'Lower Intermediate', 'Upper Intermediate / Advanced']

WAITING_STATUS = '**Status**: Awaiting more players'
TO_BOOK_STATUS = '**Status**: To be booked'
BOOKED_STATUS = '**Staus**: Court #{court_no} booked by {user}'

SESSION_MESSAGE = '\\*\\*\\_\\_{date}\\_\\_\\*\\*, {start_time} to {end_time} at {location}'
SLOT_MESSAGE = '''
Slot {slot_idx}: 
Level: {level}
**Status:** Awaiting more players
'''
SCHEDULE_MESSAGE = '''
**__{{date}}__**, {{start_time}} to {{end_time}} at {{location}}
Slot 1: 
Level: {level0}
**Status:** Awaiting more players
Slot 2: 
Level: {level1}
**Status:** Awaiting more players
Slot 3: 
Level: {level2}
**Status:** Awaiting more players
'''.format(level0=LEVELS[0], level1=LEVELS[1], level2=LEVELS[2])


# Helper class for creating and tracking scheduling messages
class Scheduler:
    @staticmethod
    def __get_schedule_key(content):
        session_data = content.split('\n')[0]
        regex = re.sub(r'{(.+?)}', r'(?P<_\1>.+)', SESSION_MESSAGE)
        return list(re.search(regex, session_data).groups())

    @staticmethod
    def create_schedule(date: str, start_time: str, end_time: str, location: str):
        return SCHEDULE_MESSAGE.format(date=date, start_time=start_time, end_time=end_time, location=location)

    # Add user mention to a specific slot in schedule
    @staticmethod
    def add_schedule_mention(content: str, slot_idx: int, user: Union[discord.Member, discord.User]):
        date, _, _, location = Scheduler.__get_schedule_key(content)

        idx = -1
        prefix = f"Slot {slot_idx}: ".format(slot_idx=slot_idx)
        content_lines = content.split('\n')

        for i in range(len(content_lines)):
            if content_lines[i].startswith(prefix):
                idx = i
                break

        if idx == -1:
            raise Exception(SLOT_NOT_FOUND.format(slot_idx=slot_idx, date=date, location=location))

        attendees = content_lines[idx][len(prefix):].split(', ')
        if len(attendees) == 1 and attendees[0] == '':
            attendees = []
        # Check if slot is full
        if len(attendees) == 6:
            raise Exception(SLOT_FULL.format(slot_idx=slot_idx, date=date, location=location))

        curr_slot = 0
        # Check if user is in another slot and find current slot number
        for slot in content_lines:
            if slot.startswith("Slot"):
                curr_slot += 1
                if user.mention in slot:
                    raise Exception(MULTIPLE_SIGN_UP.format(user=user.mention, date=date, location=location))

        # Add user to slot
        attendees.append(user.mention)
        content_lines[idx] = prefix + ', '.join(attendees)
        if len(attendees) == 4 and content_lines[idx+2] == WAITING_STATUS:
            content_lines[idx+2] = TO_BOOK_STATUS
            # Add another slot if there is no empty slot and
            if not content_lines[idx+1].endswith('*'):
                level = content_lines[idx+1][len('Level: '):]
                content += SLOT_MESSAGE.format(level=level, slot_idx=curr_slot + 1)
                content_lines[idx+1] += '*'
        content = '\n'.join(content_lines)
        return content

    # Remove user mention from schedule
    @staticmethod
    def remove_schedule_mention(content: str, slot_idx: int, user: Union[discord.Member, discord.User]):
        idx = -1
        prefix = f"Slot {slot_idx}: ".format(slot_idx=slot_idx)
        content_lines = content.split('\n')
        for i in range(len(content_lines)):
            if content_lines[i].startswith(prefix):
                idx = i
                break

        if idx == -1:
            return ''

        # Find attendees and remove user
        attendees = content_lines[idx][len(prefix):].split(', ')
        attendees.remove(user.mention)
        # Check if slot is now waiting for more players
        if len(attendees) == 3 and content_lines[idx+2] == TO_BOOK_STATUS:
            content_lines[idx+2] = WAITING_STATUS
        content_lines[idx] = prefix + ', '.join(attendees)
        content = '\n'.join(content_lines)
        return content

    # Book a slot under a user specifying the court number
    @staticmethod
    def book_slot(content: str, slot_idx: str, court_no: str, user: Union[discord.Member, discord.User]):
        date, _, _, location = Scheduler.__get_schedule_key(content)

        idx = -1
        prefix = f"Slot {slot_idx}: ".format(slot_idx=slot_idx)
        content_lines = content.split('\n')

        for i in range(len(content_lines)):
            if content_lines[i].startswith(prefix):
                idx = i
                break

        if idx == -1:
            raise Exception(SLOT_NOT_FOUND.format(slot_idx=slot_idx, date=date, location=location))

        content_lines[idx + 2] = BOOKED_STATUS.format(court_no=court_no, user=user.mention)
        content = '\n'.join(content_lines)
        return content
