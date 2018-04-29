from collections import defaultdict
import numpy as np

# Each operation can be represented by a tuple consisting of the number of
# one's beads moved, five's beads moved, and ten's beads moved. Subtraction
# and addition are therefore covered.

OPERATION_COUNT = 27


class Operation(object):
    def __init__(self, ones, fives, tens):
        self.ones = ones
        self.fives = fives
        self.tens = tens

        self.validate()

        self._vector = np.zeros(
            OPERATION_COUNT,
            dtype=np.float64
        )
        self._vector[self.index] = 1

    @classmethod
    def from_add_index(cls, index):
        ones = (index % 9) - 4
        fives = index // 9 - 1
        tens = -((ones + 5 * fives) // 10)

        return cls(ones, fives, tens)

    @classmethod
    def from_sub_index(cls, index):
        ones = (index % 9) - 4
        fives = index // 9 - 1
        tens = -((ones + 5 * fives) // 10) - 1

        return cls(ones, fives, tens)

    def validate(self):
        assert isinstance(self.ones, int)
        assert isinstance(self.fives, int)
        assert isinstance(self.tens, int)

        assert -4 <= self.ones <= +4
        assert -1 <= self.fives <= 1
        assert -1 <= self.tens <= 1

        assert -9 <= self.effect <= +9

    @property
    def effect(self):
        """Returns an integer that represents how much the value changes
        when this operation is applied
        """
        return self.ones + 5 * self.fives + 10 * self.tens

    @property
    def index(self):
        """Returns an index between 0 and 26 associated with the
        operation. No two operations that have effects of the same
        sign will share an index. Useful for building vectors.
        """
        return 9 * (self.fives + 1) + (self.ones + 4)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '{}({x.ones}, {x.fives}, {x.tens})'.format(
            self.__class__.__name__, x=self
        )

    @property
    def vector(self):
        return self._vector


def digit_to_beads(digit):
    assert 0 <= digit <= 9
    ones = digit % 5
    fives = digit // 5
    return ones, fives

addition_ops = [
    Operation(ones, fives, -((ones + 5 * fives) // 10))
    for ones in range(-4, 5)
    for fives in range(-1, 2)
]

subtraction_ops = [
    Operation(ones, fives, -((ones + 5 * fives - 1) // 10) - 1)
    for ones in range(-4, 5)
    for fives in range(-1, 2)
]

add_natural_freq = np.zeros(OPERATION_COUNT, dtype=np.float64)
sub_natural_freq = np.zeros(OPERATION_COUNT, dtype=np.float64)

add_op_index_to_digit_pairs = defaultdict(list)
sub_op_index_to_digit_pairs = defaultdict(list)

for digit_1 in range(10):
    ones_1, fives_1 = digit_to_beads(digit_1)
    for digit_2 in range(10):
        add_result = digit_1 + digit_2
        add_ones, add_fives = digit_to_beads(add_result % 10)
        add_tens = add_result // 10
        add_op = Operation(add_ones - ones_1, add_fives - fives_1, add_tens)
        add_natural_freq[add_op.index] += 1
        add_op_index_to_digit_pairs[add_op.index].append((digit_1, digit_2))

        sub_result = digit_1 - digit_2
        sub_ones, sub_fives = digit_to_beads(sub_result % 10)
        sub_tens = sub_result // 10
        sub_op = Operation(sub_ones - ones_1, sub_fives - fives_1, sub_tens)
        sub_natural_freq[sub_op.index] += 1
        sub_op_index_to_digit_pairs[sub_op.index].append((digit_1, digit_2))


add_natural_freq /= 100.
sub_natural_freq /= 100.


def digit_pair_prob(
        op_freq,
        op_index_to_digit_pairs,
):
    p = np.zeros((10, 10), dtype=np.float32)

    assert np.abs(op_freq.sum() - 1.) < 1.e-06

    for op_index, digit_pairs in op_index_to_digit_pairs.items():
        for digit_1, digit_2 in digit_pairs:
            p[digit_1, digit_2] = (
                op_freq[op_index] / len(digit_pairs)
            )

    assert np.abs(p.sum() - 1.) < 1.e-06
    return p


def digit_vector_to_number(vec):
    num = 0
    for digit in vec:
        num += 10 * num + digit
    return num


def generate_mixed_problem(
        add_digit_pair_prob,
        add_prob,
        sub_digit_pair_prob,
        num_digits,
        num_operands
):
    assert num_operands > 1
    digits = np.arange(10)

    add_first_digit_prob = add_digit_pair_prob.sum(axis=1)
    sub_first_digit_prob = sub_digit_pair_prob.sum(axis=1)

    add_second_given_first_prob = (
        add_digit_pair_prob / add_first_digit_prob[:, None]
    )
    sub_second_given_first_prob = (
        sub_digit_pair_prob / sub_first_digit_prob[:, None]
    )

    operand_digits = np.zeros((num_operands, num_digits), dtype=np.int32)
    sum_digits = np.zeros((num_operands, num_digits + 1), dtype=np.int32)

    operand_rand = np.random.random(size=num_operands)

    for digit_n in range(num_digits - 1, -1, -1):
        for operand_n in range(1, num_operands):
            if operand_n == 1:
                operand_digits[0, digit_n] = np.random.choice(
                    digits,
                    p=add_first_digit_prob
                )

            if operand_rand[operand_n] <= add_prob:
                second_given_first_prob = add_second_given_first_prob
                sign = 1
            else:
                second_given_first_prob = sub_second_given_first_prob
                sign = -1
            s = (
                sum_digits[operand_n, digit_n + 1]
                + sum_digits[operand_n - 1, digit_n + 1]
                + operand_digits[operand_n - 1, digit_n]
            )
            sum_digits[operand_n, digit_n] = s // 10
            sum_digits[operand_n, digit_n + 1] = s % 10

            operand_digits[operand_n, digit_n] = sign * np.random.choice(
                digits,
                p=second_given_first_prob[
                    sum_digits[operand_n, digit_n + 1]
                ]
            )

    operands = [
        digit_vector_to_number(operand_digits[operand_n, :])
        for operand_n in range(num_operands)
    ]

    if sum(operands) < 0:
        mult = 10 ** num_digits
        operands[0] = operands[0] - mult * (sum(operands) // mult)

    return operands
