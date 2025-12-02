from datetime import timedelta
from src.persistencia.dao.dao_historicos import historicos_dao
from src.persistencia.dao.dao_grd import grd_dao
from src.utils import timebox


def compute_range(window: str, page: int):
    now = timebox.utc_now()
    if window == '1sem':
        end_period = now - timedelta(weeks=max(page, 0))
        start_period = end_period - timedelta(days=6)
        start = start_period.replace(hour=0, minute=0, second=0, microsecond=0)
        end = end_period.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start, end
    if window == '1mes':
        ref = now - relativedelta(months=max(page, 0))
        start = ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = (start + relativedelta(months=1)) - timedelta(microseconds=1)
        return start, end
    start = now - timedelta(days=30)
    end = now
    return start, end


from dateutil.relativedelta import relativedelta

grd_id = 5
window = '1sem'
page = 0

desc = grd_dao.get_grd_description(grd_id)
print('desc', desc)

today_str = timebox.utc_now().strftime('%Y-%m-%d')
if window == '1sem':
    df = historicos_dao.get_weekly_data_for_grd(grd_id, today_str, page)
elif window == '1mes':
    df = historicos_dao.get_monthly_data_for_grd(grd_id, today_str, page)
else:
    df = historicos_dao.get_all_data_for_grd(grd_id)
print('rows', len(df))
print(df.head())
print(df.tail())
plot_start, plot_end = compute_range(window, page)
print('range', plot_start, plot_end)
connected_before = historicos_dao.get_connected_state_before_timestamp(grd_id, plot_start)
print('connected_before', connected_before)
