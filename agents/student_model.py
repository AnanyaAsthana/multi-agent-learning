class StudentModel:
    def __init__(self):
        self.state = {}

    def init_topic(self, topic):
        if topic not in self.state:
            self.state[topic] = {
                "mastery": 0.3,
                "history": [],
                "weak_areas": [],
                "attempts": 0
            }

    def update(self, topic, score, mistakes):
        data = self.state[topic]

        # update attempts
        data["attempts"] += 1

        # update mastery (simple moving average)
        data["mastery"] = (data["mastery"] * (data["attempts"] - 1) + score) / data["attempts"]

        # update weak areas
        data["weak_areas"].extend(mistakes)

    def get_mastery(self, topic):
        return self.state[topic]["mastery"]

    def get_state(self, topic):
        return self.state[topic]