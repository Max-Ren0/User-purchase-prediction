
# reco_pipeline_utils.py
import pandas as pd, numpy as np

def ensure_sorted(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if not np.issubdtype(df['create_order_time'].dtype, np.datetime64):
        df['create_order_time'] = pd.to_datetime(df['create_order_time'])
    return df.sort_values(['buyer_admin_id','create_order_time','irank']).reset_index(drop=True)

def time_decay(days, tau=14.0):
    days = np.maximum(days, 0.0)
    return np.exp(-days / float(tau))

def safe_vc(g, col, topn):
    vc = g[col].value_counts()
    return vc.head(topn).index.tolist() if len(vc) else []
