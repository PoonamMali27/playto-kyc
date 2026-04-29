class KYCStateMachine:
    ALLOWED_TRANSITIONS = {
        "draft": ["submitted"],
        "submitted": ["under_review"],
        "under_review": ["approved", "rejected", "more_info_requested"],
        "more_info_requested": ["submitted"],
        "approved": [],
        "rejected": [],
    }

    @classmethod
    def validate_transition(cls, current_state, new_state):
        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, [])

        if new_state not in allowed:
            raise ValueError(
                f"Invalid transition from {current_state} to {new_state}"
            )