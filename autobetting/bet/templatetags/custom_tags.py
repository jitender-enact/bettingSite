"""
Contain the custom filters, used in displaying the template data.
"""
from django import template
from bet.models import SELECTED_LINES, GAME_INTERVALS, GAME_TYPES, BET_ERROR_STATUS

# create register instance
register = template.Library()


GAME_TYPES_DICT = dict(GAME_TYPES)
GAME_INTERVALS_DICT = dict(GAME_INTERVALS)
SELECTED_LINES_DICT = dict(SELECTED_LINES)
BET_ERROR_STATUS_DICT = dict(BET_ERROR_STATUS)


def display_dict_value(key, dictionary):
    """
    Check the given `key` exist in given `dictionary` and return the '`dictionary`[`key`] value' or '--' string
    :param key:
    :param dictionary:
    :return `dictionary`[`key`] or '--':
    """
    if key in dictionary:
        return dictionary[key].title()
    return '--'


@register.filter
def get_game_type(value):
    """
    return the type of game
    :param value:
    :return type of game or '--':
    """
    return display_dict_value(value, GAME_TYPES_DICT)


@register.filter
def get_game_interval(value):
    """
    return the interval value.
    :param value:
    :return interval value:
    """
    return display_dict_value(value, GAME_INTERVALS_DICT)


@register.filter
def get_selected_line(value):
    """
    return the selected line value.
    :param value:
    :return selected value:
    """
    return display_dict_value(value, SELECTED_LINES_DICT)


@register.filter
def get_error_status(value):
    """
    return the error status value.
    :param value:
    :return error_status value:
    """
    return display_dict_value(value, BET_ERROR_STATUS_DICT)


@register.simple_tag
def add_active_class(current_value, data_value, initial_value ):
    """
    Return the 'active' string
    :param current_value:
    :param data_value:
    :param initial_value:
    :return:
    """
    compare_val = data_value if data_value is not None else initial_value
    return "active" if int(compare_val) == int(current_value) else ""
