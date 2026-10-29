"""Conservative comparison of a small OpenAPI subset; unsupported changes require review."""
import argparse
import json
from pathlib import Path


def compare(old, new):
    for doc in (old, new):
        if not isinstance(doc, dict) or not str(doc.get('openapi', '')).startswith(('3.0.', '3.1.')):
            raise ValueError('OpenAPI 3.0/3.1 JSON required')
        if not isinstance(doc.get('paths'), dict): raise ValueError('paths object required')
    findings=[]
    def note(level, where, reason):
        findings.append({'level':level,'path':where,'reason':reason})
    def extras(a,b,known,where):
        for key in sorted((set(a)|set(b))-set(known)):
            if a.get(key)!=b.get(key) and key not in {'description','summary','title','example','examples','externalDocs','tags'}:
                note('review',where+'/'+key,'unsupported or semantic change')
    def schema(a,b,where,direction):
        if a==b: return
        if not isinstance(a,dict) or not isinstance(b,dict):
            note('review',where,'schema form not supported'); return
        if '$ref' in a or '$ref' in b:
            note('review',where,'reference requires resolved comparison'); return
        extras(a,b,{'type','enum','properties','required'},where)
        if a.get('type')!=b.get('type'):
            note('breaking',where+'/type','schema type changed')
        if a.get('enum')!=b.get('enum'):
            left,right=(a.get('enum'),b.get('enum')) if direction=='request' else (b.get('enum'),a.get('enum'))
            if right is not None and (left is None or any(v not in right for v in left)):
                note('breaking',where+'/enum','accepted request values narrowed or response values broadened')
        ar,br=set(a.get('required',[])),set(b.get('required',[]))
        if (br-ar if direction=='request' else ar-br):
            note('breaking',where+'/required','new required input or removed response guarantee')
        ap,bp=a.get('properties',{}),b.get('properties',{})
        if not isinstance(ap,dict) or not isinstance(bp,dict): raise ValueError('properties must be objects')
        for name in ap.keys()&bp.keys(): schema(ap[name],bp[name],where+'/properties/'+name,direction)
        for name in ap.keys()-bp.keys():
            note('breaking' if direction=='response' and name in ar else 'review',where+'/properties/'+name,'property removed')
        if bp.keys()-ap.keys():
            note('review',where+'/properties','added properties: verify additionalProperties and consumers')
    def content(a,b,where,direction):
        for mime in a:
            if mime not in b: note('breaking',where+'/'+mime,'media type removed')
            else:
                schema(a[mime].get('schema',{}),b[mime].get('schema',{}),where+'/'+mime+'/schema',direction)
                extras(a[mime],b[mime],{'schema'},where+'/'+mime)
        if set(b)-set(a): note('review',where,'media type added; verify negotiation')
    methods={'get','put','post','delete','options','head','patch','trace'}
    extras(old,new,{'paths','openapi','info','components'},'')
    if old.get('components')!=new.get('components'):
        note('review','/components','component definitions changed; resolve references before approval')
    if old.get('openapi')!=new.get('openapi'): note('review','/openapi','specification version changed')
    for route, prior in old['paths'].items():
        if route not in new['paths']:
            note('breaking','/paths/'+route,'path removed'); continue
        current=new['paths'][route]
        extras(prior,current,methods,'/paths/'+route)
        for method in prior.keys()&methods:
            where='/paths/'+route+'/'+method
            if method not in current: note('breaking',where,'operation removed'); continue
            a,b=prior[method],current[method]
            extras(a,b,{'parameters','requestBody','responses','operationId'},where)
            if a.get('operationId')!=b.get('operationId'): note('review',where+'/operationId','generated client name may change')
            def parameters(op):
                result={}
                for p in op.get('parameters',[]):
                    if '$ref' in p: raise ValueError('resolve parameter references first')
                    key=(p['in'],p['name'])
                    if key in result: raise ValueError('duplicate parameter')
                    result[key]=p
                return result
            pa,pb=parameters(a),parameters(b)
            for key,p in pa.items():
                loc=where+'/parameters/'+key[0]+'/'+key[1]
                if key not in pb: note('breaking',loc,'parameter removed'); continue
                q=pb[key]
                if not p.get('required',False) and q.get('required',False): note('breaking',loc,'parameter now required')
                schema(p.get('schema',{}),q.get('schema',{}),loc+'/schema','request')
                extras(p,q,{'name','in','required','schema'},loc)
            for key in pb.keys()-pa.keys():
                if pb[key].get('required',False): note('breaking',where+'/parameters','required parameter added')
            ra,rb=a.get('requestBody',{}),b.get('requestBody',{})
            if not ra.get('required',False) and rb.get('required',False): note('breaking',where+'/requestBody','body now required')
            extras(ra,rb,{'required','content'},where+'/requestBody')
            content(ra.get('content',{}),rb.get('content',{}),where+'/requestBody/content','request')
            for status,response in a.get('responses',{}).items():
                loc=where+'/responses/'+str(status)
                if status not in b.get('responses',{}): note('breaking',loc,'response status removed'); continue
                replacement=b['responses'][status]
                extras(response,replacement,{'content'},loc)
                content(response.get('content',{}),replacement.get('content',{}),loc+'/content','response')
            if set(b.get('responses',{}))-set(a.get('responses',{})): note('review',where+'/responses','new status; verify consumers')
    counts={level:sum(x['level']==level for x in findings) for level in ('breaking','review')}
    return {'counts':counts,'findings':findings,'scope':'OpenAPI subset; no live service validation',
            'status':'breaking' if counts['breaking'] else 'review' if counts['review'] else 'no-breaking-detected'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before',type=Path); parser.add_argument('after',type=Path)
    args=parser.parse_args()
    try:
        result=compare(json.loads(args.before.read_text(encoding='utf-8-sig')),json.loads(args.after.read_text(encoding='utf-8-sig')))
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return {'breaking':1,'review':2,'no-breaking-detected':0}[result['status']]
    except (OSError,ValueError,KeyError,TypeError,AttributeError) as e:
        print(json.dumps({'status':'incomplete','error':type(e).__name__})); return 2


if __name__=='__main__': raise SystemExit(main())
