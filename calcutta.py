#!/usr/bin/env python

import math


def ratio_to_cents(f1, f2):
    return 1200 * math.log(float(f1) / float(f2), 2)


def get_fibonacci_ratios():
    results = []
    a, b = 1, 2
    last_ratio = 1.0
    while True:
        ratio = float(b) / a
        results.append((a, b, ratio))
        diff = abs(ratio - last_ratio)
        if diff < 0.0000000000000001:
            return results
        a, b = b, a + b
        last_ratio = ratio


def divide_interval(lower_bottom=0, total_interval=4811.271151650251, ratio=1.618033988749895):
    interval = total_interval / float(ratio)

    lower_top = lower_bottom + interval

    upper_top = lower_bottom + total_interval
    upper_bottom = upper_top - interval

    return [(lower_bottom, lower_top), (upper_bottom, upper_top)]


def build_structure(base=0, interval=4811.271151650251, ratio=1.618033988749895):
    levels = [[(base, interval + base)]]
    for _ in range(4):
        level = []
        for bottom, top in levels[-1]:
            level.extend(divide_interval(bottom, top - bottom, ratio))
        levels.append(level)

    return levels


class Calcutta(object):
    def __init__(self):
        self.ratios = get_fibonacci_ratios()
        self.golden_ratio = self.ratios[-1][-1]

        # The outer interval is 4811.271151650251 cents.
        # When subdivided several times into intervals with fibonacci ratios
        # between interval sizes, this creates "triads" with in-tune fifths and
        # slightly sharp major thirds.
        self.fifth = ratio_to_cents(3, 2)
        self.outer_interval = self.fifth * (self.golden_ratio ** 4)

        self.structures = []
        self.harmonies = []

        self.main()

    def main(self):
        base = 4800  # Lowest pitch
        for _, _, ratio in self.ratios:
            structure = build_structure(base, self.outer_interval, ratio)
            self.structures.append(structure)

            harmony = []
            for pitches in structure[-1]:
                harmony.extend(pitches)
            # harmony = [round(h, 5) for h in harmony]
            # harmony = list(set(harmony))
            harmony.sort()
            harmony = [h / 100 for h in harmony]
            self.harmonies.append(harmony)

    # def play(self):
    #     for harmony in self.harmonies:
    #         synthesize(2.0, harmony)


if __name__ == '__main__':
    calcutta = Calcutta()
    for harmony in calcutta.harmonies:
        print ', '.join([str(h) for h in harmony])
    # calcutta.play()
