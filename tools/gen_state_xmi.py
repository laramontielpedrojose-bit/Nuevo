#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera MAQUINAS DE ESTADO (StateDiagram) en XMI nativo de EA 15, igual que la
plantilla 'state.xml': ActivityModel con StateMachine.transitions + StateMachine.top
(CompositeState {top} con SimpleState y PseudoState initial/final), elemento
StateMachine y un Diagram diagramType=StateDiagram.

Spec:
  states: [(nombre, kind)]  kind: initial|final|state
  transitions: [(origen, destino, trigger, guard, effect)]  (cualquiera puede ser '')
"""
import uuid
import gen_ea_xmi as G

gid, brace, esc, newg = G.gid, G.brace, G.esc, G.newg
ROOT_ID, DATE, AUTHOR = G.ROOT_ID, G.DATE, G.AUTHOR


def _layout(states, transitions, name2id):
    # columnas por BFS desde el estado initial
    adj = {}
    for s, t, *_ in transitions:
        adj.setdefault(s, []).append(t)
    init = next((n for n, k in states if k == 'initial'), states[0][0])
    col = {init: 0}
    queue = [init]
    while queue:
        u = queue.pop(0)
        for v in adj.get(u, []):
            if v not in col:
                col[v] = col[u] + 1
                queue.append(v)
    maxc = max(col.values()) if col else 0
    for n, k in states:
        if n not in col:
            maxc += 0
            col[n] = maxc + 1 if k == 'final' else maxc
    rows = {}
    pos = {}
    for n, k in states:
        c = col.get(n, 0)
        r = rows.get(c, 0)
        rows[c] = r + 1
        pos[n] = (c, r)
    return pos


def build_state(pkg_name, states, transitions, context=None):
    PKGID = 'EAPK_' + gid(newg())[5:]   # los paquetes de EA usan prefijo EAPK_
    MODELID = 'MX_' + gid(newg())
    AMID = PKGID + '_ActivityModel'
    TOPID = PKGID + '_Activity_Top'
    SMID = gid(newg())            # elemento StateMachine (owner de los estados)
    CLASSID = gid(newg())         # clase de contexto (clasificador de la maquina)
    DIAGID = gid(newg())
    CDIAGID = gid(newg())         # diagrama de clases (muestra Clase + StateMachine)
    cls_duid = uuid.uuid4().hex[:8].upper()
    sm_duid = uuid.uuid4().hex[:8].upper()
    ctx_name = context or (pkg_name + ' (contexto)')
    cnt = [80]
    loc = lambda: (cnt.__setitem__(0, cnt[0] + 1) or cnt[0])

    st = {}
    for nm, kind in states:
        st[nm] = {'name': nm, 'kind': kind, 'id': newg(), 'localid': loc(),
                  'duid': uuid.uuid4().hex[:8].upper()}
    pos = _layout(states, transitions, st)
    for nm in st:
        c, r = pos[nm]
        st[nm]['x'] = 60 + c * 230
        st[nm]['y'] = 80 + r * 130

    def stype(nm):
        return 'StateNode' if st[nm]['kind'] in ('initial', 'final') else 'State'

    trans = []
    for s, t, trig, guard, eff in transitions:
        trans.append({'id': newg(), 'src': st[s], 'tgt': st[t], 'localid': loc(),
                      'trigger': trig, 'guard': guard, 'effect': eff})

    out = []
    w = out.append
    G._header(w)
    w('\t\t<UML:Model name="EA Model" xmi.id="%s">' % MODELID)
    w('\t\t\t<UML:Namespace.ownedElement>')
    w('\t\t\t\t<UML:Class name="EARootClass" xmi.id="%s" isRoot="true" isLeaf="false" isAbstract="false"/>' % ROOT_ID)
    w('\t\t\t\t<UML:Package name="%s" xmi.id="%s" isRoot="false" isLeaf="false" isAbstract="false" visibility="public">' % (esc(pkg_name), PKGID))
    w('\t\t\t\t\t<UML:ModelElement.taggedValue>')
    for t, v in [('ea_package_id', str(loc())), ('created', DATE), ('modified', DATE),
                 ('iscontrolled', 'FALSE'), ('isprotected', 'FALSE'), ('version', '1.0'),
                 ('author', AUTHOR), ('status', 'Proposed'), ('ea_stype', 'Public')]:
        w('\t\t\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v)))
    w('\t\t\t\t\t</UML:ModelElement.taggedValue>')
    w('\t\t\t\t\t<UML:Namespace.ownedElement>')
    w('\t\t\t\t\t\t<UML:ActivityModel xmi.id="%s" context="%s" name="ActivityModel" visibility="public">' % (AMID, PKGID))

    # --- transiciones ---
    w('\t\t\t\t\t\t\t<UML:StateMachine.transitions>')
    for tr in trans:
        s, r = tr['src'], tr['tgt']
        w('\t\t\t\t\t\t\t\t<UML:Transition xmi.id="%s" visibility="public" source="%s" target="%s">' % (tr['id'], s['id'], r['id']))
        if tr['trigger']:
            w('\t\t\t\t\t\t\t\t\t<UML:Transition.trigger>')
            w('\t\t\t\t\t\t\t\t\t\t<UML:Event name="%s"/>' % esc(tr['trigger']))
            w('\t\t\t\t\t\t\t\t\t</UML:Transition.trigger>')
        if tr['guard']:
            w('\t\t\t\t\t\t\t\t\t<UML:Transition.guard>')
            w('\t\t\t\t\t\t\t\t\t\t<UML:Guard>')
            w('\t\t\t\t\t\t\t\t\t\t\t<UML:Guard.expression>')
            w('\t\t\t\t\t\t\t\t\t\t\t\t<UML:BooleanExpression body="%s"/>' % esc(tr['guard']))
            w('\t\t\t\t\t\t\t\t\t\t\t</UML:Guard.expression>')
            w('\t\t\t\t\t\t\t\t\t\t</UML:Guard>')
            w('\t\t\t\t\t\t\t\t\t</UML:Transition.guard>')
        if tr['effect']:
            w('\t\t\t\t\t\t\t\t\t<UML:Transition.effect>')
            w('\t\t\t\t\t\t\t\t\t\t<UML:ActionSequence>')
            w('\t\t\t\t\t\t\t\t\t\t\t<UML:ActionSequence.action>')
            w('\t\t\t\t\t\t\t\t\t\t\t\t<UML:UninterpretedAction name="%s"/>' % esc(tr['effect']))
            w('\t\t\t\t\t\t\t\t\t\t\t</UML:ActionSequence.action>')
            w('\t\t\t\t\t\t\t\t\t\t</UML:ActionSequence>')
            w('\t\t\t\t\t\t\t\t\t</UML:Transition.effect>')
        w('\t\t\t\t\t\t\t\t\t<UML:ModelElement.taggedValue>')
        tv = [('style', '3'), ('ea_type', 'StateFlow'), ('direction', 'Source -&gt; Destination'),
              ('linemode', '3'), ('linecolor', '-1'), ('linewidth', '0'), ('seqno', '0'),
              ('headStyle', '0'), ('lineStyle', '0')]
        if tr['trigger']:
            tv.append(('privatedata1', tr['trigger']))
        if tr['guard']:
            tv.append(('privatedata2', tr['guard']))
        if tr['effect']:
            tv.append(('privatedata3', tr['effect']))
        tv += [('ea_localid', str(tr['localid'])), ('ea_sourceName', s['name']),
               ('ea_targetName', r['name']), ('ea_sourceType', stype(s['name'])),
               ('ea_targetType', stype(r['name'])), ('ea_sourceID', str(s['localid'])),
               ('ea_targetID', str(r['localid'])),
               ('src_visibility', 'Public'), ('src_isOrdered', 'false'), ('src_targetScope', 'instance'),
               ('src_changeable', 'none'), ('src_isNavigable', 'false'), ('src_containment', 'Unspecified'),
               ('src_style', 'Union=0;Derived=0;AllowDuplicates=0;'),
               ('dst_visibility', 'Public'), ('dst_isOrdered', 'false'), ('dst_targetScope', 'instance'),
               ('dst_changeable', 'none'), ('dst_isNavigable', 'true'), ('dst_containment', 'Unspecified'),
               ('dst_style', 'Union=0;Derived=0;AllowDuplicates=0;'), ('virtualInheritance', '0')]
        for t, v in tv:
            vv = v if t == 'direction' else esc(v)
            w('\t\t\t\t\t\t\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, vv))
        w('\t\t\t\t\t\t\t\t\t</UML:ModelElement.taggedValue>')
        w('\t\t\t\t\t\t\t\t</UML:Transition>')
    w('\t\t\t\t\t\t\t</UML:StateMachine.transitions>')

    # --- top / substates ---
    w('\t\t\t\t\t\t\t<UML:StateMachine.top>')
    w('\t\t\t\t\t\t\t\t<UML:CompositeState xmi.id="%s" name="{top}">' % TOPID)
    w('\t\t\t\t\t\t\t\t\t<UML:CompositeState.substate>')
    for nm, kind in states:
        s = st[nm]
        if kind == 'state':
            ntype = '0'
            w('\t\t\t\t\t\t\t\t\t\t<UML:SimpleState name="%s" xmi.id="%s" visibility="public" namespace="%s">' % (esc(nm), s['id'], PKGID))
            stype_v, eleopen = 'State', 'SimpleState'
        else:
            ntype = '3' if kind == 'initial' else '4'
            w('\t\t\t\t\t\t\t\t\t\t<UML:PseudoState name="%s" xmi.id="%s" visibility="public" namespace="%s" kind="%s">' % (esc(nm), s['id'], PKGID, kind))
            stype_v, eleopen = 'StateNode', 'PseudoState'
        w('\t\t\t\t\t\t\t\t\t\t\t<UML:ModelElement.taggedValue>')
        for t, v in [('isAbstract', 'false'), ('isSpecification', 'false'), ('ea_stype', stype_v),
                     ('ea_ntype', ntype), ('version', '1.0'), ('isActive', 'false'), ('package', PKGID),
                     ('owner', SMID), ('date_created', DATE), ('date_modified', DATE),
                     ('gentype', '<none>'), ('tagged', '0'), ('package_name', pkg_name), ('phase', '1.0'),
                     ('author', AUTHOR), ('complexity', '1'), ('status', 'Proposed'), ('tpos', '0'),
                     ('ea_localid', str(s['localid'])), ('ea_eleType', 'element'),
                     ('style', 'BackColor=-1;BorderColor=-1;BorderWidth=-1;FontColor=-1;VSwimLanes=0;HSwimLanes=0;BorderStyle=0;')]:
            w('\t\t\t\t\t\t\t\t\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v)))
        w('\t\t\t\t\t\t\t\t\t\t\t</UML:ModelElement.taggedValue>')
        w('\t\t\t\t\t\t\t\t\t\t</UML:%s>' % eleopen)
    w('\t\t\t\t\t\t\t\t\t</UML:CompositeState.substate>')
    w('\t\t\t\t\t\t\t\t</UML:CompositeState>')
    w('\t\t\t\t\t\t\t</UML:StateMachine.top>')
    w('\t\t\t\t\t\t</UML:ActivityModel>')

    # --- elemento StateMachine (ea_ntype=8, dueno = clase de contexto) ---
    w('\t\t\t\t\t\t<UML:StateMachine name="State Machine %s" xmi.id="%s" visibility="public" namespace="%s">' % (esc(pkg_name), SMID, PKGID))
    w('\t\t\t\t\t\t\t<UML:ModelElement.taggedValue>')
    for t, v in [('isAbstract', 'false'), ('isSpecification', 'false'), ('ea_stype', 'StateMachine'),
                 ('ea_ntype', '8'), ('version', '1.0'), ('isActive', 'false'), ('package', PKGID),
                 ('owner', CLASSID), ('date_created', DATE), ('date_modified', DATE), ('gentype', '<none>'),
                 ('tagged', '0'), ('package_name', pkg_name), ('phase', '1.0'), ('author', AUTHOR),
                 ('complexity', '1'), ('status', 'Proposed'), ('tpos', '0'), ('ea_localid', str(loc())),
                 ('ea_eleType', 'element'),
                 ('style', 'BackColor=-1;BorderColor=-1;BorderWidth=-1;FontColor=-1;VSwimLanes=1;HSwimLanes=1;BorderStyle=0;')]:
        w('\t\t\t\t\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v)))
    w('\t\t\t\t\t\t\t</UML:ModelElement.taggedValue>')
    w('\t\t\t\t\t\t</UML:StateMachine>')

    # --- clase de contexto (clasificador cuyo comportamiento describe la maquina) ---
    w('\t\t\t\t\t\t<UML:Class name="%s" xmi.id="%s" visibility="public" namespace="%s" isRoot="false" isLeaf="false" isAbstract="false" isActive="false">' % (esc(ctx_name), CLASSID, PKGID))
    w('\t\t\t\t\t\t\t<UML:ModelElement.taggedValue>')
    for t, v in [('isSpecification', 'false'), ('ea_stype', 'Class'), ('ea_ntype', '0'), ('version', '1.0'),
                 ('package', PKGID), ('date_created', DATE), ('date_modified', DATE), ('gentype', '<none>'),
                 ('tagged', '0'), ('package_name', pkg_name), ('phase', '1.0'), ('author', AUTHOR),
                 ('complexity', '1'), ('status', 'Proposed'), ('tpos', '0'), ('ea_localid', str(loc())),
                 ('ea_eleType', 'element'),
                 ('style', 'BackColor=-1;BorderColor=-1;BorderWidth=-1;FontColor=-1;VSwimLanes=1;HSwimLanes=1;BorderStyle=0;')]:
        w('\t\t\t\t\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v)))
    w('\t\t\t\t\t\t\t</UML:ModelElement.taggedValue>')
    w('\t\t\t\t\t\t</UML:Class>')

    w('\t\t\t\t\t</UML:Namespace.ownedElement>')
    w('\t\t\t\t</UML:Package>')
    w('\t\t\t</UML:Namespace.ownedElement>')
    w('\t\t</UML:Model>')

    # --- diagrama ---
    w('\t\t<UML:Diagram name="%s" xmi.id="%s" diagramType="StateDiagram" owner="%s" toolName="Enterprise Architect 2.5">' % (esc(pkg_name), DIAGID, PKGID))
    w('\t\t\t<UML:ModelElement.taggedValue>')
    EASTYLE = ('ShowPrivate=1;ShowProtected=1;ShowPublic=1;HideRelationships=0;Locked=0;Border=1;'
               'HighlightForeign=1;PackageContents=1;SequenceNotes=0;ScalePrintImage=0;PPgs.cx=1;PPgs.cy=1;'
               'DocSize.cx=827;DocSize.cy=1169;ShowDetails=0;Orientation=P;Zoom=100;ShowTags=0;OpParams=1;'
               'VisibleAttributeDetail=0;ShowOpRetType=1;ShowIcons=1;CollabNums=0;HideProps=0;ShowReqs=0;'
               'ShowCons=0;PaperSize=9;HideParents=0;UseAlias=0;HideAtts=0;HideOps=0;HideStereo=0;'
               'HideElemStereo=0;ShowTests=0;ShowMaint=0;ConnectorNotation=UML 2.1;ExplicitNavigability=0;'
               'ShowShape=1;AllDockable=0;AdvancedElementProps=1;AdvancedFeatureProps=1;'
               'AdvancedConnectorProps=1;m_bElementClassifier=1;SPT=1;ShowNotes=0;SuppressBrackets=0;'
               'SuppConnectorLabels=0;PrintPageHeadFoot=0;ShowAsList=0;')
    for t, v in [('version', '1.0'), ('author', AUTHOR), ('created_date', DATE), ('modified_date', DATE),
                 ('package', PKGID), ('parent', SMID), ('type', 'Statechart'), ('ea_localid', str(loc())),
                 ('EAStyle', EASTYLE), ('styleex', 'SaveTag=F6B74707;SuppressFOC=1;TConnectorNotation=UML 2.1;SPT=1;Theme=:119;')]:
        w('\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v)))
    w('\t\t\t</UML:ModelElement.taggedValue>')
    w('\t\t\t<UML:Diagram.element>')
    sq = 0
    for nm, kind in states:
        sq += 1
        s = st[nm]
        L, T = s['x'], s['y']
        if kind == 'state':
            R, B = L + 170, T + 70
            stylep = 'ImageID=0;StateLabel=0;fontsz=0;bold=0;black=0;italic=0;ul=0;charset=0;pitch=0;BFol=-1;BCol=-1;LCol=-1;DUID=%s;' % s['duid']
        else:
            R, B = L + 20, T + 20
            stylep = ('ImageID=0;fontsz=0;bold=0;black=0;italic=0;ul=0;charset=0;pitch=0;BFol=-1;BCol=-1;LCol=-1;'
                      'LBL=CX=28:CY=14:OX=-3:OY=26:HDN=0:BLD=0:ITA=0:UND=0:CLR=-1:ALN=1:ALT=0:ROT=0;DUID=%s;' % s['duid'])
        w('\t\t\t\t<UML:DiagramElement geometry="Left=%d;Top=%d;Right=%d;Bottom=%d;" subject="%s" seqno="%d" style="%s"/>'
          % (L, T, R, B, s['id'], sq, stylep))
    edge = 1
    for tr in trans:
        edge += 1
        w('\t\t\t\t<UML:DiagramElement geometry="SX=0;SY=0;EX=0;EY=0;EDGE=%d;$LLB=;LLT=;LMT=;LMB=;LRT=;LRB=;IRHS=;ILHS=;Path=;" subject="%s" style="Mode=3;EOID=%s;SOID=%s;Color=-1;LWidth=0;Hidden=0;"/>'
          % (edge, tr['id'], tr['tgt']['duid'], tr['src']['duid']))
    w('\t\t\t</UML:Diagram.element>')
    w('\t\t</UML:Diagram>')

    # --- diagrama de clases (Clase de contexto con su StateMachine), como en la
    #     plantilla: refuerza que la maquina pertenece a un clasificador ---
    w('\t\t<UML:Diagram name="%s" xmi.id="%s" diagramType="ClassDiagram" owner="%s" toolName="Enterprise Architect 2.5">' % (esc(pkg_name + ' - Contexto'), CDIAGID, PKGID))
    w('\t\t\t<UML:ModelElement.taggedValue>')
    CEASTYLE = ('ShowPrivate=1;ShowProtected=1;ShowPublic=1;HideRelationships=0;Locked=0;Border=1;'
                'HighlightForeign=1;PackageContents=1;SequenceNotes=0;ScalePrintImage=0;PPgs.cx=1;PPgs.cy=1;'
                'DocSize.cx=827;DocSize.cy=1169;ShowDetails=0;Orientation=P;Zoom=100;ShowTags=0;OpParams=1;'
                'VisibleAttributeDetail=0;ShowOpRetType=1;ShowIcons=1;CollabNums=0;HideProps=0;ShowReqs=0;'
                'ShowCons=0;PaperSize=9;HideParents=0;UseAlias=0;HideAtts=0;HideOps=0;HideStereo=0;'
                'HideElemStereo=0;ShowTests=0;ShowMaint=0;ConnectorNotation=UML 2.1;ExplicitNavigability=0;'
                'ShowShape=1;AllDockable=0;AdvancedElementProps=1;AdvancedFeatureProps=1;'
                'AdvancedConnectorProps=1;m_bElementClassifier=1;SPT=1;ShowNotes=0;SuppressBrackets=0;'
                'SuppConnectorLabels=0;PrintPageHeadFoot=0;ShowAsList=0;')
    for t, v in [('version', '1.0'), ('author', AUTHOR), ('created_date', DATE), ('modified_date', DATE),
                 ('package', PKGID), ('type', 'Logical'), ('ea_localid', str(loc())),
                 ('EAStyle', CEASTYLE), ('styleex', 'SaveTag=F6B74707;TConnectorNotation=UML 2.1;SPT=1;Theme=:119;')]:
        w('\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v)))
    w('\t\t\t</UML:ModelElement.taggedValue>')
    w('\t\t\t<UML:Diagram.element>')
    w('\t\t\t\t<UML:DiagramElement geometry="Left=120;Top=113;Right=300;Bottom=233;" subject="%s" seqno="1" style="DUID=%s;"/>' % (CLASSID, cls_duid))
    w('\t\t\t\t<UML:DiagramElement geometry="Left=400;Top=113;Right=560;Bottom=193;" subject="%s" seqno="2" style="DUID=%s;"/>' % (SMID, sm_duid))
    w('\t\t\t</UML:Diagram.element>')
    w('\t\t</UML:Diagram>')
    G._footer(w)
    return '\n'.join(out) + '\n'
