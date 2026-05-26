import zipfile, re, os, io

BASE = r'd:/graphics/Jero/MTIC/industrial_diagnostic_study/report'

def esc(t):
    return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def inline(text):
    result = []
    for part in re.split(r'(\*\*[^*\n]+\*\*|\*[^*\n]+\*)', text):
        if part.startswith('**') and part.endswith('**') and len(part) > 4:
            result.append(f'<w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t xml:space="preserve">{esc(part[2:-2])}</w:t></w:r>')
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            result.append(f'<w:r><w:rPr><w:i/><w:iCs/></w:rPr><w:t xml:space="preserve">{esc(part[1:-1])}</w:t></w:r>')
        elif part:
            result.append(f'<w:r><w:t xml:space="preserve">{esc(part)}</w:t></w:r>')
    return ''.join(result)

def md_to_body(md):
    paras = []
    skip = False
    for line in md.splitlines():
        s = line.strip()
        if s == '## Working Notes for Solomon':
            skip = True
        if skip:
            continue
        if not s or s == '---' or s.startswith('|'):
            continue
        if s.startswith('### '):
            paras.append(f'<w:p><w:pPr><w:pStyle w:val="Heading3"/></w:pPr>{inline(s[4:])}</w:p>')
        elif s.startswith('## '):
            paras.append(f'<w:p><w:pPr><w:pStyle w:val="Heading2"/></w:pPr>{inline(s[3:])}</w:p>')
        elif s.startswith('# '):
            paras.append(f'<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>{inline(s[2:])}</w:p>')
        elif s.startswith('- '):
            paras.append(f'<w:p><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr><w:r><w:t xml:space="preserve">•  {esc(s[2:])}</w:t></w:r></w:p>')
        elif s.startswith('> '):
            paras.append(f'<w:p><w:pPr><w:ind w:left="720"/></w:pPr><w:r><w:rPr><w:i/><w:color w:val="595959"/></w:rPr><w:t>{esc(s[2:])}</w:t></w:r></w:p>')
        else:
            r = inline(s)
            if r:
                paras.append(f'<w:p>{r}</w:p>')
    return '\n'.join(paras)

CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>'''

RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

DOC_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''

STYLES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:pPr><w:spacing w:after="160" w:line="276" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:pPr>
      <w:spacing w:before="480" w:after="160"/>
      <w:outlineLvl w:val="0"/>
    </w:pPr>
    <w:rPr>
      <w:b/><w:bCs/>
      <w:sz w:val="40"/><w:szCs w:val="40"/>
      <w:color w:val="1F3864"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:pPr>
      <w:spacing w:before="320" w:after="120"/>
      <w:outlineLvl w:val="1"/>
    </w:pPr>
    <w:rPr>
      <w:b/><w:bCs/>
      <w:sz w:val="32"/><w:szCs w:val="32"/>
      <w:color w:val="2E5496"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:pPr>
      <w:spacing w:before="240" w:after="80"/>
      <w:outlineLvl w:val="2"/>
    </w:pPr>
    <w:rPr>
      <w:b/><w:bCs/>
      <w:sz w:val="28"/><w:szCs w:val="28"/>
      <w:color w:val="404040"/>
    </w:rPr>
  </w:style>
</w:styles>'''

def make_doc_xml(body):
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
{body}
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>
    </w:sectPr>
  </w:body>
</w:document>'''

def write_docx(md_path, out_path):
    with open(md_path, encoding='utf-8') as f:
        md = f.read()
    body = md_to_body(md)
    doc_xml = make_doc_xml(body)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', CONTENT_TYPES)
        z.writestr('_rels/.rels', RELS)
        z.writestr('word/document.xml', doc_xml)
        z.writestr('word/_rels/document.xml.rels', DOC_RELS)
        z.writestr('word/styles.xml', STYLES)
    with open(out_path, 'wb') as f:
        f.write(buf.getvalue())
    print(f'Created: {out_path}')

write_docx(
    os.path.join(BASE, 'structure-1.md'),
    os.path.join(BASE, 'MTIC_Report1_Structure_DRAFT.docx')
)
write_docx(
    os.path.join(BASE, 'structure-2.md'),
    os.path.join(BASE, 'MTIC_Report2_Structure_DRAFT.docx')
)
