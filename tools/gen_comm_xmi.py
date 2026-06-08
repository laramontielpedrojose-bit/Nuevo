#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera DIAGRAMAS DE COMUNICACION (collaboration) en XMI nativo de EA 15,
igual que la plantilla 'comunicacion.xml' (diagramType=CollaborationDiagram):
objetos (ClassifierRole ea_stype=Object), enlaces (AssociationRole) y mensajes
con numeracion anidada (1, 1.1, 1.1.1, ...).

Entrada por especificacion:
  participants: [(alias, nombre, kind)]  kind: actor|boundary|control|dao|dto|object
  calls: [(emisor_alias, receptor_alias, etiqueta)]  -> SOLO llamadas (sin returns/BD)

Uso como libreria: build_comm(pkg, participants, calls) -> str (XMI)
"""
import uuid
import gen_ea_xmi as G

gid, brace, esc, newg = G.gid, G.brace, G.esc, G.newg
ROOT_ID, DATE, AUTHOR = G.ROOT_ID, G.DATE, G.AUTHOR

# capa para el layout 2D
LAYER = {'actor': 0, 'boundary': 1, 'control': 2, 'dao': 3, 'dto': 4, 'object': 3}


def _number_calls(calls, alias_seq):
    """Numeracion anidada por pila de contexto del emisor."""
    frames = []
    nums = []
    for s, r, _ in calls:
        while len(frames) > 1 and frames[-1]['obj'] != s:
            frames.pop()
        if not frames:
            frames.append({'obj': s, 'prefix': '', 'counter': 0})
        elif frames[-1]['obj'] != s:
            frames[-1] = {'obj': s, 'prefix': '', 'counter': 0}
        top = frames[-1]
        top['counter'] += 1
        num = (top['prefix'] + '.' if top['prefix'] else '') + str(top['counter'])
        nums.append(num)
        frames.append({'obj': r, 'prefix': num, 'counter': 0})
    return nums


def build_comm(pkg_name, participants, calls):
    PKGID = gid(newg())
    MODELID = 'MX_' + gid(newg())
    COLLABID = gid(newg())
    INTID = gid(newg())
    DIAGID = gid(newg())
    cnt = [1]
    loc = lambda: (cnt.__setitem__(0, cnt[0] + 1) or cnt[0])

    # objetos
    objs = []
    by_alias = {}
    layer_count = {}
    for alias, name, kind in participants:
        o = {'alias': alias, 'name': name[1:] if name.startswith(':') else name,
             'kind': kind, 'id': newg(), 'localid': loc(),
             'duid': uuid.uuid4().hex[:8].upper()}
        lay = LAYER.get(kind, 3)
        idx = layer_count.get(lay, 0)
        layer_count[lay] = idx + 1
        o['x'] = 60 + lay * 300
        o['y'] = 80 + idx * 170
        objs.append(o)
        by_alias[alias] = o

    nums = _number_calls(calls, [p[0] for p in participants])

    # enlaces (AssociationRole) por par no ordenado (o reflexivo)
    pair2link = {}
    links = []
    for s, r, _ in calls:
        key = frozenset((s, r)) if s != r else ('self', s)
        if key not in pair2link:
            lid = newg()
            so, ro = by_alias[s], by_alias[r]
            link = {'id': lid, 'src': so, 'tgt': ro, 'localid': loc()}
            pair2link[key] = link
            links.append(link)

    # mensajes
    msgs = []
    for (s, r, label), num in zip(calls, nums):
        key = frozenset((s, r)) if s != r else ('self', s)
        link = pair2link[key]
        msgs.append({'id': newg(), 'sender': by_alias[s], 'receiver': by_alias[r],
                     'label': label, 'num': num, 'link': link, 'localid': loc(),
                     'seqno': len(msgs) + 1})

    # separar los mensajes que comparten un mismo enlace para que NO se solapen
    per_link = {}
    for m in msgs:
        per_link.setdefault(m['link']['id'], []).append(m)
    for lid, ml in per_link.items():
        n = len(ml)
        so, ro = ml[0]['sender'], ml[0]['receiver']
        horizontal = abs(so['x'] - ro['x']) >= abs(so['y'] - ro['y'])
        for j, m in enumerate(ml):
            d = int((j - (n - 1) / 2.0) * 28)
            if so is ro:                      # auto-mensaje (loop)
                m['ox'], m['oy'] = 46, d
            elif horizontal:                  # enlace horizontal -> separar en vertical
                m['ox'], m['oy'] = 0, d
            else:                             # enlace vertical -> separar en horizontal
                m['ox'], m['oy'] = d, 0

    bottom = max((o['y'] for o in objs), default=200) + 120

    STYLE = 'BackColor=-1;BorderColor=-1;BorderWidth=-1;FontColor=-1;VSwimLanes=1;HSwimLanes=1;BorderStyle=0;'
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
    w('\t\t\t\t\t\t<UML:Collaboration xmi.id="%s_Collaboration" name="Collaborations">' % COLLABID)
    w('\t\t\t\t\t\t\t<UML:Namespace.ownedElement>')

    def otags(o):
        return [('isAbstract', 'false'), ('isSpecification', 'false'), ('ea_stype', 'Object'),
                ('ea_ntype', '0'), ('version', '1.0'), ('isActive', 'false'), ('package', PKGID),
                ('date_created', DATE), ('date_modified', DATE), ('gentype', '<none>'),
                ('tagged', '0'), ('package_name', pkg_name), ('phase', '1.0'), ('author', AUTHOR),
                ('complexity', '1'), ('status', 'Proposed'), ('tpos', '0'),
                ('ea_localid', str(o['localid'])), ('ea_eleType', 'element'), ('style', STYLE)]

    # objetos + enlaces intercalados (como en la plantilla, no importa el orden)
    for o in objs:
        w('\t\t\t\t\t\t\t\t<UML:ClassifierRole name="%s" xmi.id="%s" visibility="public" base="%s">'
          % (esc(o['name']), o['id'], ROOT_ID))
        w('\t\t\t\t\t\t\t\t\t<UML:ModelElement.taggedValue>')
        for t, v in otags(o):
            w('\t\t\t\t\t\t\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v)))
        w('\t\t\t\t\t\t\t\t\t</UML:ModelElement.taggedValue>')
        w('\t\t\t\t\t\t\t\t</UML:ClassifierRole>')

    for lk in links:
        so, ro = lk['src'], lk['tgt']
        w('\t\t\t\t\t\t\t\t<UML:AssociationRole xmi.id="%s" visibility="public" isRoot="false" isLeaf="false" isAbstract="false">' % lk['id'])
        w('\t\t\t\t\t\t\t\t\t<UML:ModelElement.taggedValue>')
        for t, v in [('style', '3'), ('ea_type', 'Association'), ('direction', 'Unspecified'),
                     ('linemode', '3'), ('linecolor', '-1'), ('linewidth', '0'), ('seqno', '0'),
                     ('headStyle', '0'), ('lineStyle', '0'), ('ea_localid', str(lk['localid'])),
                     ('ea_sourceName', so['name']), ('ea_targetName', ro['name']),
                     ('ea_sourceType', 'Object'), ('ea_targetType', 'Object'),
                     ('ea_sourceID', str(so['localid'])), ('ea_targetID', str(ro['localid'])),
                     ('src_visibility', 'Public'), ('src_aggregation', '0'), ('src_isOrdered', 'false'),
                     ('src_targetScope', 'instance'), ('src_changeable', 'none'),
                     ('src_isNavigable', 'false'), ('src_containment', 'Unspecified'),
                     ('src_style', 'Union=0;Derived=0;AllowDuplicates=0;Owned=0;Navigable=Unspecified;'),
                     ('dst_visibility', 'Public'), ('dst_aggregation', '0'), ('dst_isOrdered', 'false'),
                     ('dst_targetScope', 'instance'), ('dst_changeable', 'none'),
                     ('dst_isNavigable', 'false'), ('dst_containment', 'Unspecified'),
                     ('dst_style', 'Union=0;Derived=0;AllowDuplicates=0;Owned=0;Navigable=Unspecified;'),
                     ('virtualInheritance', '0')]:
            w('\t\t\t\t\t\t\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v)))
        w('\t\t\t\t\t\t\t\t\t</UML:ModelElement.taggedValue>')
        w('\t\t\t\t\t\t\t\t\t<UML:Association.connection>')
        w('\t\t\t\t\t\t\t\t\t\t<UML:AssociationEndRole visibility="public" aggregation="none" isOrdered="false" targetScope="instance" changeable="none" isNavigable="true" type="%s">' % so['id'])
        w('\t\t\t\t\t\t\t\t\t\t\t<UML:ModelElement.taggedValue>')
        w('\t\t\t\t\t\t\t\t\t\t\t\t<UML:TaggedValue tag="containment" value="Unspecified"/>')
        w('\t\t\t\t\t\t\t\t\t\t\t\t<UML:TaggedValue tag="ea_end" value="source"/>')
        w('\t\t\t\t\t\t\t\t\t\t\t</UML:ModelElement.taggedValue>')
        w('\t\t\t\t\t\t\t\t\t\t</UML:AssociationEndRole>')
        w('\t\t\t\t\t\t\t\t\t\t<UML:AssociationEndRole visibility="public" aggregation="none" isOrdered="false" targetScope="instance" changeable="none" isNavigable="true" type="%s">' % ro['id'])
        w('\t\t\t\t\t\t\t\t\t\t\t<UML:ModelElement.taggedValue>')
        w('\t\t\t\t\t\t\t\t\t\t\t\t<UML:TaggedValue tag="containment" value="Unspecified"/>')
        w('\t\t\t\t\t\t\t\t\t\t\t\t<UML:TaggedValue tag="ea_end" value="target"/>')
        w('\t\t\t\t\t\t\t\t\t\t\t</UML:ModelElement.taggedValue>')
        w('\t\t\t\t\t\t\t\t\t\t</UML:AssociationEndRole>')
        w('\t\t\t\t\t\t\t\t\t</UML:Association.connection>')
        w('\t\t\t\t\t\t\t\t</UML:AssociationRole>')

    w('\t\t\t\t\t\t\t</UML:Namespace.ownedElement>')
    w('\t\t\t\t\t\t\t<UML:Collaboration.interaction>')
    w('\t\t\t\t\t\t\t\t<UML:Interaction xmi.id="%s" name="%s">' % (INTID, INTID))
    w('\t\t\t\t\t\t\t\t\t<UML:Interaction.message>')
    for m in msgs:
        so, ro, lk = m['sender'], m['receiver'], m['link']
        lt = '%s: %s' % (m['num'], m['label'])
        w('\t\t\t\t\t\t\t\t\t\t<UML:Message name="%s" xmi.id="%s" visibility="public" sender="%s" receiver="%s" collaboration="%s">'
          % (esc(m['label']), m['id'], so['id'], ro['id'], lk['id']))
        w('\t\t\t\t\t\t\t\t\t\t\t<UML:ModelElement.taggedValue>')
        for t, v in [('message_link', lk['id']), ('style', '3'), ('ea_type', 'Collaboration'),
                     ('direction', 'Source -&gt; Destination'), ('linemode', '3'), ('linecolor', '-1'),
                     ('linewidth', '0'), ('seqno', str(m['seqno'])), ('headStyle', '0'), ('lineStyle', '0'),
                     ('privatedata1', 'Synchronous'), ('privatedata3', 'Call'), ('privatedata4', m['num']),
                     ('ea_localid', str(m['localid'])), ('ea_sourceName', so['name']),
                     ('ea_targetName', ro['name']), ('ea_sourceType', 'Object'), ('ea_targetType', 'Object'),
                     ('ea_sourceID', str(so['localid'])), ('ea_targetID', str(ro['localid'])),
                     ('src_visibility', 'Public'), ('src_isOrdered', 'false'), ('src_targetScope', 'instance'),
                     ('src_changeable', 'none'), ('src_isNavigable', 'false'), ('src_containment', 'Unspecified'),
                     ('src_style', 'Union=0;Derived=0;AllowDuplicates=0;Owned=0;Navigable=Non-Navigable;'),
                     ('dst_visibility', 'Public'), ('dst_aggregation', '0'), ('dst_isOrdered', 'false'),
                     ('dst_targetScope', 'instance'), ('dst_changeable', 'none'), ('dst_isNavigable', 'true'),
                     ('dst_containment', 'Unspecified'),
                     ('dst_style', 'Union=0;Derived=0;AllowDuplicates=0;Owned=0;Navigable=Navigable;'),
                     ('stateflags', 'IsReturn=false;'), ('virtualInheritance', '0'),
                     ('lt', lt), ('diagram', DIAGID)]:
            vv = v if t == 'direction' else esc(v)
            w('\t\t\t\t\t\t\t\t\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, vv))
        w('\t\t\t\t\t\t\t\t\t\t\t</UML:ModelElement.taggedValue>')
        w('\t\t\t\t\t\t\t\t\t\t</UML:Message>')
    w('\t\t\t\t\t\t\t\t\t</UML:Interaction.message>')
    w('\t\t\t\t\t\t\t\t</UML:Interaction>')
    w('\t\t\t\t\t\t\t</UML:Collaboration.interaction>')
    w('\t\t\t\t\t\t</UML:Collaboration>')
    w('\t\t\t\t\t</UML:Namespace.ownedElement>')
    w('\t\t\t\t</UML:Package>')
    w('\t\t\t</UML:Namespace.ownedElement>')
    w('\t\t</UML:Model>')

    # diagrama
    w('\t\t<UML:Diagram name="%s" xmi.id="%s" diagramType="CollaborationDiagram" owner="%s" toolName="Enterprise Architect 2.5">'
      % (esc(pkg_name), DIAGID, PKGID))
    w('\t\t\t<UML:ModelElement.taggedValue>')
    EASTYLE = ('ShowPrivate=1;ShowProtected=1;ShowPublic=1;HideRelationships=0;Locked=0;Border=1;'
               'HighlightForeign=1;PackageContents=1;SequenceNotes=0;ScalePrintImage=0;PPgs.cx=1;PPgs.cy=1;'
               'DocSize.cx=826;DocSize.cy=1169;ShowDetails=0;Orientation=P;Zoom=100;ShowTags=0;OpParams=1;'
               'VisibleAttributeDetail=0;ShowOpRetType=1;ShowIcons=1;CollabNums=1;HideProps=0;ShowReqs=0;'
               'ShowCons=0;PaperSize=9;HideParents=0;UseAlias=0;HideAtts=0;HideOps=0;HideStereo=0;'
               'HideElemStereo=0;ShowTests=0;ShowMaint=0;ConnectorNotation=UML 2.1;ExplicitNavigability=0;'
               'ShowShape=1;AllDockable=0;AdvancedElementProps=1;AdvancedFeatureProps=1;'
               'AdvancedConnectorProps=1;m_bElementClassifier=1;SPT=1;ShowNotes=0;SuppressBrackets=0;'
               'SuppConnectorLabels=0;PrintPageHeadFoot=0;ShowAsList=0;')
    for t, v in [('version', '1.0'), ('author', AUTHOR), ('created_date', DATE),
                 ('modified_date', DATE), ('package', PKGID), ('type', 'Collaboration'),
                 ('ea_localid', str(loc())), ('EAStyle', EASTYLE),
                 ('styleex', 'SaveTag=CEA3BDE1;SuppressFOC=1;TConnectorNotation=UML 2.1;SPT=1;Theme=:119;')]:
        w('\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v)))
    w('\t\t\t</UML:ModelElement.taggedValue>')
    w('\t\t\t<UML:Diagram.element>')
    sq = 0
    for o in objs:
        sq += 1
        L, T = o['x'], o['y']
        w('\t\t\t\t<UML:DiagramElement geometry="Left=%d;Top=%d;Right=%d;Bottom=%d;" subject="%s" seqno="%d" style="DUID=%s;"/>'
          % (L, T, L + 110, T + 60, o['id'], sq, o['duid']))
    for lk in links:
        w('\t\t\t\t<UML:DiagramElement geometry="SX=0;SY=0;EX=0;EY=0;EDGE=1;$LLB=;LLT=;LMT=;LMB=;LRT=;LRB=;IRHS=;ILHS=;Path=;" subject="%s" style="Mode=3;EOID=%s;SOID=%s;Color=-1;LWidth=0;Hidden=0;"/>'
          % (lk['id'], lk['tgt']['duid'], lk['src']['duid']))
    for m in msgs:
        w('\t\t\t\t<UML:DiagramElement geometry="SX=%d;SY=%d;EX=%d;EY=%d;EDGE=2;$LLB=;LLT=;LMT=;LMB=;LRT=;LRB=;IRHS=;ILHS=;Path=;" subject="%s" style="Mode=1;EOID=%s;SOID=%s;Color=-1;LWidth=0;Hidden=0;"/>'
          % (m['ox'], m['oy'], m['ox'], m['oy'], m['id'], m['receiver']['duid'], m['sender']['duid']))
    w('\t\t\t</UML:Diagram.element>')
    w('\t\t</UML:Diagram>')
    G._footer(w)
    return '\n'.join(out) + '\n'
