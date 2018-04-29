import datetime
import glob
from google_speech import Speech
import numpy as np
import pandas as pd
from pygame.draw import polygon
from pygame.font import SysFont
from pygame_utilities import display_centered_text
import time

from bead import (
    digitize,
    draw_columns,
    height_to_width,
)
import operation as op


AS_SUFFIX = '_abacus_as.dat'
DATE_FORMAT = '%Y_%m_%d'


def get_data_filenames(suffix=AS_SUFFIX):
    return glob.glob('*' + suffix)


def date_to_filename(
        dt,
        suffix=AS_SUFFIX
):
    return dt.strftime(DATE_FORMAT) + suffix


def storage_filename():
    return date_to_filename(datetime.date.today())


# Get listing of appropriate data files by date
def get_dataset_dates(suffix=AS_SUFFIX):
    dates = []
    fns = get_data_filenames(suffix=suffix)

    for fn in fns:
        dt = datetime.datetime.strptime(
            fn.split(suffix)[0], DATE_FORMAT
        ).date()
        dates.append(dt)
    dates.sort()

    return dates


def read_as_data(date):
    return pd.read_csv(
        date_to_filename(date, suffix=AS_SUFFIX),
        delimiter=',',
        header=None,
        names=[
            'problem',
            'response_time',
            'response',
            'correct',
            'time_of_day',
            'presentation_method',
        ]
    )


def write_problem_result(
        stream,
        operands,
        response,
        response_time,
        is_correct,
        number_style,
):
    # n1, n2, time, answer, correct?
    stream.write(
        '{},{:.2f},{},{},{},{}\n'.format(
            ';'.join(map(str, operands)),
            response_time,
            response,
            is_correct,
            datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'),
            number_style.name,
        )
    )


def generate_problems(
        addition_prob=.5,
        num_digits=6,
        num_operands=5,
        new_problem_prob=.5,
        previous_incorrect_prob=.4,
        previous_slow_prob=.1,
):
    if new_problem_prob + previous_incorrect_prob + previous_slow_prob != 1.:
        raise ValueError('Problem selection probabilities must sum to 1.')

    dates = get_dataset_dates()

    add_digit_pair_prob = op.digit_pair_prob(
        np.ones(op.OPERATION_COUNT) / op.OPERATION_COUNT,
        op.add_op_index_to_digit_pairs
    )
    sub_digit_pair_prob = op.digit_pair_prob(
        np.ones(op.OPERATION_COUNT) / op.OPERATION_COUNT,
        op.sub_op_index_to_digit_pairs
    )

    while True:
        rand = np.random.random()

        # decide whether to generate a new problem or give a problem where
        # the answer was previously incorrect or the response was slow
        if not dates or 0 <= rand < new_problem_prob:
            operands = op.generate_mixed_problem(
                add_digit_pair_prob,
                addition_prob,
                sub_digit_pair_prob,
                num_digits,
                num_operands,
            )
        else:
            date = np.random.choice(dates)
            df = read_as_data(date)
            incorrect_df = df[df.correct == False]  # noqa: E712

            # choose a problem where the response was wrong, if possible1
            if (
                    incorrect_df.shape[0] > 0
                    and 0. <= rand - new_problem_prob < previous_incorrect_prob
            ):
                row_n = np.random.randint(low=0, high=incorrect_df.shape[0])
                operands = map(
                    int,
                    incorrect_df.iloc[row_n].problem.split(';')
                )
                print('Failure from {}'.format(date))
            else:
                groups = df.groupby('problem')
                if not groups:
                    continue
                max_time_series = groups.response_time.max()
                total_max_time = sum(max_time_series)
                row_n = np.random.choice(
                    max_time_series.shape[0],
                    p=max_time_series / total_max_time
                )
                operands = map(int, max_time_series.index[row_n].split(';'))
                print('Slow response {} from {}'.format(
                    max_time_series.iloc[row_n],
                    date
                ))
        yield list(operands)


def format_operand(operand):
    return '{: >+10,}'.format(operand)


def display_arabic_add_subtract_problem(
        screen,
        color,
        operands,
        font
):
    operand_rows = [
        format_operand(operand) for operand in operands
    ]
    max_length = max(len(row) for row in operand_rows)
    operand_rows.append('-' * max_length)

    text = '\n'.join(operand_rows)

    response_x, response_y, width = display_centered_text(
        screen,
        text,
        color,
        font,
    )

    return response_x, response_y, width


def display_abacus_add_subtract_problem(
        screen,
        color,
        separator_bead_color,
        upper_left,
        height,
        operands,
        line_spacing=1.2,
        font=None,
):
    if font is None:
        font = SysFont('Lucida Console', height)
    x_ul, y_ul = upper_left
    max_digits = max(
        len(digitize(operand))
        for operand in operands
    )
    column_width = height_to_width(height)
    max_sign_width = 0.

    for row_n, operand in enumerate(operands):
        x_row = x_ul
        y_row = y_ul + row_n * height * line_spacing

        digits = digitize(abs(operand))
        n_digits = len(digits)

        sign = '+' if operand >= 0 else '-'
        sign_surface = font.render(sign, True, color)
        sign_width = sign_surface.get_width()

        max_sign_width = max(sign_width, max_sign_width)

        screen.blit(
            sign_surface,
            (x_row, y_row)
        )

        draw_columns(
            screen,
            color,
            (
                x_row
                + sign_width
                + (max_digits - n_digits) * column_width,
                y_row
            ),
            height,
            digits,
            separator_bead_color=separator_bead_color,
        )

    row_n = len(operands)
    x_rect_left = x_ul
    x_rect_right = (
        x_ul
        + max_sign_width
        + max_digits * column_width
    )
    y_rect_top = (
        y_ul
        + height * (row_n * line_spacing
                    - .25 * (line_spacing - 1.))
    )
    y_rect_bottom = (
        y_rect_top
        + .25 * (line_spacing - 1.) * height
    )

    polygon(
        screen,
        color,
        [
            (x_rect_left, y_rect_top),
            (x_rect_right, y_rect_top),
            (x_rect_right, y_rect_bottom),
            (x_rect_left, y_rect_bottom),
        ]
    )

    # coordinates of where to draw the rightmost digit
    # of the response
    return (
        (
            x_ul
            + sign_width
            + max_digits * column_width
        ),
        y_ul + row_n * height * line_spacing
    )


def read_problem(
        operands,
        inter_operand_pause=1.5,
        language='en',
):
    speeches = []
    for operand in operands:
        speeches.append(Speech(str(operand), language))

    for speech in speeches:
        speech.play(None)
        time.sleep(inter_operand_pause)
