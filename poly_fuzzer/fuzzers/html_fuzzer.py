from poly_fuzzer.fuzzers.abstract_fuzzer import AbstractFuzzer
import random
import numpy as np
from poly_fuzzer.common.abstract_seed import AbstractSeed
from poly_fuzzer.power_schedules.abstract_power_schedule import AbstractPowerSchedule


class HtmlFuzzer(AbstractFuzzer):

    def __init__(
        self,
        executor,
        seeds: list[AbstractSeed],
        power_schedule: AbstractPowerSchedule = None,
        min_mutations: int = 1,
        max_mutations: int = 10,
    ):
        super().__init__(executor)
        self.seeds = seeds
        self.seed_index = 0
        self.executor = executor
        self.seed_index = 0
        self.power_schedule = power_schedule
        self.min_mutations = min_mutations
        self.max_mutations = max_mutations
        self.mutators = [
            self._delete_random_character,
            self._replace_random_character,
            self._replace_body_content,
            self._generate_random_html_content,
        ]

    def generate_input(self):
        """
        Mutate the seed to generate input for fuzzing.
        With this function, we first use the given seeds to generate inputs,
        and then we mutate the seeds to generate new inputs.
        """
        if self.seed_index < len(self.seeds):
            # Still seeding
            inp = self.seeds[self.seed_index].data
            self.seed_index += 1
        else:
            # Mutating
            inp = self._create_candidate()

        return inp

    def _update(self, input):
        """Update the fuzzer with the input and its coverage."""
        if len(self.data["coverage"]) > 1:
            if self.data["coverage"][-1] > self.data["coverage"][-2]:
                seed = AbstractSeed(input)
                seed.coverage = self.data["coverage"][-1]
                seed.execution_time = self.data["execution_times"][-1]
                self.seeds.append(seed)

    def _create_candidate(self):
        seed = np.random.choice(self.seeds)

        # Stacking: Apply multiple mutations to generate the candidate
        if self.power_schedule:
            candidate = self.power_schedule.choose(self.seeds).data
        else:
            candidate = seed.data
        # Apply power schedule to generate the candidate
        trials = random.randint(self.min_mutations, self.max_mutations)
        for i in range(trials):
            candidate = self.mutate(candidate)
        return candidate

    def mutate(self, s):
        """Return s with a random mutation applied"""
        mutator = random.choice(self.mutators)
        return mutator(s)

    def _delete_random_character(self, s):
        """Returns s with a random character deleted"""
        if len(s) > 5:
            pos = random.randint(0, len(s) - 1)
            return s[:pos] + s[pos + 1 :]
        else:
            return s

    def _replace_random_character(self, s):
        """Returns s with a random character replaced"""
        if s == "":
            return ""
        pos = random.randint(0, len(s) - 1)
        random_character = chr(random.randrange(32, 127))
        return s[:pos] + random_character + s[pos + 1 :]

    def _replace_body_content(self, s):
        """Replaces content within the <body> tag with a random string"""
        body_start = s.find("<body>")
        body_end = s.find("</body>") + len("</body>")
        if body_start != -1 and body_end != -1:
            body_content = s[body_start:body_end]
            new_content = self._generate_random_html_content()
            return s.replace(body_content, new_content, 1)
        return s

    def _generate_random_html_content(self):
        """Generates random HTML content"""
        # You can customize this method based on your requirements
        return "<p>" + "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10)) + "</p>"
