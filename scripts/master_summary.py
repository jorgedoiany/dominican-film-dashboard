#!/usr/bin/env python3
"""Master Summary of the CIPAC EDA: results per section as plain text, plus a check
of every hard-coded number in 'Key Findings & Conclusions' against the data.

Usage (repo root):
  python3 scripts/master_summary.py                 # sections 2-14 and the check
  python3 scripts/master_summary.py --section 8     # only one section
  python3 scripts/master_summary.py --check         # only the conclusions check
Read-only: it never writes. It uses the same definitions as the notebook.
"""
import argparse
from pathlib import Path

import pandas as pd

CSV = Path('data/cipac_resolutions.csv')
MISSING = Path('data/02_missing_resolutions.csv')
M = 1e6


def load():
    df = pd.read_csv(CSV)
    df['request_date'] = pd.to_datetime(df['request_date'])
    df['resolution_date'] = pd.to_datetime(df['resolution_date'])
    appr = df[df['resolution_type'] == 'approved'].copy()
    d34_all = df[(df['incentive_article'] == 'art_34') & (df['resolution_type'] == 'approved')]  # sections 8-11: approved only
    d39_all = df[(df['incentive_article'] == 'art_39') & (df['resolution_type'] == 'approved')]
    a34 = appr[appr['incentive_article'] == 'art_34']
    a39 = appr[appr['incentive_article'] == 'art_39']
    t = appr[appr['request_date'].notna() & appr['resolution_date'].notna()].copy()
    t['days'] = (t['resolution_date'] - t['request_date']).dt.days
    t = t[t['days'] >= 0]
    return df, appr, d34_all, d39_all, a34, a39, t


def tbl(s, n=15, fmt=None):
    s = s.head(n)
    return s.to_string(float_format=fmt) if fmt else s.to_string()


def outliers(appr, cols):
    rows = []
    for c in cols:
        x = appr[c].dropna()
        q1, q3 = x.quantile(.25), x.quantile(.75)
        i = q3 - q1
        n = int(((x < q1 - 1.5 * i) | (x > q3 + 1.5 * i)).sum())
        rows.append((c, n, round(n / len(x) * 100, 1), round(x.min() / M, 1), round(x.max() / M, 1)))
    return pd.DataFrame(rows, columns=['variable', 'outliers', 'pct', 'min_M', 'max_M'])


def outliers_by_article(appr, cols):
    rows = []
    for c in cols:
        d = appr[['incentive_article', c]].dropna()
        q1, q3 = d[c].quantile(.25), d[c].quantile(.75)
        i = q3 - q1
        o = d[(d[c] < q1 - 1.5 * i) | (d[c] > q3 + 1.5 * i)]
        rows.append((c, len(o), int((o['incentive_article'] == 'art_34').sum()), int((o['incentive_article'] == 'art_39').sum())))
    return pd.DataFrame(rows, columns=['variable', 'outliers', 'art_34', 'art_39'])


def quarters(appr):
    q = appr.assign(quarter=appr['resolution_date'].dt.to_period('Q').astype(str))
    q = q.groupby(['quarter', 'incentive_article'])['validated_amount_dop'].sum().div(M).unstack(fill_value=0)
    for c in ('art_34', 'art_39'):
        if c not in q:
            q[c] = 0
    q['total'] = q['art_34'] + q['art_39']
    return q


def budget_year(appr):
    b = appr.groupby('year').agg(avg_approved=('total_budget_approved', 'mean'), avg_executed=('total_budget_executed', 'mean'))
    b['rate'] = (b['avg_executed'] / b['avg_approved'] * 100).round(1)
    return b


def over100(appr):
    e = appr[appr['total_budget_approved'].notna() & appr['total_budget_executed'].notna()].copy()
    e['rate'] = (e['total_budget_executed'] / e['total_budget_approved'] * 100).round(1)
    return e, int((e['rate'] > 100).sum())


def sections(S, only):
    df, appr, d34, d39, a34, a39, t = S
    num4 = ['validated_amount_dop', 'tax_credit_dop', 'total_budget_approved', 'total_budget_executed']
    out = {}
    out[2] = ('Dataset Overview', lambda: '\n'.join([
        f'shape: {df.shape[0]} x {df.shape[1]}',
        'article: ' + str(df['incentive_article'].value_counts().to_dict()),
        'type: ' + str(df['resolution_type'].value_counts().to_dict()),
        'unique: ' + str({c: int(df[c].nunique()) for c in ['investor_name', 'investor_rnc', 'producer_rnc', 'production_company', 'film_title', 'pur_number']}),
        f"year range: {df['year'].min()}-{df['year'].max()}"]))
    def s3():
        n = df.isnull().sum(); n = n[n > 0]
        lines = ['nulls: ' + ', '.join(f'{k}={v} ({v / len(df) * 100:.2f}%)' for k, v in n.items())]
        if MISSING.exists():
            m = pd.read_csv(MISSING, sep=';', encoding='utf-8-sig')
            g = m[m['status'] == 'Not found (404)'].groupby('year').size()
            lines.append(f'404 gaps: total {int(g.sum())} | by year: ' + str(g.to_dict()))
        lines.append(f"duplicated resolution_number: {int(df['resolution_number'].duplicated().sum())}")
        odd = df.loc[~df['resolution_number'].str.fullmatch(r'CIPAC-\d{4}-\d{3}'), 'resolution_number'].tolist()
        lines.append(f'non-standard resolution numbers: {odd}')
        return '\n'.join(lines)
    out[3] = ('Data Quality', s3)
    out[4] = ('Outliers (IQR, approved only)', lambda: outliers(appr, num4 + ['tax_credit_pct']).to_string(index=False)
              + '\n\nby article:\n' + outliers_by_article(appr, num4).to_string(index=False))
    out[5] = ('Resolutions by Year (all)', lambda: df['year'].value_counts().sort_index().to_string())
    def s6():
        by = t.groupby('year')['days'].mean().round(1)
        top = t.sort_values('days', ascending=False).drop_duplicates('pur_number').head(15)[['resolution_number', 'film_title', 'incentive_article', 'days']]
        mo = df['resolution_date'].dt.month.value_counts().sort_index()
        q = quarters(appr).sort_values('total', ascending=False)
        return '\n'.join([
            f"records with both dates: {len(t)} | mean {t['days'].mean():.1f} | median {t['days'].median():.0f} | min {t['days'].min()} | max {t['days'].max()}",
            'mean days by year: ' + str(by.to_dict()), '', 'slowest 15 (one per PUR):', top.to_string(index=False), '',
            'resolutions by month: ' + str(mo.to_dict()), '', 'top 8 quarters (RD$ M):', q.head(8).round(1).to_string(),
            f"largest art_34 quarter: {q['art_34'].idxmax()} {q['art_34'].max():.1f} | largest art_39 quarter: {q['art_39'].idxmax()} {q['art_39'].max():.1f}"])
    out[6] = ('Time Series', s6)
    out[7] = ('Art. 34 vs Art. 39', lambda: '\n'.join([
        str(df.groupby(['incentive_article', 'resolution_type']).size().to_dict()),
        'by year and article:', df.groupby(['year', 'incentive_article']).size().unstack(fill_value=0).to_string()]))
    out[8] = ('Top Art. 34 Investors (approved only)', lambda: '\n'.join([
        'by number of resolutions:', tbl(d34.groupby(['investor_rnc', 'investor_name']).size().sort_values(ascending=False)), '',
        'by total tax credit (RD$ M):', tbl((d34.groupby(['investor_rnc', 'investor_name'])['tax_credit_dop'].sum().dropna().sort_values(ascending=False) / M).round(1))]))
    out[9] = ('Top Art. 34 Production Companies', lambda: '\n'.join([
        'by number of resolutions:', tbl(d34.groupby(['producer_rnc', 'production_company']).size().sort_values(ascending=False)), '',
        'by validated amount (RD$ M):', tbl((d34.groupby(['producer_rnc', 'production_company'])['validated_amount_dop'].sum().dropna().sort_values(ascending=False) / M).round(1)), '',
        'most funded films (RD$ M):', tbl((d34.groupby(['pur_number', 'film_title'])['validated_amount_dop'].sum().dropna().sort_values(ascending=False) / M).round(1))]))
    out[10] = ('Top Art. 39 Production Companies', lambda: '\n'.join([
        'by number of resolutions:', tbl(d39.groupby(['producer_rnc', 'production_company']).size().sort_values(ascending=False)), '',
        'by validated expenses (RD$ M):', tbl((d39.groupby(['producer_rnc', 'production_company'])['validated_amount_dop'].sum().dropna().sort_values(ascending=False) / M).round(1)), '',
        'most funded films (RD$ M):', tbl((d39.groupby(['pur_number', 'film_title'])['validated_amount_dop'].sum().dropna().sort_values(ascending=False) / M).round(1))]))
    def s11():
        c34, c39 = d34.groupby('pur_number').size(), d39.groupby('pur_number').size()
        top34 = d34.groupby(['pur_number', 'film_title', 'production_company']).size().sort_values(ascending=False).head(10)
        top39 = d39.groupby(['pur_number', 'film_title', 'production_company']).size().sort_values(ascending=False).head(5)
        return '\n'.join([
            f'art_34 unique PUR: {len(c34)} | with 1: {int((c34 == 1).sum())} | with >=2: {int((c34 >= 2).sum())} | >=5: {int((c34 >= 5).sum())} | >=10: {int((c34 >= 10).sum())}',
            f'art_39 unique PUR: {len(c39)} | max resolutions per film: {int(c39.max())}',
            'top art_34 films by resolutions:', top34.to_string(), 'top art_39 films by resolutions:', top39.to_string()])
    out[11] = ('Film Analysis', s11)
    def s12():
        y = appr.groupby(['year', 'incentive_article']).agg(validated_M=('validated_amount_dop', lambda x: x.sum() / M), credit_M=('tax_credit_dop', lambda x: x.sum() / M)).round(1)
        tot = appr.groupby('incentive_article')[['validated_amount_dop', 'tax_credit_dop']].sum() / M
        avg = appr.groupby('incentive_article')['tax_credit_dop'].mean() / M
        v = tot['validated_amount_dop']
        return '\n'.join([
            f"total validated (approved): {v.sum():.1f} M | total credit: {tot['tax_credit_dop'].sum():.1f} M",
            f"art_34 validated {v['art_34']:.1f} M ({v['art_34'] / v.sum() * 100:.1f}%) | art_39 {v['art_39']:.1f} M ({v['art_39'] / v.sum() * 100:.1f}%)",
            f"avg tax credit: art_34 {avg['art_34']:.1f} M | art_39 {avg['art_39']:.1f} M | ratio {avg['art_39'] / avg['art_34']:.1f}x",
            'by year and article (RD$ M):', y.to_string()])
    out[12] = ('Validated Amounts & Tax Credits (approved only)', s12)
    out[13] = ('Correlation (approved only)', lambda: appr[['validated_amount_dop', 'tax_credit_dop', 'tax_credit_pct', 'total_budget_approved', 'total_budget_executed']].corr().round(2).to_string())
    def s14():
        b = budget_year(appr)
        e, n = over100(appr)
        overall = appr['total_budget_executed'].mean() / appr['total_budget_approved'].mean() * 100
        return '\n'.join([
            f'overall execution rate: {overall:.1f}% | resolutions with rate > 100%: {n} ({n / len(e) * 100:.1f}% of {len(e)})',
            'execution rate by year (%): ' + str(b['rate'].to_dict())])
    out[14] = ('Budget Analysis (approved only)', s14)
    keys = [only] if only else sorted(out)
    for k in keys:
        title, fn = out[k]
        print(f'\n## Section {k}: {title}\n{fn()}')


def check(S):
    df, appr, d34, d39, a34, a39, t = S
    rows = []

    def c(label, claimed, actual, tol=0.0):
        try:
            ok = abs(float(claimed) - float(actual)) <= tol + 1e-9
        except (TypeError, ValueError):
            ok = claimed == actual
        rows.append((label, claimed, actual, 'OK' if ok else 'MISMATCH'))

    n = len(df)
    c('total resolutions', 2543, n)
    c('approved', 2539, len(appr)); c('approved %', 99.8, round(len(appr) / n * 100, 1), .05)
    c('rejected', 4, n - len(appr))
    n34, n39 = int((df['incentive_article'] == 'art_34').sum()), int((df['incentive_article'] == 'art_39').sum())
    c('art_34 total', 2459, n34); c('art_34 %', 96.7, round(n34 / n * 100, 1), .05)
    c('art_39 total', 84, n39); c('art_39 %', 3.3, round(n39 / n * 100, 1), .05)
    c('approved art_34', 2455, len(a34)); c('approved art_39', 84, len(a39))
    c('rejected art_34', 4, int(((df.resolution_type == 'rejected') & (df.incentive_article == 'art_34')).sum()))
    for col, claimed in [('investor_name', 3.3), ('investor_rnc', 3.3), ('cpnd_number', 3.3)]:
        c(f'missing % {col}', claimed, round(df[col].isnull().mean() * 100, 1), .05)
    for col, claimed in [('request_date', 4), ('tax_credit_dop', 4), ('total_budget_approved', 1), ('total_budget_executed', 2)]:
        c(f'missing {col}', claimed, int(df[col].isnull().sum()))
    if MISSING.exists():
        m = pd.read_csv(MISSING, sep=';', encoding='utf-8-sig')
        g = m[m['status'] == 'Not found (404)'].groupby('year').size()
        c('404 total', 229, int(g.sum())); c('404 in 2024', 155, int(g.get(2024, 0)))
    o = outliers(appr, ['validated_amount_dop', 'tax_credit_dop', 'total_budget_approved', 'total_budget_executed', 'tax_credit_pct']).set_index('variable')
    for col, cnt, pct in [('validated_amount_dop', 289, 11.4), ('tax_credit_dop', 271, 10.7), ('total_budget_approved', 102, 4.0), ('total_budget_executed', 61, 2.4), ('tax_credit_pct', 84, 3.3)]:
        c(f'outliers {col}', cnt, o.loc[col, 'outliers']); c(f'outliers % {col}', pct, o.loc[col, 'pct'], .05)
    oa = outliers_by_article(appr, ['validated_amount_dop', 'tax_credit_dop', 'total_budget_approved', 'total_budget_executed']).set_index('variable')
    for col, n34, n39 in [('validated_amount_dop', 211, 78), ('tax_credit_dop', 218, 53), ('total_budget_approved', 44, 58), ('total_budget_executed', 10, 51)]:
        c(f'outliers art_34 {col}', n34, oa.loc[col, 'art_34']); c(f'outliers art_39 {col}', n39, oa.loc[col, 'art_39'])
    c('art_39 outliers, % of its resolutions', 93, round(oa.loc['validated_amount_dop', 'art_39'] / len(a39) * 100), .5)
    c('art_34 outliers, % of its resolutions', 8.6, round(oa.loc['validated_amount_dop', 'art_34'] / len(a34) * 100, 1), .05)
    ry = df['year'].value_counts().sort_index()
    c('resolutions 2012', 14, int(ry.get(2012, 0))); c('peak year', 2023, int(ry.idxmax())); c('peak count', 330, int(ry.max()))
    comp = ry[ry.index < df['resolution_date'].max().year]
    c('average per year, complete years', 166, round(comp.mean())); c('lowest year', 2012, int(ry.idxmin()))
    c('processing records', 2537, len(t)); c('processing mean', 33, round(t['days'].mean())); c('processing median', 29, round(t['days'].median()))
    by = t.groupby('year')['days'].mean().round(1)
    for y, v in [(2017, 46.6), (2013, 38.3), (2018, 41.4), (2020, 36.8), (2024, 34.8), (2012, 10.6), (2025, 29.5), (2026, 28.9)]:
        c(f'processing days {y}', v, by.get(y, float('nan')), .05)
    c('slowest 5 years, order as written', [2017, 2018, 2013, 2020, 2024], by.sort_values(ascending=False).head(5).index.tolist())
    c('longest processing days', 218, int(t['days'].max())); c('longest processing record', 'CIPAC-2017-105', t.loc[t['days'].idxmax(), 'resolution_number'])
    mo = df['resolution_date'].dt.month.value_counts()
    c('February', 708, int(mo.get(2, 0))); c('March', 555, int(mo.get(3, 0))); c('January', 383, int(mo.get(1, 0)))
    q = quarters(appr)
    c('peak quarter', '2023Q3', q['total'].idxmax()); c('peak quarter RD$M', 9450.7, round(q['total'].max(), 1), .05)
    c('five largest quarters', ['2023Q3', '2022Q1', '2023Q1', '2022Q3', '2026Q1'], q['total'].sort_values(ascending=False).head(5).index.tolist())
    c('largest art_34 quarter', '2023Q1', q['art_34'].idxmax()); c('largest art_34 quarter RD$M', 2134.3, round(q['art_34'].max(), 1), .05)
    c('largest art_39 quarter', '2023Q3', q['art_39'].idxmax()); c('largest art_39 quarter RD$M', 9276.1, round(q['art_39'].max(), 1), .05)
    tot = appr.groupby('incentive_article')[['validated_amount_dop', 'tax_credit_dop']].sum() / M
    v = tot['validated_amount_dop']
    c('total validated RD$M', 52200, round(v.sum(), 1), 50); c('total tax credit RD$M', 29943, round(tot['tax_credit_dop'].sum(), 1), 50)
    c('art_34 validated RD$M', 22523.4, round(v['art_34'], 1), .05); c('art_34 share %', 43.1, round(v['art_34'] / v.sum() * 100, 1), .05)
    c('art_39 validated RD$M', 29676.8, round(v['art_39'], 1), .05); c('art_39 share %', 56.9, round(v['art_39'] / v.sum() * 100, 1), .05)
    avg = appr.groupby('incentive_article')['tax_credit_dop'].mean() / M
    c('avg credit art_39 RD$M', 88.3, round(avg['art_39'], 1), .05); c('avg credit art_34 RD$M', 9.2, round(avg['art_34'], 1), .05)
    c('credit ratio', 9.6, round(avg['art_39'] / avg['art_34'], 1), .05)
    med = appr.groupby('incentive_article')['tax_credit_dop'].median() / M
    c('median credit art_39 RD$M', 36.8, round(med['art_39'], 1), .05); c('median credit art_34 RD$M', 5.0, round(med['art_34'], 1), .05)
    c('median credit ratio', 7.4, round(med['art_39'] / med['art_34'], 1), .05)
    ic = d34.groupby(['investor_rnc', 'investor_name']).size().sort_values(ascending=False).head(5)
    c('top 5 investors, resolutions', [88, 86, 78, 65, 55], ic.tolist())
    icr = (d34.groupby(['investor_rnc', 'investor_name'])['tax_credit_dop'].sum().dropna().sort_values(ascending=False) / M).round(1).head(5)
    c('top 5 investors, credit RD$M', [3002.9, 2114.7, 1642.8, 1030.9, 943.6], icr.tolist())
    tc = d34.groupby('investor_rnc')['tax_credit_dop'].sum().sort_values(ascending=False)
    c('top 5 investors, share of Art. 34 credit %', 38.8, round(tc.head(5).sum() / d34['tax_credit_dop'].sum() * 100, 1), .05)
    c('top 15 investors, share of Art. 34 credit %', 56.6, round(tc.head(15).sum() / d34['tax_credit_dop'].sum() * 100, 1), .05)
    c('Art. 34 investors', 487, d34['investor_rnc'].nunique())
    c1 = d34.groupby('pur_number').size()
    c('art_34 unique PUR', 523, len(c1)); c('art_34 films with 1', 105, int((c1 == 1).sum())); c('art_34 films with >=2', 418, int((c1 >= 2).sum()))
    c('art_34 films with >=5', 220, int((c1 >= 5).sum())); c('art_34 films with >=10', 49, int((c1 >= 10).sum()))
    ft = d34.groupby(['pur_number', 'film_title']).size().sort_values(ascending=False)
    c('art_34 max resolutions per film', 29, int(ft.max()))
    f34 = (d34.groupby(['pur_number', 'film_title'])['validated_amount_dop'].sum().dropna().sort_values(ascending=False) / M).round(1).head(5)
    c('top 5 art_34 films RD$M', [187.0, 127.1, 126.0, 116.8, 113.7], f34.tolist())
    pc = d34.groupby(['producer_rnc', 'production_company']).size().sort_values(ascending=False).head(5)
    c('top 5 art_34 companies, resolutions', [59, 51, 46, 45, 37], pc.tolist())
    c39 = d39.groupby('pur_number').size()
    c('art_39 films with 2+', 7, int((c39 >= 2).sum()))
    c('art_39 unique PUR', 76, len(c39)); c('art_39 max resolutions per film', 3, int(c39.max()))
    e39 = (d39.groupby(['producer_rnc', 'production_company'])['validated_amount_dop'].sum().dropna().sort_values(ascending=False) / M).round(1).head(3)
    c('top 3 art_39 companies RD$M', [4302.2, 4033.5, 2404.6], e39.tolist())
    g39 = (d39.groupby(['pur_number', 'film_title'])['validated_amount_dop'].sum().dropna().sort_values(ascending=False) / M).round(1).head(5)
    c('top 5 art_39 films RD$M', [4302.2, 2404.6, 2163.4, 1926.1, 1516.0], g39.tolist())
    b = budget_year(appr); e, n100 = over100(appr)
    overall = appr['total_budget_executed'].mean() / appr['total_budget_approved'].mean() * 100
    c('overall execution rate %', 74.3, round(overall, 1), .05)
    c('lowest year rate % (2014 and 2016)', 69.4, b['rate'].min(), .05); c('years at the lowest rate', [2014, 2016], b.index[b['rate'] == b['rate'].min()].tolist())
    c('highest year rate % (2013)', 86.3, b['rate'].max(), .05); c('year of the highest rate', 2013, int(b['rate'].idxmax()))
    c('resolutions with rate > 100%', 77, n100); c('% with rate > 100%', 3.0, round(n100 / len(e) * 100, 1), .05)
    latest = (appr.sort_values(['pur_number', 'resolution_date', 'resolution_number']).groupby('pur_number').tail(1)
              .dropna(subset=['total_budget_approved', 'total_budget_executed']))
    over_f = int((latest['total_budget_executed'] > latest['total_budget_approved']).sum())
    c('films with budgets (latest resolution)', 599, len(latest))
    c('execution rate, latest resolution of each film %', 84.7, round(latest['total_budget_executed'].sum() / latest['total_budget_approved'].sum() * 100, 1), .05)
    c('films with executed above approved', 47, over_f); c('% of films with executed above approved', 7.8, round(over_f / len(latest) * 100, 1), .05)
    r = appr[['validated_amount_dop', 'tax_credit_dop', 'tax_credit_pct', 'total_budget_approved', 'total_budget_executed']].corr()
    for a, bb, claimed in [('validated_amount_dop', 'total_budget_approved', .97), ('validated_amount_dop', 'tax_credit_dop', .96),
                           ('validated_amount_dop', 'total_budget_executed', .96), ('total_budget_approved', 'total_budget_executed', .96),
                           ('tax_credit_dop', 'total_budget_approved', .92), ('tax_credit_dop', 'total_budget_executed', .91),
                           ('tax_credit_pct', 'tax_credit_dop', -.41), ('tax_credit_pct', 'validated_amount_dop', -.47)]:
        c(f'corr {a} / {bb}', claimed, round(r.loc[a, bb], 2), .005)
    money = ['validated_amount_dop', 'tax_credit_dop', 'total_budget_approved', 'total_budget_executed']
    sp = appr[money].corr(method='spearman')
    for x, y, claimed in [('validated_amount_dop', 'tax_credit_dop', .99), ('validated_amount_dop', 'total_budget_approved', .22),
                          ('validated_amount_dop', 'total_budget_executed', .28), ('total_budget_approved', 'total_budget_executed', .74)]:
        c(f'spearman {x} / {y}', claimed, round(sp.loc[x, y], 2), .005)
    for art, d, vals in (('art_34', a34, (.21, .30, .73)), ('art_39', a39, (.98, .96, .96))):
        rr = d[money].corr()
        for (x, y), claimed in zip((('validated_amount_dop', 'total_budget_approved'), ('validated_amount_dop', 'total_budget_executed'),
                                    ('total_budget_approved', 'total_budget_executed')), vals):
            c(f'pearson {art} {x} / {y}', claimed, round(rr.loc[x, y], 2), .005)
    films34 = d34.groupby('pur_number').agg(validated=('validated_amount_dop', 'sum'), budget=('total_budget_approved', 'median')).dropna()
    c('film-level check, number of Art. 34 films', 523, len(films34))
    c('film-level pearson, validated / approved budget', .84, round(films34['validated'].corr(films34['budget']), 2), .005)
    c('film-level spearman, validated / approved budget', .84, round(films34['validated'].corr(films34['budget'], method='spearman'), 2), .005)
    bad = [x for x in rows if x[3] != 'OK']
    print(f'\n## Check of Key Findings: {len(rows)} claims | OK {len(rows) - len(bad)} | MISMATCH {len(bad)}')
    for lab, claimed, actual, st in rows:
        if st != 'OK':
            print(f'MISMATCH | {lab} | written: {claimed} | data: {actual}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--section', type=int, choices=range(2, 15), help='print a single section')
    ap.add_argument('--check', action='store_true', help='only the conclusions check')
    a = ap.parse_args()
    S = load()
    if not a.check:
        sections(S, a.section)
    if a.check or not a.section:
        check(S)


if __name__ == '__main__':
    main()
