def format_date(value, format="%d/%m/%Y %H:%M:%S"):
    return value.strftime(format)


def bitwise_flag(value, flag):
    return (value & flag) == flag


def format_number(number, num_format='{0:,d}'):
    # Jode tener que crear un filtro para esto, jinja de mierda, en mako no
    # pasaba esto.
    return num_format.format(number)


def num_str(number):
    if number % 1:
        return '%.1f' % number
    return '%d' % number

number_names = {1: 'one',
                2: 'two',
                3: 'three',
                4: 'four',
                5: 'five',
                6: 'six',
                7: 'seven',
                8: 'eight',
                9: 'nine',
                10: 'ten',
                11: 'eleven',
                12: 'twelve',
                13: 'thirteen'
                }


def app_register_filters(app):
    @app.template_filter('number_name')
    def number_name(number):
        return number_names[number]

    @app.template_filter('nl2br')
    def nl2br(value): 
        return value.replace(' ','<br>\n', 1)
