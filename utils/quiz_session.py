from datetime import datetime, timedelta

class QuizSession:
    def __init__(self, questions, duration_minutes=10):
        self.questions = questions
        self.answers = {}
        self.start_time = datetime.now()
        self.duration_minutes = duration_minutes
        self.is_submitted = False

    def submit(self):
        self.is_submitted = True

    def is_time_up(self):
        return datetime.now() > self.start_time + timedelta(minutes=self.duration_minutes)

    def get_score(self):
        correct = 0
        for i, q in enumerate(self.questions):
            if i in self.answers and self.answers[i] == q["answer"]:
                correct += 1
        return correct, len(self.questions)

    def get_percentage(self):
        correct, total = self.get_score()
        return (correct / total) * 100 if total > 0 else 0

    def get_weak_topics(self):
        weak = []
        correct, total = self.get_score()

        if self.get_percentage() < 60:
            for q in self.questions:
                weak.append(q.topic)

        return list(set(weak))

    def get_report(self):
        report = []
        for i, q in enumerate(self.questions):
            user_ans = self.answers.get(i, None)
            report.append({
                "question": q["question"],
                "correct": q["answer"],
                "user": user_ans,
                "is_correct": user_ans == q["answer"]
            })
        return report