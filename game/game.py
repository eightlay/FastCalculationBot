from random import randint


class Game:
    LEFT_FROM = 10
    RIGHT_FROM = 2
    MIN_VALS = {
        "difficulty": 1,
        "max_multiplier": 2,
        "problems_per_round": 1,
        "number_of_rounds": 1,
    }

    def __init__(
        self,
        difficulty: int,
        max_multiplier: int,
        problems_per_round: int,
        number_of_rounds: int,
    ) -> None:
        self.check_input("difficulty", difficulty)
        self.check_input("max_multiplier", max_multiplier)
        self.check_input("problems_per_round", problems_per_round)
        self.check_input("number_of_rounds", number_of_rounds)

        self.difficulty = 10 ** (difficulty + 1) - 1
        self.max_multiplier = max_multiplier
        self.problems_per_round = problems_per_round
        self.number_of_rounds = number_of_rounds

        self.current_round = 0
        self.finished = False

        self.history = set([])
        self.questions = []
        self.answers = []

    def check_input(self, param_name: str,  val: int) -> None:
        min_val = Game.MIN_VALS[param_name]
        if val < min_val:
            raise Exception(f"{param_name} must be {min_val} or greater")

    def get_questions(self) -> tuple[bool, str]:
        if self.generate():
            return False, self.to_str()
        return True, ""

    def generate(self) -> bool:
        if self.finished:
            return False

        self.clear()
        self.generate_questions()
        self.check_round()

        return True

    def clear(self) -> None:
        self.questions.clear()
        self.answers.clear()

    def generate_questions(self) -> None:
        i = 0

        while i < self.problems_per_round:
            i += 1

            left = randint(Game.LEFT_FROM, self.difficulty)
            right = randint(Game.RIGHT_FROM, self.max_multiplier)
            question = (str(left), str(right))

            if question in self.history:
                i -= 1
                continue

            self.history.add(question)
            self.questions.append(question)
            self.answers.append(left * right)

    def to_str(self, results: list[str] | None = None) -> str:
        width_left, width_right = self.get_widths()
        answers_str = [str(a) for a in self.answers]
        width_answer = len(max(answers_str, key=len))
        questions = []

        for i, (left, right) in enumerate(self.questions):
            question = f"`{left.ljust(width_left)} * {right.ljust(width_right)}"

            if results:
                question += f" = {answers_str[i].ljust(width_answer)} ({results[i]})"

            question += "`"

            questions.append(question)

        return "\n".join(questions)

    def get_widths(self) -> tuple[int, int]:
        return self.get_width(0), self.get_width(1)

    def get_width(self, ind: int) -> int:
        return len(max(self.questions, key=lambda q: len(q[ind]))[ind])

    def check_round(self) -> None:
        self.current_round += 1
        self.finished = self.current_round >= self.number_of_rounds

    def check_answers(self, answers: str) -> str:
        results = self.get_results(answers)
        return self.to_str(results)

    def get_results(self, answers: str) -> list[str]:
        results = ['-' for _ in range(len(self.answers))]

        for i, answer in enumerate(answers.split("\n")):
            if i >= len(self.answers):
                break

            try:
                result = int(answer.replace(" ", "")) == self.answers[i]
                result = '+' if result else f'-'
            except ValueError:
                result = '-'

            results[i] = result

        return results
