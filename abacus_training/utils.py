import datetime
import glob
import pandas as pd

as_suffix = '_abacus_as.dat'
date_format = '%Y_%m_%d'

def get_data_fns(suffix=as_suffix):
    return glob.glob('*' + suffix)

def date_to_fn(
        dt,
        suffix=as_suffix
):
    return dt.strftime(date_format) + suffix

# Get listing of appropriate data files by date
def get_dataset_dates(suffix=as_suffix):
    dates = []
    fns = get_data_fns(suffix=suffix)

    for fn in fns:
        dt = datetime.datetime.strptime(fn.split(suffix)[0], date_format).date()
        dates.append(dt)
    dates.sort()

    return dates

def read_as_data(date):
    return pd.read_csv(
        date_to_fn(date, suffix=as_suffix),
        delimiter=',',
        header=None,
        names=['problem', 'response_time', 'response', 'correct', 'time_of_day']
    )

def display_as_problem(operands):
    print()
    for operand in operands:
        print(' {: >+10,}'.format(operand))
    print('-------------------------')

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
