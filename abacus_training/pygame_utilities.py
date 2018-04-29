import pygame
from typing import List

NUMBER_TO_KEYS = [
    {pygame.K_0, pygame.K_KP0},
    {pygame.K_1, pygame.K_KP1},
    {pygame.K_2, pygame.K_KP2},
    {pygame.K_3, pygame.K_KP3},
    {pygame.K_4, pygame.K_KP4},
    {pygame.K_5, pygame.K_KP5},
    {pygame.K_6, pygame.K_KP6},
    {pygame.K_7, pygame.K_KP7},
    {pygame.K_8, pygame.K_KP8},
    {pygame.K_9, pygame.K_KP9},
]

NUMBER_KEYS = {
    pygame.K_0: 0,
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 4,
    pygame.K_5: 5,
    pygame.K_6: 6,
    pygame.K_7: 7,
    pygame.K_8: 8,
    pygame.K_9: 9,
    pygame.K_KP0: 0,
    pygame.K_KP1: 1,
    pygame.K_KP2: 2,
    pygame.K_KP3: 3,
    pygame.K_KP4: 4,
    pygame.K_KP5: 5,
    pygame.K_KP6: 6,
    pygame.K_KP7: 7,
    pygame.K_KP8: 8,
    pygame.K_KP9: 9,
}

ENTER_KEYS = {pygame.K_KP_ENTER, pygame.K_RETURN}


def format_number(num, columns=10):
    format_string = '\{: >+{},\}'.format(columns)
    return format_string.format(num)


def display_centered_text(
        screen,
        text,
        color,
        font,
):
    lines = text.split('\n')
    surfaces = []
    width = 0.
    height = 0.

    for line in lines:
        surface = font.render(line, True, color)
        surfaces.append(surface)

        width = max(width, surface.get_width())
        height += surface.get_height()

    text_x = .5 * (screen.get_width() - width)
    for line_n, surface in enumerate(surfaces):
        text_y = .5 * (
            screen.get_height()
            - height
        ) + line_n * (height / len(lines))

        screen.blit(
            surface,
            (text_x, text_y)
        )

    text_y = (
        .5 * (screen.get_height() - height)
        + len(surfaces) * (height / len(lines))
    )

    return text_x, text_y, width


class MenuChoice(object):
    def __init__(
            self,
            text,
            keys,
            result,
    ):
        self.text = text
        self.keys = keys
        self.result = result


class Menu(object):
    def __init__(
            self,
            header: str,
            menu_choices: List[MenuChoice],
    ):
        """Provides a simple menu that responds to keypresses
        from the user to trigger actions
        """
        self.key_to_menu_choice = {
            key: mc
            for mc in menu_choices
            for key in mc.keys
        }
        if len(self.key_to_menu_choice) != sum(
                len(set(mc.keys)) for mc in menu_choices
        ):
            raise ValueError(
                'Menu choices have overlapping keys'
            )
        self.choice_text = header + '\n' + '\n'.join(
            mc.text for mc in menu_choices
        )

    def present_loop(
            self,
            screen,
            background_color,
            foreground_color,
            font,
            frames_per_second=20.,
            exit_condition=lambda value: False,
    ):
        while True:
            result_fn = self.present(
                screen,
                background_color,
                foreground_color,
                font,
                frames_per_second
            )

            result = result_fn()

            if exit_condition(result):
                break

            return result

    def present(
            self,
            screen,
            background_color,
            foreground_color,
            font,
            frames_per_second,
    ):
        """Presents the menu and returns the result associated
        with the selected menu item. Ignores keypresses not
        associated with any menu item.
        """
        clock = pygame.time.Clock()

        menu_choice = None
        while True:
            screen.fill(background_color)
            display_centered_text(
                screen,
                self.choice_text,
                foreground_color,
                font,
            )
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    menu_choice = self.key_to_menu_choice.get(
                        event.key
                    )
                if menu_choice:
                    break
            if menu_choice:
                break

            clock.tick(frames_per_second)

        if callable(menu_choice.result):
            return menu_choice.result
        else:
            return lambda: menu_choice.result
