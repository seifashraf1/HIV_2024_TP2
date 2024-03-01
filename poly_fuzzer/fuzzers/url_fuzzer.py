import random
from poly_fuzzer.common.abstract_seed import AbstractSeed
from poly_fuzzer.fuzzers.abstract_fuzzer import AbstractFuzzer
from poly_fuzzer.power_schedules.abstract_power_schedule import AbstractPowerSchedule
import numpy as np

class UrlFuzzer(AbstractFuzzer):
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
        self.mutators = [self._delete_random_character, self._replace_random_character, self._insert_random_character, self._insert_random_slash, self._insert_random_special_character, self._concatenate_random_slash, self._mutate_plus_to_space]

    def generate_input(self):

        """Mutate the seed to generate input for fuzzing.
        With this function we first use the gien seeds to generate inputs 
        and then we mutate the seeds to generate new inputs."""
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
        #
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

    def _insert_random_character(self, s):
        """Returns s with a random character inserted"""
        pos = random.randint(0, len(s))
        random_character = chr(random.randrange(32, 127))
        return s[:pos] + random_character + s[pos:]

    def _replace_random_character(self, s):
        """Returns s with a random character replaced"""
        if s == "":
            return ""
        pos = random.randint(0, len(s) - 1)
        random_character = chr(random.randrange(32, 127))
        return s[:pos] + random_character + s[pos + 1 :]

    #method to insert random slash
    def _insert_random_slash(self, s):
        pos = random.randint(0, len(s))
        return s[:pos] + '/' + s[pos:]

    #method to insert random special character
    def _insert_random_special_character(self, s):
        pos = random.randint(0, len(s))
        special_characters = ['&', '=', '?', '#', '%', ' ']
        special_character = random.choice(special_characters)
        return s[:pos] + special_character + s[pos:]

    #method to concatenate random slash and part of the string
    def _concatenate_random_slash(self, s):
        pos = random.randint(0, len(s))
        #get a random substring from the string
        random_substring = s[:pos]
        #concatenate the random substring with a slash and the end of the string
        return random_substring + '/' + s[pos:]

    def _mutate_plus_to_space(self, s):
        """Mutate string by replacing '+' with space"""
        return s.replace("+", " ")
