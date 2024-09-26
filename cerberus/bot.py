
# https://discord.com/api/oauth2/authorize?client_id=<client_id>&permissions=1099511704576&scope=bot
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pyexpat.errors import messages
from typing import List
import discord

import uuid
from cerberus.constants import REGIONAL_INDICATORS, ThreatLevel, EVENT_LOG_WINDOW, THREAT_LOG_WINDOW, ACTIVE_THREAT_WINDOW, THREAT_WARNING_MESSAGE, THREAT_BAN_MESSAGE, REACTS_PER_MESSAGE

# clap back
# async def discord.on_member_ban(guild, user):
# await remove_reaction(emoji, member)

"""
each react goes into event log

if user reacts with 3 or more letters
- begin tracking them
- escalate to threat YELLOW

if user reacts with 3 or more letters on two unique messages
- send warning message
- escalate to threat ORANGE

if user reacts with 3 or more letters on 3 unique messages
- remove all reacts
- send ban warning message
- escalate to threat RED

if user reacts
- ban user
"""


class EventLog:
    __log_events = []
    __sus_users = {}

    __threats = {}

    async def add_event(self, event):
        if self.__threats.get(event.user) is None:
            self.__threats[event.user] = Threat(event.user)
        active_threat = self.__threats[event.user]
        await active_threat.add_event(event)
        self.scrub_events()



        self.__log_events.append(event)

    def remove_event(self, event):
        # stubbed for future removal tracking
        pass

    def scrub_events(self):
        delta = timedelta(minutes = EVENT_LOG_WINDOW)
        now = datetime.now()
        self.__log_events = [x for x in self.__log_events if (now - x.datetime) < delta]
    """
    def alert_sus(self, user):
        if self.__sus_users.get(user) is None:
            self.__sus_users[user] = []

        events = [x for x in self.__log_events if x.user == user]
        for event in events:
            if event not in self.__sus_users[user]:
                self.__sus_users[user].append(event)

        message_hash = {}
        for event in self.__sus_users[user]:

            if message_hash.get(event.message) is None:
                message_hash[event.message] = []
            message_hash[event.message].append(event)

        print("================================================================================")
        print(f"{user}  @  {datetime.now()}")
        for message, events in message_hash.items():
            print("--------------------------------------------------------------------------------")
            print(f"Message was in #{message.channel.name} at {message.created_at}" )
            print(message.jump_url)
            print()
            print(f"{message.content}")
            print(" ".join([x.emoji.name for x in events]))
        print("==============================================================================")
        print("\n\n\n")

        # scrub out the events we just alerted on, so we're not blasting
        self.__log_events = [x for x in self.__log_events if x not in events]

    def check(self):
        self.scrub_events()

        user_track = {}
        for event in self.__log_events:
            if user_track.get(event.user) is None:
                user_track[event.user] = 0
            user_track[event.user] += 1
        
        for user, message_count in user_track.items():
            if message_count >= 3:
                self.alert_sus(user)
    """

@dataclass
class LogEvent:
    user: object = field(compare=False)
    message: discord.Message
    emoji: object
    datetime: str = field(default_factory=datetime.now, compare=False)
    removed: bool = field(default=False)


"""
TODO:
loop over all threats and remove all threats with touch time older than ACTIVE_THREAT_WINDOW
"""

class Threat:

    def __init__(self, user: discord.User):
        self.user = user
        self.level = ThreatLevel.GREEN
        self.events = []
        self.touch = datetime.now()
    
    async def add_event(self, event: LogEvent):
        self.events.append(event)
        self.scrub_events()
        threat_level = self.calc_threat_level()

        if threat_level > self.level:
            await self.escalate(threat_level)
        elif threat_level < self.level:
            self.deescalate(threat_level)

        self.touch = datetime.now()
        
    def scrub_events(self):
        delta = timedelta(minutes = THREAT_LOG_WINDOW)
        now = datetime.now()
        self.events = [x for x in self.events if (now - x.datetime) < delta]
    
    def calc_threat_level(self):
        message_hash = {}
        
        # todo: track descalation, and start threat_level based on passed threats
        threat_level = ThreatLevel.GREEN

        # If user reacts with 3 or more letters
        # - escalate threat (first escalation: YELLOW)
        if len(self.events) >= 3:
            threat_level = ThreatLevel.YELLOW

        for event in self.events:
            if message_hash.get(event.message) is None:
                message_hash[event.message] = []
            message_hash[event.message].append(event)

        offending_post_count = len([len(y) for x,y in message_hash.items()if len(y) >= REACTS_PER_MESSAGE])

        # if user reacts with 3 or more letters on two unique messages
        # - send warning message
        # - escalate threat (first escalation: ORANGE)
        if offending_post_count >= 2:
            threat_level = ThreatLevel.ORANGE

        # if user reacts with 3 or more letters on 3 unique messages
        # - remove all reacts
        # - send ban warning message
        # - escalate threat (first escalation: RED)
        if offending_post_count >= 3:
            threat_level = ThreatLevel.RED

        # if user was already at ThreatLevel.RED and our current assesment is at ThreatLevel.RED
        # - this means they hit red, and kept going.
        # - hard escalate to ThreatLevel.Midnight
        # - ban user
        if threat_level == ThreatLevel.RED and self.level == ThreatLevel.RED:
            threat_level = ThreatLevel.MIDNIGHT

        # log all the things
        if threat_level >= ThreatLevel.YELLOW:
            print("================================================================================")
            print(f"username:{self.user} datetime:{datetime.now()}")
            for message, events in message_hash.items():
                print("--------------------------------------------------------------------------------")
                print(f"Message was in #{message.channel.name} at {message.created_at}" )
                print(message.jump_url)
                print()
                print(f"{message.content}")
                print(" ".join([x.emoji.name for x in events]))
            print("==============================================================================")
            print("\n\n\n")

        return threat_level
    
    async def escalate(self, threat_level):
        self.level = threat_level

        if self.level == ThreatLevel.GREEN:
            # noop, this should even happen
            pass
        elif self.level == ThreatLevel.YELLOW:
            # print report to console
            # todo: send message to custom mod channel if defined in config
            pass
        elif self.level == ThreatLevel.ORANGE:
            # - send warning message
            try:
                await self.user.send(content=THREAT_WARNING_MESSAGE)
            except Exception:
                pass
        elif self.level == ThreatLevel.RED:
            # - remove all reacts
            # - send ban warning message
            try:
                await self.user.send(content=THREAT_BAN_MESSAGE)
            except Exception:
                pass
            for event in self.events:
                if event.removed is False:
                    await event.message.remove_reaction(event.emoji, event.user)
                    event.removed = True
        elif self.level == ThreatLevel.MIDNIGHT:
            # - remove all reacts
            # - todo: ban user
            for event in self.events:
                if event.removed is False:
                    await event.message.remove_reaction(event.emoji, event.user)
                    event.removed = True
            pass
        else:
            # handle weird case 
            pass

    def deescalate(self, threat_level):
        self.level = threat_level
        pass


class Cerberus(discord.Client):
    __log = EventLog()

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name in REGIONAL_INDICATORS:
            channel = await self.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await self.__log.add_event(LogEvent(user=payload.member, message=message, emoji=payload.emoji))
            #self.__log.check()

    #async def on_raw_reaction_remove(self, payload):
    #    if payload.emoji.name in REGIONAL_INDICATORS:
    #        channel = await self.fetch_channel(payload.channel_id)
    #        message = await channel.fetch_message(payload.message_id)
    #        self.__log.remove_event(LogEvent(user=payload.member, message=message, emoji=payload.emoji))
    #        self.__log.check()
