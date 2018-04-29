from pygame.draw import (
    polygon,
)
from pygame.gfxdraw import (
    aapolygon,
    filled_polygon,
)
from pygame_utilities import (
    display_centered_text,
    format_number,
)

BEAD_HEIGHT = .75
BEAD_FLAT = BEAD_HEIGHT * .5 / 1.6
BEAD_DIAMETER = 1.3

COLUMN_HEIGHT = 5.
COLUMN_WIDTH = 15 / 11.
COLUMN_HEAVEN_HEIGHT = 1.2
COLUMN_EARTH_HEIGHT = 3.6
COLUMN_RECKONING_BAR_HEIGHT = .2
COLUMN_ROD_DIAMETER = .67 * BEAD_FLAT

PROBLEM_LINE_HEIGHT = .05

def draw_bead(
        screen,
        color,
        center,
        height,
):
    scale = height / BEAD_HEIGHT

    bead_diameter = scale * BEAD_DIAMETER
    bead_flat = scale * BEAD_FLAT
    bead_height = height

    # start drawing polygon at rightmost part and proceed counterclockwise
    x_c, y_c = center
    points = [
        (x_c + .5 * bead_diameter, y_c),
        (x_c + .5 * bead_flat, y_c + .5 * bead_height),
        (x_c - .5 * bead_flat, y_c + .5 * bead_height),
        (x_c - .5 * bead_diameter, y_c),
        (x_c - .5 * bead_flat, y_c - .5 * bead_height),
        (x_c + .5 * bead_flat, y_c - .5 * bead_height),
    ]
    aapolygon(screen, points, color)
    filled_polygon(screen, points, color)

def draw_column(
        screen,
        color,
        upper_left,
        height,
        value,  # digit to display in column
        separator_bead_color=None,
        is_separator_column=False,
):
    scale = height / COLUMN_HEIGHT
    on_center_spacing = scale * COLUMN_WIDTH
    bead_height = scale * BEAD_HEIGHT
    
    x_ul, y_ul = upper_left
    x_c = x_ul + .5 * on_center_spacing
    y_top = y_ul
    y_bottom = y_ul + height

    fives, ones = divmod(value, 5)

    # draw rod
    polygon(
        screen,
        color,
        [
            (x_c - .5 * scale * COLUMN_ROD_DIAMETER, y_ul),
            (x_c + .5 * scale * COLUMN_ROD_DIAMETER, y_ul),
            (x_c + .5 * scale * COLUMN_ROD_DIAMETER, y_ul + scale * COLUMN_HEIGHT),
            (x_c - .5 * scale * COLUMN_ROD_DIAMETER, y_ul + scale * COLUMN_HEIGHT)
        ]
    )

    # draw reckoning bar
    polygon(
        screen,
        color,
        [
            (x_c - .5 * on_center_spacing, y_ul + scale * COLUMN_HEAVEN_HEIGHT),
            (x_c - .5 * on_center_spacing, y_ul + scale * (COLUMN_HEAVEN_HEIGHT + COLUMN_RECKONING_BAR_HEIGHT)),
            (x_c + .5 * on_center_spacing, y_ul + scale * (COLUMN_HEAVEN_HEIGHT + COLUMN_RECKONING_BAR_HEIGHT)),
            (x_c + .5 * on_center_spacing, y_ul + scale * COLUMN_HEAVEN_HEIGHT)
        ]
    )
    
    # draw heaven bead
    if fives == 0:
        # touching top of abacus
        y_heaven = y_ul + .5 * bead_height
    else:
        # touching reckoning bar
        y_heaven = y_ul + scale * COLUMN_HEAVEN_HEIGHT - .5 * bead_height

    draw_bead(screen, color, (x_c, y_heaven), bead_height)

    # draw earth beads touching the reckoning bar
    for bead_n in range(ones):
        if bead_n == 0 and is_separator_column:
            bead_color = separator_bead_color
        else:
            bead_color = color

        y_earth = (
            y_ul
            + scale * (COLUMN_HEAVEN_HEIGHT + COLUMN_RECKONING_BAR_HEIGHT)
            + (.5 + bead_n) * bead_height
        )
        draw_bead(
            screen,
            bead_color,
            (x_c, y_earth),
            bead_height
        )

    # draw earth beads touching the bottom of the abacus
    for bead_n in range(4 - ones):
        if bead_n == 3 and is_separator_column:
            bead_color = separator_bead_color
        else:
            bead_color = color
        y_earth = (
            y_ul
            + scale * COLUMN_HEIGHT
            - (.5 + bead_n) * bead_height
        )
        draw_bead(
            screen,
            bead_color,
            (x_c, y_earth),
            bead_height
        )


def digitize(integer):
    remaining_value = integer
    digits = []

    while remaining_value > 0:
        remaining_value, digit = divmod(remaining_value, 10)
        digits.append(digit)
    digits.reverse()
    
    return digits

def numerify(digits):
    number = 0
    multiplier = 1
    
    for digit in reversed(digits):
        number += multiplier * digit
        multiplier *= 10

    return number

def height_to_width(height):
    return COLUMN_WIDTH * (height / COLUMN_HEIGHT)

def draw_columns(
        screen,
        color,
        upper_left,
        height,
        digits,
        separator_bead_color=None
):
    if separator_bead_color is None:
        separator_bead_color = color

    column_width = height_to_width(height)
    x_ul, y_ul = upper_left
    n_digits = len(digits)
    
    for digit_n, digit in enumerate(digits):
        is_separator_column = (
            (n_digits - 1 - digit_n) % 3 == 0
        )

        draw_column(
            screen,
            color,
            (x_ul + digit_n * column_width, y_ul),
            height,
            digit,
            separator_bead_color=separator_bead_color,
            is_separator_column=is_separator_column,
        )

_all_ = [
    digitize,
    draw_bead,
    draw_column,
    draw_columns,
]

