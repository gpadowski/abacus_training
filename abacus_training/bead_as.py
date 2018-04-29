import csv
import datetime
from enum import Enum
from functools import partial
import numpy as np
import os 
import pygame
import sys

from abacus_as import (
    display_abacus_add_subtract_problem,
    display_arabic_add_subtract_problem,
    format_operand,
    generate_problems,
    read_problem,
    storage_filename,
    write_problem_result,
)
from bead import (
    digitize,
    draw_columns,
    height_to_width,
    numerify,
)
from pygame_utilities import (
    display_centered_text,
    ENTER_KEYS,
    Menu,
    MenuChoice,
    NUMBER_TO_KEYS,
    NUMBER_KEYS,
)


os.environ['SDL_VIDEO_CENTERED'] = '1'

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 800
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

BLACK = (0x00, 0x00, 0x00)
GREEN = (0x00, 0xFF, 0x00)
GREY = (0xAA, 0xAA, 0xAA)
ORANGE = (0xFF, 0xA0, 0x00)


class NumberStyle(Enum):
    ABACUS = 1
    ARABIC = 2
    VERBAL = 3

def not_implemented():
    raise NotImplementedError()


def format_number(num):
    return '{: >+,}'.format(num)


def check_response(
        entered_digits,
        operands
):
    # Destructively modifies entered_digits!!!

    response = numerify(entered_digits)
    correct_response = sum(operands)
    return response == correct_response, response


def collect_digits(digit_list, key):
    if key in NUMBER_KEYS:
        digit_list.append(NUMBER_KEYS[key])
    elif key == pygame.K_BACKSPACE:
        try:
            digit_list.pop()
        except IndexError:
            pass
    else:
        pass


def give_problem(
        operands,
        result_file,
        font_size=100,
        frames_per_second=20,
        font=None,
        bead_color=GREEN,
        separator_bead_color=ORANGE,
        prior_response_time=None,
        number_style=NumberStyle.ARABIC,
        language='en',
):
    if font is None:
        font = pygame.font.SysFont(
            'Lucida Console', font_size
        )
    column_width = height_to_width(font_size)

    clock = pygame.time.Clock()

    entered_digits = []
    correct_response = sum(operands)

    # wait for start
    while True:
        screen.fill(BLACK)

        exit_while = False
        if prior_response_time:
            display_centered_text(
                screen,
                '{:.2f}'.format(prior_response_time),
                bead_color,
                font,
            )
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return True, None
                start_time = pygame.time.get_ticks() 
                exit_while = True
        if exit_while:
            break

        pygame.display.flip()
        clock.tick(frames_per_second)
        
    # present problem and collect response

    read = True
    
    while True:
    # verbal reading of the problem must occur outside of this loop
        if read and number_style == NumberStyle.VERBAL:
            read_problem(
                operands,
                inter_operand_pause=2.,
                language=language
            )
            read = False
            
        screen.fill(BLACK)
        if number_style == NumberStyle.ABACUS:
            x_response, y_response = display_abacus_add_subtract_problem(
                screen,
                bead_color,
                separator_bead_color,
                (25, 25),
                font_size,
                operands,
                font=font,
            )
            draw_columns(
                screen,
                bead_color,
                (x_response - len(entered_digits) * column_width,
                 y_response),
                font_size,
                entered_digits,
                separator_bead_color=separator_bead_color,
            )
        elif number_style == NumberStyle.ARABIC:
            x_response, y_response, width = display_arabic_add_subtract_problem(
                screen,
                bead_color,
                operands,
                font
            )
            surface = font.render(
                format_operand(numerify(entered_digits)),
                True,
                bead_color
            )
            screen.blit(
                surface,
                (x_response + width - surface.get_width(), y_response)
            )
        elif number_style == NumberStyle.VERBAL:
            display_centered_text(
                screen,
                format_number(numerify(entered_digits)),
                bead_color,
                font,
            )
        else:
            pass

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                collect_digits(entered_digits, event.key)

                if event.key in ENTER_KEYS:
                    response_time = (
                        pygame.time.get_ticks() - start_time
                    ) / 1000.
                    correct, response = check_response(
                        entered_digits,
                        operands
                    )
                    write_problem_result(
                        result_file,
                        operands,
                        response,
                        response_time,
                        correct,
                        number_style,
                    )
                    if correct:
                        return False, response_time
                    else:
                        start_time = pygame.time.get_ticks()
                        entered_digits.clear()
                        read = True
                elif event.key == pygame.K_q:
                    return True, None
                else:
                    pass
                    
        pygame.display.flip()
        clock.tick(frames_per_second)

def add_subtract(
        number_style=NumberStyle.ARABIC,
        language=None,
):
    problems = generate_problems()
    response_time = None

    with open(storage_filename(), 'a') as result_file:
        while True:
            end, response_time = give_problem(
                next(problems),
                result_file,
                prior_response_time=response_time,
                number_style=number_style,
                language=language,
            )
            if end:
                break

def abacus_reading_problem(
        result_file,
        display_digits,
        flash_seconds,
        font,
        fps=20,
):
    n_digits = len(display_digits)
    column_width = height_to_width(font.get_height())
    clock = pygame.time.Clock()
    
    x_display = .5 * (
        SCREEN_WIDTH - n_digits * column_width
    )
    y_display = .5 * (SCREEN_HEIGHT - font.get_height())

    # display number for specified period of time
    screen.fill(BLACK)
    draw_columns(
        screen,
        GREY,
        # GREEN,
        (x_display, y_display),
        font.get_height(),
        display_digits,
        separator_bead_color=ORANGE,
    )
    pygame.display.flip()
    pygame.time.wait(int(1000 * flash_seconds))

    # get response
    entered_digits = []
    clock = pygame.time.Clock()
    break_out = False
    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                collect_digits(entered_digits, event.key)
                if event.key in ENTER_KEYS:
                    break_out = True
                    is_correct = (
                        entered_digits == display_digits
                    )
        if break_out:
            break

        x_display = .5 * (
            SCREEN_WIDTH - len(entered_digits) * column_width
        )
        draw_columns(
            screen,
            GREY,
            # GREEN,
            (x_display, y_display),
            font.get_height(),
            entered_digits,
            separator_bead_color=ORANGE,
        )
        pygame.display.flip()
        clock.tick(fps)

    # Display whether correct or not
    screen.fill(BLACK)
    display_centered_text(
        screen,
        'Correct' if is_correct else 'Incorrect',
        GREY,
        font,
    )
    pygame.display.flip()
    pygame.time.wait(750)

    return is_correct, numerify(entered_digits)


def abacus_reading(
        n_digits=5
):
    font = pygame.font.SysFont('Lucida Console', 100)
    flash_seconds = 1.
    result_filename = datetime.date.today().strftime(
        '%Y_%m_%d_abacus_reading.dat'
    )
    with open(result_filename, 'a') as result_file:
        csv_file = csv.writer(result_file, delimiter=',')

        while True:
            number = np.random.randint(
                10 ** (n_digits - 1),
                10 ** n_digits
            )
            digits = digitize(number)

            is_correct, response = abacus_reading_problem(
                result_file,
                digits,
                flash_seconds,
                font
            )

            csv_file.writerow([
                datetime.datetime.now().strftime(
                    '%Y-%m-%d-%H:%M:%S'
                ),
                number,
                response,
                '{:.3f}'.format(flash_seconds),
                is_correct,
            ])

            if is_correct:
                flash_seconds *= .95
            else:
                flash_seconds *= 1.1

            # See if user wants to do another
            screen.fill(BLACK)
            while True:
                break_out = False
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            return
                        else:
                            break_out = True
                if break_out:
                    break

if __name__ == '__main__':
    screen = pygame.display.set_mode(SCREEN_SIZE)

    pygame.font.init()
    pygame.init()
    pygame.display.set_caption('Abacus Training')

    background_color = BLACK
    foreground_color = GREEN
    menu_font = pygame.font.SysFont('Lucida Console', 40)
    frames_per_second = 20
    
    menu_args = [
        screen,
        background_color,
        foreground_color,
        menu_font,
        frames_per_second,
    ]

    main_menu = None
    addition_subtraction_menu = None
    abacus_reading_menu = None
    verbal_menu = None

    BACK = object()

    abacus_reading_menu = Menu(
        'Number of Digits',
        [MenuChoice(
            '({}) Digit{}'.format(d, 's' if d > 1 else ''),
            NUMBER_TO_KEYS[d],
            partial(abacus_reading, n_digits=d),
        ) for d in range(1, 10)
        ] + [MenuChoice('(B) Back', [pygame.K_b], BACK)],
    )

    verbal_menu = Menu(
        'Language',
        [MenuChoice('(1) English', NUMBER_TO_KEYS[1], 'en'),
         MenuChoice('(2) Mandarin', NUMBER_TO_KEYS[2], 'zh-CN'),
         MenuChoice('(3) French', NUMBER_TO_KEYS[3], 'fr'),
         MenuChoice('(4) German', NUMBER_TO_KEYS[4], 'de'),
         MenuChoice('(5) Japanese', NUMBER_TO_KEYS[5], 'ja'),
         MenuChoice('(B) Back', [pygame.K_b], BACK),
         MenuChoice('(Q) Quit', [pygame.K_q],
                    partial(sys.exit, 0)),
        ],
    )

    def add_subtract_speech():
        result = verbal_menu.present(
            *menu_args,
        )
        if result() is BACK:
            return

        add_subtract(
            number_style=NumberStyle.VERBAL,
            language=result()
        )
    
    addition_subtraction_menu = Menu(
        'Operand Presentation Style',
        [
            MenuChoice(
                '(1) Abacus',
                NUMBER_TO_KEYS[1],
                partial(
                    add_subtract,
                    number_style=NumberStyle.ABACUS
                ),
            ),
            MenuChoice(
                '(2) Arabic numerals',
                NUMBER_TO_KEYS[2],
                partial(
                    add_subtract,
                    number_style=NumberStyle.ARABIC
                ),
            ),
            MenuChoice(
                '(3) Speech',
                NUMBER_TO_KEYS[3],
                add_subtract_speech,
            ),
            MenuChoice(
                '(B) Back', [pygame.K_b], BACK
            ),
            MenuChoice(
                '(Q) Quit', [pygame.K_q], partial(sys.exit, 0)
            ),
        ],
    )
    main_menu = Menu(
        'Main Menu',
        [MenuChoice(
            '(1) Addition and Subtraction',
            NUMBER_TO_KEYS[1],
            partial(
                addition_subtraction_menu.present_loop,
                *menu_args,
                exit_condition=lambda fn: fn is BACK
            )
        ),
        MenuChoice(
            '(2) Multiplication',
            NUMBER_TO_KEYS[2],
            not_implemented,
        ),
        MenuChoice(
            '(3) Division',
            NUMBER_TO_KEYS[3],
            not_implemented,
        ),
        MenuChoice(
            '(4) Abacus Reading',
            NUMBER_TO_KEYS[4],
            partial(
                abacus_reading_menu.present_loop,
                *menu_args,
                exit_condition=lambda fn: fn is BACK
            )
        ),
        MenuChoice(
            '(Q) Quit',
            [pygame.K_q],
            partial(sys.exit, 0)
        )],
    )

    main_menu.present_loop(
        screen,
        BLACK,
        GREEN,
        menu_font,
    )
