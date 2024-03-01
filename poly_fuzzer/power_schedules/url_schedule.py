from poly_fuzzer.common.abstract_seed import AbstractSeed
import random


class UrlSchedule():
    def __init__(self):
        """Constructor"""
        #self.seeds = [AbstractSeed(data) for data in seeds_data]
        self.path_frequency: dict = {}

    def _assign_energy(self, seeds: list[AbstractSeed]) -> None:
        """Assigns each seed the same energy"""
        #energy assignment algorithm to assign energy for seed based on the seed's length, execution time and coverage
        #it will use weighted sum of the three factors
        coverage_weight = 0.5
        length_weight = 0.3
        execution_time_weight = 0.2
        normalized_seeds = self.normalize_seeds(seeds)

        for seed in normalized_seeds:
            seed.energy = (seed.length * length_weight) + (seed.execution_time * execution_time_weight) + (seed.coverage * coverage_weight)

        return seeds

    def normalize(self, attribute_list):
        #min-max normalization
        min_val = min(attribute_list)
        max_val = max(attribute_list)

        if min_val == max_val:
            return [0.0] * len(attribute_list)

        normalized_values = [
            (val - min_val) / (max_val - min_val) for val in attribute_list
        ]

        return normalized_values

    def _normalized_energy(self, seeds: list[AbstractSeed]) -> list[float]:
        """Normalize energy"""
        energy = [seed.energy for seed in seeds]
        sum_energy = sum(energy)  # Add up all values in energy
        assert sum_energy != 0
        norm_energy = [nrg / sum_energy for nrg in energy]
        return norm_energy

    def choose(self, seeds: list[AbstractSeed]) -> AbstractSeed:
        """Choose weighted by normalized energy."""
        seeds = self._assign_energy(seeds)
        norm_energy = self._normalized_energy(seeds)
        seed = random.choices(seeds, weights=norm_energy)[0]
        return seed

    def normalize_seeds(self, seeds: list[AbstractSeed]) -> list[float]:
        lengths = [seed.length for seed in seeds]
        execution_times = [seed.execution_time for seed in seeds]
        coverages = [seed.coverage for seed in seeds]

        #normalize attributes (scaling to the range [0, 1])
        normalized_lengths = self.normalize(lengths)
        normalized_execution_times = self.normalize(execution_times)
        normalized_coverages = self.normalize(coverages)

        normalized_seeds = [
            {
                'length': length,
                'execution_time': execution_time,
                'coverage': coverage,
            }
            for length, execution_time, coverage in zip(
                normalized_lengths, normalized_execution_times, normalized_coverages
            )
        ]

        for seed, normalized_seed in zip(seeds, normalized_seeds):
            seed.length = normalized_seed['length']
            seed.execution_time = normalized_seed['execution_time']
            seed.coverage = normalized_seed['coverage']

        return seeds