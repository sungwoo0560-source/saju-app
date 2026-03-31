with open('manse.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''        for _title, _body in _danger_signals:
            lines.append(f"**{_title}**")
            lines.append(_body)
            lines.append("")'''

new = '''        for _title, _body in _danger_signals:
            lines.append(f"**{_title}**  ")
            lines.append("")
            lines.append(_body)
            lines.append("")'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ 줄바꿈 수정 완료")
else:
    print("❌ 패턴 없음")

with open('manse.py', 'w', encoding='utf-8') as f:
    f.write(content)
