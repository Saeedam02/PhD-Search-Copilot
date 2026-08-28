import pytest

from phd_search_agent.models import OpportunityStatus
from phd_search_agent.state_machine import can_transition, validate_transition


def test_valid_transition():
    assert can_transition(OpportunityStatus.DISCOVERED, OpportunityStatus.VERIFIED)


def test_same_state_allowed():
    assert can_transition(OpportunityStatus.ELIGIBLE, OpportunityStatus.ELIGIBLE)


def test_invalid_jump_rejected():
    with pytest.raises(ValueError):
        validate_transition(OpportunityStatus.DISCOVERED, OpportunityStatus.SUBMITTED)
