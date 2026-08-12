from pathlib import Path

path = Path("frontend/main.py")
text = path.read_text()

old_style_start = '    <style>'
old_style_end = '    </style>'

start_idx = text.index(old_style_start)
end_idx = text.index(old_style_end) + len(old_style_end)

new_style = Path("/tmp/new_style.txt").read_text()

new_text = text[:start_idx] + new_style + text[end_idx:]
path.write_text(new_text)
