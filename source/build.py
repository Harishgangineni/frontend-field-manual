import base64
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

with open(os.path.join(HERE, 'template.html'), 'r', encoding='utf-8') as f:
    body = f.read()

sections = ['fundamentals', 'frameworks', 'system_design', 'dsa', 'ops_excellence', 'leadership']

b64_entries = []
for key in sections:
    with open(os.path.join(HERE, 'sections', key + '.md'), 'rb') as f:
        raw = f.read().replace(b'\r\n', b'\n')  # identical output regardless of checkout line endings
    b64 = base64.b64encode(raw).decode('ascii')
    b64_entries.append('    %s: "%s"' % (key, b64))

b64_block = "  var DATA_B64 = {\n" + ",\n".join(b64_entries) + "\n  };\n"

old_files_pattern = re.compile(r'  var FILES = \{.*?\};\n', re.DOTALL)
new_body, n = old_files_pattern.subn(b64_block, body, count=1)
assert n == 1, "FILES block not found"
body = new_body

new_load_pillar = '''  function b64ToUtf8(b64){
    var binary = atob(b64);
    var bytes = new Uint8Array(binary.length);
    for (var i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new TextDecoder("utf-8").decode(bytes);
  }

  function loadPillar(key){
    var container = document.getElementById("content-" + key);
    return new Promise(function(resolve){
      try {
        var md = b64ToUtf8(DATA_B64[key]);
        md = md.replace(/^#\\s*Pillar:.*\\n/, "");
        container.innerHTML = marked.parse(md);
        enhancePillar(container, key);
      } catch (err) {
        container.innerHTML = '<p class="loading">Could not render this section (' + err.message + ').</p>';
      }
      resolve();
    });
  }
'''
old_load_pillar_pattern = re.compile(r'  function loadPillar\(key\)\{.*?\n  \}\n', re.DOTALL)
new_body, n = old_load_pillar_pattern.subn(lambda m: new_load_pillar, body, count=1)
assert n == 1, "loadPillar block not found"
body = new_body

body = body.replace('Object.keys(FILES)', 'Object.keys(DATA_B64)')

idx = body.index('</style>') + len('</style>')
head_part = body[:idx]
body_part = body[idx:]

full_html = (
    '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    + head_part + '\n'
    '</head>\n<body>\n'
    + body_part.lstrip('\n') +
    '</body>\n</html>\n'
)

out_path = os.path.join(ROOT, 'index.html')
with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(full_html)

print("Wrote %s, %d bytes" % (out_path, len(full_html.encode('utf-8'))))
