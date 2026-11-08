"""Synthetic tasks and independent behavioral checks for paired simplification trials."""
import copy
import datetime
import importlib.util
import itertools
from pathlib import Path

CSV_HELPER = '''import csv
import io

def export_rows(rows):
    output = io.StringIO(newline='')
    writer = csv.writer(output, lineterminator='\\n')
    writer.writerow(('name', 'note'))
    for row in rows:
        if not isinstance(row['name'], str) or not isinstance(row['note'], str):
            raise ValueError('text required')
        writer.writerow((row['name'], row['note']))
    return output.getvalue()
'''
CSV_APP = '''from helpers import export_rows

def export_all(rows):
    return export_rows(rows)

def export_active(rows):
    raise NotImplementedError
'''
SUMMARY_APP = '''def summarize(rows):
    totals = {}
    order = []
    for row in rows:
        if type(row['quantity']) is not int or row['quantity'] < 0:
            raise ValueError('quantity')
        if row['status'] not in ('paid', 'cancelled'):
            raise ValueError('status')
        if row['status'] == 'paid':
            if row['sku'] in totals:
                totals[row['sku']] = totals[row['sku']] + row['quantity']
            else:
                totals[row['sku']] = row['quantity']
                order.append(row['sku'])
        else:
            pass
    output = []
    for sku in order:
        record = {}
        record['sku'] = sku
        record['quantity'] = totals[sku]
        output.append(record)
    return output
'''
DATE_APP = '''from datetime import date

def parse_booking_date(value, blocked):
    if not isinstance(value, str):
        raise ValueError('format')
    if len(value) != 10:
        raise ValueError('format')
    if value[4] != '-' or value[7] != '-':
        raise ValueError('format')
    digits = value[:4] + value[5:7] + value[8:]
    for char in digits:
        if char not in '0123456789':
            raise ValueError('format')
    try:
        day = date(int(value[:4]), int(value[5:7]), int(value[8:]))
    except ValueError:
        raise ValueError('calendar') from None
    if day.weekday() == 5:
        raise ValueError('weekend')
    if day.weekday() == 6:
        raise ValueError('weekend')
    if value in blocked:
        raise ValueError('blocked')
    return day
'''
CASES = {
    'reuse': {
        'source': CSV_APP,
        'helper': CSV_HELPER,
        'request': 'export_active를 구현해 줘. active가 정확히 True인 행만 기존 CSV 형식(name,note 헤더와 LF 줄바꿈)으로 내보내. 입력은 list 또는 1회용 iterable이고 입력을 바꾸면 안 돼. 선택된 행의 잘못된 텍스트는 기존처럼 ValueError, 제외된 행의 텍스트는 검사하지 않아. export_all과 helpers.py는 그대로 유지해. 구현과 필요한 테스트까지 자율적으로 끝내 줘.',
        'public_test': "self.assertEqual(app.export_all([{'name':'a','note':'b'}]), 'name,note\\na,b\\n')",
    },
    'duplicates': {
        'source': SUMMARY_APP,
        'request': 'summarize의 중복·불필요한 상태를 줄여 읽기 쉽게 정리하고 테스트해 줘. 기존 공개 동작을 유지해: paid의 SKU 첫 등장 순서, 수량 합계, 0인 항목 포함, cancelled도 수량과 상태 검사, bool 수량 거절, 같은 예외 메시지, 입력 보존. 없는 키의 KeyError도 유지해. 이번 함수 범위에서 알아서 진행해.',
        'public_test': "self.assertEqual(app.summarize([{'sku':'a','quantity':2,'status':'paid'}]), [{'sku':'a','quantity':2}])",
    },
    'strict-date': {
        'source': DATE_APP,
        'request': 'parse_booking_date를 더 단순하게 정리하고 테스트해 줘. ASCII YYYY-MM-DD만 허용하고 날짜 객체 반환, 실제 달력 날짜 검사, 주말·blocked 금지, 입력 보존, ValueError 메시지와 검사 우선순위를 모두 유지해야 해. 기본 기능으로 충분한 부분은 활용하되 필요한 업무 규칙은 유지해. 요청 범위에서 자율적으로 완료해 줘.',
        'public_test': "self.assertEqual(app.parse_booking_date('2026-11-09', set()).isoformat(), '2026-11-09')",
    },
}


def seed(folder, name):
    case = CASES[name]
    (folder / 'app.py').write_text(case['source'], encoding='utf-8')
    if 'helper' in case:
        (folder / 'helpers.py').write_text(case['helper'], encoding='utf-8')
    test = 'import unittest\nimport app\n\nclass Existing(unittest.TestCase):\n    def test_existing(self):\n        ' + case['public_test'] + '\n'
    (folder / 'test_existing.py').write_text(test, encoding='utf-8')


def outcome(fn, *args):
    supplied = copy.deepcopy(args)
    before = copy.deepcopy(supplied)
    try:
        result = ('return', fn(*supplied))
    except (ValueError, KeyError) as exc:
        result = (type(exc).__name__, str(exc))
    assert supplied == before, 'input mutated'
    return result


def check(name, module):
    """Compare to frozen behavior or fixed expectations, never to model-written tests."""
    count = 0
    if name == 'reuse':
        baseline = {}
        exec(CSV_HELPER, baseline)
        for first, second in itertools.product(['', 'a,b', '"quote"', '한글\n줄'], repeat=2):
            rows = [dict(name=first, note=second, active=True), dict(name=5, note=None, active=False),
                    dict(name='ignore', note='integer is not True', active=1)]
            expected = baseline['export_rows']([rows[0]])
            assert outcome(module.export_active, rows) == ('return', expected)
            assert module.export_active(iter(rows)) == expected
            count += 2
        assert module.export_active([]) == 'name,note\n'
        for field in ('name', 'note'):
            row = dict(name='a', note='b', active=True)
            row[field] = 7
            assert outcome(module.export_active, [row]) == ('ValueError', 'text required')
            count += 1
        assert module.export_all([dict(name='a,b', note='c')]) == 'name,note\n"a,b",c\n'
        return count + 2
    original = {}
    exec(CASES[name]['source'], original)
    if name == 'duplicates':
        valid = [dict(sku=sku, quantity=q, status=status)
                 for sku, q, status in itertools.product(('a', 'b'), (0, 2), ('paid', 'cancelled'))]
        inputs = [[], *[[r] for r in valid], *[list(pair) for pair in itertools.product(valid, repeat=2)]]
        inputs += [[dict(sku='a', quantity=q, status=status)]
                   for q, status in itertools.product((True, -1, 1.5, '1', None, 0), ('paid', 'cancelled', 'other'))]
        inputs += [[{}], [dict(quantity=1, status='paid')], [dict(quantity=1, status='cancelled')]]
        for rows in inputs:
            assert outcome(module.summarize, rows) == outcome(original['summarize'], rows)
            count += 1
    else:
        values = ['2026-11-09', '2026-11-07', '2026-11-08', '2024-02-29', '2025-02-29',
                  '20261109', '2026-W46-1', '２０２６-１１-０９', '2026-1-09', '', None, 20261109,
                  '0000-01-01', '2026-13-01', '2026-11-09T00:00', '2026-11-09 ', '2026-02-30']
        values += [(datetime.date(2026, 11, 1) + datetime.timedelta(days=n)).isoformat() for n in range(30)]
        for value, blocked in itertools.product(values, (set(), {'2026-11-09', '2026-11-07', '2025-02-29'})):
            assert outcome(module.parse_booking_date, value, blocked) == outcome(original['parse_booking_date'], value, blocked)
            count += 1
    return count


if __name__ == '__main__':
    import json
    import sys
    path = Path(sys.argv[2]).resolve()
    sys.path.insert(0, str(path))
    spec = importlib.util.spec_from_file_location('candidate', path / 'app.py')
    candidate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(candidate)
    print(json.dumps({'passed_inputs': check(sys.argv[1], candidate)}))
