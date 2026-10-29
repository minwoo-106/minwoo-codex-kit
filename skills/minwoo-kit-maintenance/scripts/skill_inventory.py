"""Read explicitly selected skill roots; report discovery text size, not runtime token usage."""
import argparse
import json
from pathlib import Path
import re
import stat


def read_field(front,name):
    match=re.search(r'^'+name+r':\s*(.*)$',front,re.M)
    if not match: raise ValueError('Missing '+name)
    value=match.group(1).strip()
    if value in {'>','>-','|','|-'}:
        lines=[]
        for line in front[match.end():].splitlines():
            if not line.strip(): continue
            if not line.startswith((' ','\t')): break
            lines.append(line.strip())
        return ' '.join(lines)
    if value.startswith('"'):
        try: return json.loads(value)
        except ValueError: raise ValueError('Unsupported quoted field')
    if value.startswith("'") and value.endswith("'"): return value[1:-1].replace("''","'")
    return value


def inventory(roots,budget_chars=8000):
    if budget_chars<1: raise ValueError('Positive comparison budget required')
    entries=[]; errors=[]; seen=set()
    def walk(folder,label):
        if not folder.exists():
            errors.append({'root':label,'reason':'root missing'}); return
        if folder.is_symlink() or getattr(folder.lstat(),'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0x400):
            errors.append({'root':label,'reason':'linked directory skipped'}); return
        for p in sorted(folder.iterdir()):
            if p.is_dir():
                if p.name not in {'.git','node_modules','__pycache__','.venv'}: walk(p,label)
            elif p.name=='SKILL.md':
                if p.is_symlink(): errors.append({'root':label,'reason':'linked skill skipped'}); continue
                identity=str(p.absolute())
                if identity in seen: continue
                seen.add(identity)
                try:
                    text=p.read_text(encoding='utf-8-sig')
                    if not text.startswith('---\n'): raise ValueError('No frontmatter')
                    front=text.split('---',2)[1]
                    name,description=read_field(front,'name'),read_field(front,'description')
                    if not isinstance(name,str) or not isinstance(description,str) or not name or not description: raise ValueError('Invalid metadata')
                    explicit=False
                    policy=p.parent/'agents/openai.yaml'
                    if policy.is_file() and not policy.is_symlink():
                        explicit=bool(re.search(r'^\s+allow_implicit_invocation:\s*false\s*(?:#.*)?$',policy.read_text(encoding='utf-8'),re.M))
                    rendered=f'- {name}: {description} (file: {p.absolute().as_posix()})\n'
                    entries.append({'name':name,'root':label,'description_chars':len(description),
                        'list_chars':len(rendered),'list_utf8_bytes':len(rendered.encode()),'explicit_only':explicit})
                except (OSError,ValueError,IndexError) as e: errors.append({'root':label,'reason':type(e).__name__})
    for index,root in enumerate(roots): walk(root,'root-'+str(index+1))
    active=[x for x in entries if not x['explicit_only']]
    chars=sum(x['list_chars'] for x in active)
    duplicates=sorted({x['name'] for x in entries if sum(y['name']==x['name'] for y in entries)>1})
    return {'scanned':len(entries),'implicit_candidates':len(active),'explicit_only':len(entries)-len(active),
        'list_chars':chars,'list_utf8_bytes':sum(x['list_utf8_bytes'] for x in active),
        'comparison_budget_chars':budget_chars,'over_comparison_budget':chars>budget_chars,
        'duplicates':duplicates,'errors':errors,'entries':entries,
        'scope':'selected roots only; cache may include inactive plugins; exact host catalog, truncation and token count are not inferred'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,action='append',required=True)
    parser.add_argument('--budget-chars',type=int,default=8000)
    args=parser.parse_args()
    try:
        result=inventory(args.root,args.budget_chars)
        print(json.dumps(result,ensure_ascii=False,indent=2)); raise SystemExit(2 if result['errors'] else 0)
    except (OSError,ValueError) as e:
        print(json.dumps({'error':type(e).__name__})); raise SystemExit(2)
