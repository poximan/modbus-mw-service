from src.persistencia.dao.dao_historicos import historicos_dao
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
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


def df_to_records(df):
    records = []
    if df is None or df.empty:
        return records
    for _, row in df.iterrows():
        ts = row.get('timestamp')
        ts_iso = ''
        if ts is not None:
            try:
                ts_iso = timebox.utc_iso(ts if isinstance(ts, datetime) else ts.to_pydatetime())
            except Exception as exc:
                ts_iso = str(ts)
        records.append({'timestamp': ts_iso, 'conectado': int(row.get('conectado', 0))})
    return records

grd_id = 5
window = '1sem'
page = 0
plot_start, plot_end = compute_range(window, page)
current_str = timebox.utc_now().strftime('%Y-%m-%d')
df = historicos_dao.get_weekly_data_for_grd(grd_id, current_str, page)
records = df_to_records(df)
print('first record', records[0])
print('contains Z?', 'Z' in records[0]['timestamp'])
print('range_start', timebox.utc_iso(plot_start))
