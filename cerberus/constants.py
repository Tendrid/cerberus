from enum import IntEnum

REGIONAL_INDICATORS = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']

REACTS_PER_MESSAGE = 3

# how long should we keep around reacts before throwing them out (in minutes)
# default 1 hour
EVENT_LOG_WINDOW = 60

# how long should we keep around reacts on an active threat before throwing them out (in minutes)
# default 4 hour
THREAT_LOG_WINDOW = 240

# how long we should track an inactive threat before removing it (in minutes)
# default 8 hours
ACTIVE_THREAT_WINDOW = 480

THREAT_WARNING_MESSAGE = f"Reacting to more than one message within {EVENT_LOG_WINDOW} minutes with regional letters is against the rules on the TinaKitten server.  If you have any questions about this rule, please DM Tendrid."

THREAT_BAN_MESSAGE = f"You have reacted to many times with regional letters.  All reactions have been removed, and if you react one more time, you will flagged to be banned by a mod!"

class ThreatLevel(IntEnum):
    GREEN = 0
    YELLOW = 1
    ORANGE = 2
    RED = 3
    MIDNIGHT = 4