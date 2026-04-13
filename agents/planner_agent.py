def plan_next_step(history):
    """
    Decide what to do next based on performance
    """

    if not history:
        return "teach"

    last = history[-1]

    if last["score"] < 0.6:
        return "reteach"

    return "test"