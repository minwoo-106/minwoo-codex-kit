"""Synthetic design comparison, not a randomized model benchmark. Requires bundled PDF libraries."""
import argparse
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from pypdf import PdfReader
import pypdfium2 as pdfium

TITLE = '주간 업무 기록'
PERIOD = '2026.11.09 - 2026.11.13'
ROWS = [
    ['자료 목록 정리', '12건 중 10건 완료', '누락된 2건의 분류를 확인 중'],
    ['입력 양식 점검', '필수 항목 8개 확인', '날짜 입력 오류 1건은 수정 후 재검토 예정'],
    ['이용 안내 개정', '초안 검토 중', '의견 3건을 반영한 뒤 확정 예정'],
]
PLANS = [
    ['11.16', '운영 담당', '누락 자료 2건의 분류 확인'],
    ['11.17', '점검 담당', '날짜 입력 오류 수정 결과 재검토'],
    ['11.18', '문서 담당', '안내문 의견 3건 반영'],
]
LIMITATION = '내부 목표일이며 외부 회신이나 완료를 보장하지 않습니다.'
SOURCE = '근거: 검증용 합성자료 A-01 (2026.11.13 기준)'
DECISION = '입력 오류의 재검토가 끝나기 전에는 새 양식을 배포하지 않습니다.'
DECISION_SHORT = '재검토 전 새 양식 배포 보류'


def styles():
    return {
        'body': ParagraphStyle('body', fontName='Korean', fontSize=11, leading=17, wordWrap='CJK', textColor=colors.HexColor('#202020')),
        'heading': ParagraphStyle('heading', fontName='KoreanBold', fontSize=13, leading=20, spaceBefore=16, spaceAfter=8),
        'title': ParagraphStyle('title', fontName='KoreanBold', fontSize=20, leading=29, spaceAfter=12),
        'small': ParagraphStyle('small', fontName='Korean', fontSize=8, leading=12, textColor=colors.HexColor('#757575')),
        'label': ParagraphStyle('label', fontName='KoreanBold', fontSize=10, leading=16, textColor=colors.HexColor('#167680')),
    }


def table(rows, widths, st, dark=False):
    header_style = ParagraphStyle('header', parent=st['body'],
                                  textColor=colors.white if dark else colors.HexColor('#202020'))
    cells = [[Paragraph(value, header_style if index == 0 else st['body']) for value in row]
             for index, row in enumerate(rows)]
    result = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
    commands = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EDEDED')),
                ('GRID', (0, 0), (-1, -1), .45, colors.HexColor('#AAAAAA')),
                ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 9), ('BOTTOMPADDING', (0, 0), (-1, -1), 9)]
    if dark:
        commands.append(('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#223A52')))
    result.setStyle(TableStyle(commands))
    return result


def build(out, arm):
    st = styles()
    width = A4[0] - 112
    story = []
    p = lambda text, kind='body': Paragraph(text, st[kind])
    baseline = arm == 'before'
    if baseline:
        story += [p('WEEKLY WORK OVERVIEW', 'label'), Spacer(1, 6)]
    story += [p(TITLE, 'title')]
    if baseline:
        story += [p('샘플 운영팀 | ' + PERIOD), Spacer(1, 12)]
    if baseline:
        box = Table([[p('이번 주 핵심 요약', 'heading')], [p('자료 정리와 입력 양식 점검, 안내문 개정을 진행했습니다.')]], colWidths=[width])
        box.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EAF2F5')), ('BOX', (0, 0), (-1, -1), .5, colors.HexColor('#CADDE3')), ('LEFTPADDING', (0, 0), (-1, -1), 12), ('BOTTOMPADDING', (0, 0), (-1, -1), 12)]))
        story += [box, Spacer(1, 12)]
    rows = [row[:] for row in ROWS]
    if not baseline:
        rows[1][2] += '<br/>' + DECISION_SHORT
    story += [p('이번 주 진행 내용', 'heading'), table([['업무', '진행 상태', '남은 내용']] + rows, [112, 137, width - 249], st, baseline)]
    if baseline:
        story += [PageBreak(), p('NEXT WEEK ACTION PLAN', 'label'), p('다음 주 실행 계획', 'title'), p('샘플 운영팀 | ' + PERIOD)]
    else:
        story += [p('다음 주 계획', 'heading')]
    story += [table([['내부 목표일', '담당', '다음 조치']] + PLANS, [89, 90, width - 179], st, baseline)]
    if baseline:
        story += [p('확인할 사항', 'heading'), p(DECISION), Spacer(1, 14), p(SOURCE)]

    def decorate(canvas, doc):
        if not baseline:
            return
        canvas.setFont('Korean', 7.5)
        canvas.setFillColor(colors.HexColor('#777777'))
        canvas.drawString(56, A4[1] - 30, '샘플 운영팀 / 주간 운영 현황')
        canvas.drawRightString(A4[0] - 56, A4[1] - 30, PERIOD)
        canvas.setStrokeColor(colors.HexColor('#167680'))
        canvas.line(56, A4[1] - 38, A4[0] - 56, A4[1] - 38)
        canvas.setFont('Korean', 7.5)
        if doc.page == 2:
            canvas.drawString(56, 48, LIMITATION)
        canvas.drawString(56, 34, '본 문서는 업무 흐름을 한눈에 파악할 수 있도록 체계적으로 정리했습니다.')
        canvas.drawRightString(A4[0] - 56, 24, str(doc.page))

    SimpleDocTemplate(str(out / (arm + '.pdf')), pagesize=A4, leftMargin=56, rightMargin=56,
                      topMargin=62 if baseline else 50, bottomMargin=68 if baseline else 50,
                      title=TITLE, author='Synthetic fixture').build(story, onFirstPage=decorate, onLaterPages=decorate)


def check_and_render(out):
    business_content = [TITLE, '내부 목표일']
    business_content += [value for row in ROWS + PLANS for value in row]
    summary = {'kind': 'controlled synthetic layout example; not a model A/B benchmark', 'results': {}}
    for arm in ('before', 'after'):
        path = out / (arm + '.pdf')
        reader = PdfReader(path)
        text = '\n'.join(page.extract_text() for page in reader.pages)
        compact = ''.join(text.split())
        required = business_content + ([DECISION, PERIOD, LIMITATION, SOURCE] if arm == 'before' else [DECISION_SHORT])
        missing = [value for value in required if ''.join(value.split()) not in compact]
        assert not missing, (arm, missing)
        assert all(abs(float(page.mediabox.width) - A4[0]) < 1 for page in reader.pages)
        assert all(abs(float(page.mediabox.height) - A4[1]) < 1 for page in reader.pages)
        if arm == 'after':
            for extra in [PERIOD, LIMITATION, SOURCE, '샘플 운영팀', '확인할 사항',
                          '체계적으로 정리했습니다', 'WEEKLY WORK OVERVIEW']:
                assert ''.join(extra.split()) not in compact, extra
            assert len(reader.pages) == 1
        document = pdfium.PdfDocument(str(path))
        for index in range(len(document)):
            page = document[index]
            bitmap = page.render(scale=1.5)
            bitmap.to_pil().save(out / f'{arm}-{index + 1}.png')
            bitmap.close()
            page.close()
        document.close()
        summary['results'][arm] = {'pages': len(reader.pages), 'required_strings_preserved': len(required), 'missing': missing}
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', type=Path, required=True, help='Installed Korean TTF; never copied into the repository')
    parser.add_argument('--bold-font', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True, help='Fresh directory outside the repository')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    out = args.out.resolve()
    if out == root or root in out.parents:
        parser.error('PDFs and previews must be outside the source repository')
    pdfmetrics.registerFont(TTFont('Korean', str(args.font)))
    pdfmetrics.registerFont(TTFont('KoreanBold', str(args.bold_font)))
    out.mkdir(parents=True, exist_ok=False)
    build(out, 'before')
    build(out, 'after')
    check_and_render(out)


if __name__ == '__main__':
    main()
