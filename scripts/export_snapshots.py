#!/usr/bin/env python3
"""Rebuild the dashboard CSV snapshots from Supabase, in the existing formats.

Targets (format copied from the files already in data/):
  data/cipac_resolutions.csv  sep ',', utf-8, LF
  data/01_movies.csv          sep ';', utf-8 with BOM, CRLF

Dry-run by default: the new files are written to a temporary folder and compared
with data/. Nothing in data/ changes. Use --apply to back up and replace only the
files that differ. Supabase is opened read-only.
"""
import argparse
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv

DATA = Path('data')
CIPAC_COLUMNS = ['resolution_number', 'year', 'incentive_article', 'resolution_type', 'investor_name',
                 'investor_rnc', 'producer_rnc', 'film_title', 'production_company', 'pur_number',
                 'cpnd_number', 'request_date', 'resolution_date', 'validated_amount_dop',
                 'tax_credit_dop', 'tax_credit_pct', 'total_budget_approved', 'total_budget_executed']
TARGETS = {
    'cipac_resolutions': dict(path=DATA / 'cipac_resolutions.csv', sep=',', enc='utf-8', eol='\n', key='resolution_number'),
    '01_movies': dict(path=DATA / '01_movies.csv', sep=';', enc='utf-8-sig', eol='\r\n', key='project_id'),
}


def fetch_all(query):
    """Read-only query against Supabase. Returns (columns, rows)."""
    load_dotenv('.env')
    conn = psycopg2.connect(os.environ['SUPABASE_DB_URL'])
    conn.set_session(readonly=True)
    try:
        cur = conn.cursor()
        cur.execute(query)
        return [d[0] for d in cur.description], cur.fetchall()
    finally:
        conn.close()


def read_str(path, sep, enc):
    return pd.read_csv(path, sep=sep, encoding=enc, dtype=str, keep_default_na=False)


def build(name):
    t = TARGETS[name]
    if name == 'cipac_resolutions':
        cols, rows = fetch_all(f"SELECT {', '.join(CIPAC_COLUMNS)} FROM cipac_resolutions ORDER BY year, resolution_number")
        return pd.DataFrame(rows, columns=cols, dtype=object)
    existing = read_str(t['path'], t['sep'], t['enc'])
    cols = list(existing.columns)
    _, rows = fetch_all(f"SELECT {', '.join(cols)} FROM productions")
    df = pd.DataFrame(rows, columns=cols, dtype=object)
    order = {k: i for i, k in enumerate(existing[t['key']])}  # keep the current row order
    df['_o'] = df[t['key']].map(lambda k: order.get(k, len(order)))
    return df.sort_values(['_o', t['key']], kind='stable').drop(columns='_o').reset_index(drop=True)


def same_number(x, y):
    try:
        return round(float(x), 2) == round(float(y), 2)
    except ValueError:
        return False


def compare(name, new_path):
    t = TARGETS[name]
    a = read_str(t['path'], t['sep'], t['enc']).set_index(t['key'])
    b = read_str(new_path, t['sep'], t['enc']).set_index(t['key'])
    print(f"\n=== {name}")
    print(f"rows: current {len(a)} | new {len(b)} | only current {len(set(a.index) - set(b.index))} | only new {len(set(b.index) - set(a.index))}")
    print('byte-identical:', t['path'].read_bytes() == Path(new_path).read_bytes())
    common = sorted(set(a.index) & set(b.index))
    strict, real, examples = {}, {}, {}
    for c in a.columns:
        if c not in b.columns:
            continue
        for k in common:
            x, y = a.at[k, c], b.at[k, c]
            if x != y:
                strict[c] = strict.get(c, 0) + 1
                if not same_number(x, y):
                    real[c] = real.get(c, 0) + 1
                    examples.setdefault(c, []).append((k, x, y))
    print('cells that differ as text (includes number formatting):', strict or 'none')
    print('cells that differ in value:', real or 'none')
    for c, v in examples.items():
        for k, x, y in v[:2]:
            print(f"   {c} | {k} | current: {str(x)[:38]!r} | new: {str(y)[:38]!r}")
    return bool(strict) or len(a) != len(b) or set(a.index) != set(b.index)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='back up and replace the files that differ')
    ap.add_argument('--only', choices=list(TARGETS), help='process a single file')
    args = ap.parse_args()
    names = [args.only] if args.only else list(TARGETS)
    tmp = Path(tempfile.mkdtemp(prefix='snapshots_'))
    changed = []
    for name in names:
        t = TARGETS[name]
        df = build(name)
        out = tmp / t['path'].name
        df.to_csv(out, index=False, sep=t['sep'], encoding=t['enc'], lineterminator=t['eol'])
        if compare(name, out):
            changed.append((name, out))
    print(f"\nNew files written to {tmp} (outside the repo).")
    if not changed:
        print('Nothing differs: no file needs to change.')
        return
    if not args.apply:
        print('Dry-run only. Re-run with --apply to replace:', ', '.join(n for n, _ in changed))
        return
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    for name, out in changed:
        p = TARGETS[name]['path']
        shutil.copy2(p, p.with_name(p.name + f'.bak-{stamp}'))
        shutil.copy2(out, p)
        print(f'Replaced {p} (backup: {p.name}.bak-{stamp}). Do not commit the backup.')


if __name__ == '__main__':
    main()
