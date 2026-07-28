"""Domain-oriented access to the Italian Knowledge Graph seed."""

from .arts_culture import NODES as ARTS_CULTURE
from .daily_life import NODES as DAILY_LIFE
from .economy_law_politics import NODES as ECONOMY_LAW_POLITICS
from .formal_natural_sciences import NODES as FORMAL_NATURAL_SCIENCES
from .health_environment import NODES as HEALTH_ENVIRONMENT
from .language_humanities import NODES as LANGUAGE_HUMANITIES
from .society_behavior import NODES as SOCIETY_BEHAVIOR
from .technology_engineering import NODES as TECHNOLOGY_ENGINEERING

DOMAIN_NODE_GROUPS = (
    LANGUAGE_HUMANITIES,
    FORMAL_NATURAL_SCIENCES,
    HEALTH_ENVIRONMENT,
    TECHNOLOGY_ENGINEERING,
    ECONOMY_LAW_POLITICS,
    SOCIETY_BEHAVIOR,
    ARTS_CULTURE,
    DAILY_LIFE,
)

NODES = [node for group in DOMAIN_NODE_GROUPS for node in group]

__all__ = ["DOMAIN_NODE_GROUPS", "NODES"]
