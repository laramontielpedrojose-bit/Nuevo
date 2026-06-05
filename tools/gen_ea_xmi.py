#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convierte un Diagrama de Secuencia exportado como XMI 2.1 (UML 2.1) de
Enterprise Architect al dialecto NATIVO XMI 1.1 / UML 1.3 de EA
(igual que la plantilla 'algo sucede.xml'), que es el que importa de forma
fiable en Enterprise Architect 15.

Reglas de modelado:
  - Lifelines  -> UML:ClassifierRole (objetos) / UML:Actor (actores)
  - Estereotipos boundary/control/entity via <UML:Stereotype> + $ea_xref_property
  - synchCall   -> Mensaje Synchronous / Call   (flecha solida)
  - reply       -> Mensaje Synchronous / Return (linea punteada -->)
  - createMessage -> Mensaje Synchronous / Call
  - CombinedFragment alt/opt/loop -> UML:Class ea_stype=InteractionFragment
        con particiones (operandos/guardas) en $ea_xref_property
"""
import sys, re, uuid
import xml.etree.ElementTree as ET

UML = '{http://schema.omg.org/spec/UML/2.1}'
XMI = '{http://schema.omg.org/spec/XMI/2.1}'

# ea_ntype para el operador del fragmento combinado (deducido de la plantilla:
# alt=0, opt=1; loop=2 por extrapolacion)
OP_NTYPE = {'alt': 0, 'opt': 1, 'loop': 2, 'break': 3, 'par': 4, 'seq': 5,
            'critical': 6, 'neg': 7, 'assert': 8, 'ignore': 9, 'consider': 10}

ROOT_ID = 'EAID_11111111_5487_4080_A7F4_41526CB0AA00'


def gid(src):
    """EAID_ + 32 hex  ->  EAID_8_4_4_4_12 (formato nativo EA)."""
    h = src.replace('EAID_', '').replace('-', '').replace('_', '')
    h = (h + '0' * 32)[:32].upper()
    return 'EAID_%s_%s_%s_%s_%s' % (h[0:8], h[8:12], h[12:16], h[16:20], h[20:32])


def brace(src):
    """ -> {8-4-4-4-12} para $ea_xref_property."""
    h = src.replace('EAID_', '').replace('-', '').replace('_', '')
    h = (h + '0' * 32)[:32].upper()
    return '{%s-%s-%s-%s-%s}' % (h[0:8], h[8:12], h[12:16], h[16:20], h[20:32])


def esc(s):
    if s is None:
        s = ''
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('"', '&quot;'))


def newg():
    u = uuid.uuid4().hex.upper()
    return 'EAID_%s' % u


class P:  # participante (lifeline)
    pass


def parse(path):
    tree = ET.parse(path)
    root = tree.getroot()
    model = root.find(UML + 'Model')
    pkg = model.find('packagedElement')
    pkg_name = pkg.get('name')

    # actores declarados
    actor_ids = set()
    for pe in pkg.findall('packagedElement'):
        if pe.get(XMI + 'type') == 'uml:Actor':
            actor_ids.add(pe.get(XMI + 'id'))

    # ownedAttribute (property id -> classifier/type id)  dentro del Collaboration
    collab = None
    for pe in pkg.findall('packagedElement'):
        if pe.get(XMI + 'type') == 'uml:Collaboration':
            collab = pe
            break
    prop_type = {}
    for oa in collab.findall('ownedAttribute'):
        prop_type[oa.get(XMI + 'id')] = oa.get('type')

    interaction = collab.find('ownedBehavior')

    # estereotipos desde la extension
    stereo = {}
    ext = root.find(XMI + 'Extension')
    if ext is not None:
        for el in ext.iter('element'):
            if el.get(XMI + 'type') == 'uml:Lifeline':
                pr = el.find('properties')
                if pr is not None and pr.get('stereotype'):
                    stereo[el.get(XMI + 'idref')] = pr.get('stereotype')

    # participantes en orden
    parts = []           # lista de P
    by_id = {}
    for i, lf in enumerate(interaction.findall('lifeline')):
        p = P()
        p.id = lf.get(XMI + 'id')
        nm = lf.get('name') or ''
        p.name = nm[1:] if nm.startswith(':') else nm   # quita ':' inicial
        cls = prop_type.get(lf.get('represents'))
        p.is_actor = cls in actor_ids
        p.stereo = stereo.get(p.id)
        p.localid = i + 2          # localids 2..n
        parts.append(p)
        by_id[p.id] = p

    # mos id -> lifeline id  (tag 'fragment' con xmi:type MessageOccurrenceSpecification)
    mos_cover = {}
    for mos in interaction.iter('fragment'):
        if (mos.get(XMI + 'type') or '').endswith('MessageOccurrenceSpecification'):
            mos_cover[mos.get(XMI + 'id')] = mos.get('covered')

    # mensajes: id -> (name, sort, sendMos, recvMos)
    msgs = {}
    for m in interaction.findall('message'):
        msgs[m.get(XMI + 'id')] = {
            'name': m.get('name') or '',
            'sort': m.get('messageSort') or 'synchCall',
            'send': m.get('sendEvent'),
            'recv': m.get('receiveEvent'),
        }

    # recorrido en orden de documento para asignar seqno y construir fragmentos
    order = []           # ids de mensaje en orden vertical
    seen = set()
    frags = []           # combined fragments
    stack = []           # pila de fragmentos abiertos

    def walk(node):
        for ch in list(node):
            tag = ch.tag
            xt = ch.get(XMI + 'type') or ''
            if tag == 'fragment' and xt.endswith('MessageOccurrenceSpecification'):
                mid = ch.get('message')
                if mid and mid not in seen:
                    seen.add(mid)
                    order.append(mid)
                    s = len(order)          # seqno 1..n
                    msgs[mid]['seqno'] = s
                    for fr in stack:
                        fr['seqs'].append(s)
            elif tag == 'fragment' and xt.endswith('CombinedFragment'):
                fr = {
                    'id': ch.get(XMI + 'id'),
                    'op': ch.get('interactionOperator') or 'alt',
                    'covered': (ch.get('covered') or '').split(),
                    'operands': [],
                    'seqs': [],
                    'depth': len(stack),
                }
                for opd in ch.findall('operand'):
                    g = ''
                    gd = opd.find('guard')
                    if gd is not None:
                        sp = gd.find('specification')
                        if sp is not None and sp.get('body'):
                            g = sp.get('body')
                    fr['operands'].append(g)
                frags.append(fr)
                stack.append(fr)
                walk(ch)
                stack.pop()
            else:
                walk(ch)

    walk(interaction)

    # senders/receivers de cada mensaje (por lifeline)
    for mid, m in msgs.items():
        m['sender'] = mos_cover.get(m['send'])
        m['receiver'] = mos_cover.get(m['recv'])

    return pkg_name, parts, by_id, msgs, order, frags


# ----------------------------- emision ------------------------------------

def build(path):
    pkg_name, parts, by_id, msgs, order, frags = parse(path)

    PKGID = gid(newg())
    MODELID = 'MX_' + gid(newg())
    COLLABID = gid(newg())
    INTID = gid(newg())
    DIAGID = gid(newg())
    DATE = '2026-06-05 12:00:00'
    AUTHOR = 'EA'

    # geometria: columnas de lifelines
    STEP = 200
    LX = 40
    for i, p in enumerate(parts):
        p.left = LX + i * STEP
        p.width = 90 if p.is_actor else 100
        p.right = p.left + p.width
        p.center = p.left + p.width // 2

    def ymsg(s):
        return 130 + s * 40

    nmsg = len(order)
    bottom = ymsg(nmsg + 1) + 60

    out = []
    w = out.append
    w('<?xml version="1.0" encoding="windows-1252"?>')
    w('<XMI xmi.version="1.1" xmlns:UML="omg.org/UML1.3" timestamp="%s">' % DATE)
    w('\t<XMI.header>')
    w('\t\t<XMI.documentation>')
    w('\t\t\t<XMI.exporter>Enterprise Architect</XMI.exporter>')
    w('\t\t\t<XMI.exporterVersion>2.5</XMI.exporterVersion>')
    w('\t\t</XMI.documentation>')
    w('\t</XMI.header>')
    w('\t<XMI.content>')
    w('\t\t<UML:Model name="EA Model" xmi.id="%s">' % MODELID)
    w('\t\t\t<UML:Namespace.ownedElement>')
    w('\t\t\t\t<UML:Class name="EARootClass" xmi.id="%s" isRoot="true" isLeaf="false" isAbstract="false"/>' % ROOT_ID)
    w('\t\t\t\t<UML:Package name="%s" xmi.id="%s" isRoot="false" isLeaf="false" isAbstract="false" visibility="public">' % (esc(pkg_name), PKGID))
    w('\t\t\t\t\t<UML:ModelElement.taggedValue>')
    for t, v in [('ea_package_id', '2'), ('created', DATE), ('modified', DATE),
                 ('iscontrolled', 'FALSE'), ('isprotected', 'FALSE'),
                 ('version', '1.0'), ('author', AUTHOR), ('status', 'Proposed'),
                 ('ea_stype', 'Public')]:
        w('\t\t\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v)))
    w('\t\t\t\t\t</UML:ModelElement.taggedValue>')
    w('\t\t\t\t\t<UML:Namespace.ownedElement>')

    # --- Collaboration con ClassifierRoles + Interaction ---
    w('\t\t\t\t\t\t<UML:Collaboration xmi.id="%s_Collaboration" name="Collaborations">' % COLLABID)
    w('\t\t\t\t\t\t\t<UML:Namespace.ownedElement>')
    for p in parts:
        if p.is_actor:
            continue
        w('\t\t\t\t\t\t\t\t<UML:ClassifierRole name="%s" xmi.id="%s" visibility="public" base="%s">'
          % (esc(p.name), gid(p.id), ROOT_ID))
        if p.stereo:
            w('\t\t\t\t\t\t\t\t\t<UML:ModelElement.stereotype>')
            w('\t\t\t\t\t\t\t\t\t\t<UML:Stereotype name="%s"/>' % esc(p.stereo))
            w('\t\t\t\t\t\t\t\t\t</UML:ModelElement.stereotype>')
        w('\t\t\t\t\t\t\t\t\t<UML:ModelElement.taggedValue>')
        tv = [('isSpecification', 'false'), ('ea_stype', 'Sequence'), ('ea_ntype', '0'),
              ('version', '1.0'), ('isActive', 'false'), ('package', PKGID),
              ('date_created', DATE), ('date_modified', DATE),
              ('package_name', pkg_name), ('phase', '1.0'), ('author', AUTHOR),
              ('status', 'Proposed')]
        if p.stereo:
            tv.append(('stereotype', p.stereo))
        tv += [('tpos', '0'), ('ea_localid', str(p.localid)), ('ea_eleType', 'element'),
               ('style', 'BackColor=-1;BorderColor=-1;BorderWidth=-1;FontColor=-1;VSwimLanes=1;HSwimLanes=1;BorderStyle=0;')]
        for t, v in tv:
            w('\t\t\t\t\t\t\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v)))
        if p.stereo:
            xref = ('$XREFPROP=$XID=%s$XID;$NAM=Stereotypes$NAM;$TYP=element property$TYP;'
                    '$VIS=Public$VIS;$PAR=0$PAR;$DES=@STEREO;Name=%s;FQName=EAUML::%s;@ENDSTEREO;$DES;'
                    '$CLT=%s$CLT;$SUP=<none>$SUP;$ENDXREF;'
                    % (brace(newg()), p.stereo, p.stereo, brace(p.id)))
            w('\t\t\t\t\t\t\t\t\t\t<UML:TaggedValue tag="$ea_xref_property" value="%s"/>' % esc(xref))
        w('\t\t\t\t\t\t\t\t\t</UML:ModelElement.taggedValue>')
        w('\t\t\t\t\t\t\t\t</UML:ClassifierRole>')
    w('\t\t\t\t\t\t\t</UML:Namespace.ownedElement>')

    # Interaction + mensajes
    w('\t\t\t\t\t\t\t<UML:Collaboration.interaction>')
    w('\t\t\t\t\t\t\t\t<UML:Interaction xmi.id="%s" name="%s">' % (INTID, INTID))
    w('\t\t\t\t\t\t\t\t\t<UML:Interaction.message>')
    for mid in order:
        m = msgs[mid]
        s = by_id.get(m['sender'])
        r = by_id.get(m['receiver'])
        if s is None or r is None:
            continue
        seq = m['seqno']
        is_ret = (m['sort'] == 'reply')
        pkind = 'Return' if is_ret else 'Call'
        name = m['name']
        sx, ex = s.center, r.center
        y = -ymsg(seq)
        nm_attr = (' name="%s"' % esc(name)) if name else ''
        w('\t\t\t\t\t\t\t\t\t\t<UML:Message%s xmi.id="%s" visibility="public" sender="%s" receiver="%s">'
          % (nm_attr, gid(mid), gid(m['sender']), gid(m['receiver'])))
        w('\t\t\t\t\t\t\t\t\t\t\t<UML:ModelElement.taggedValue>')
        mt = name if ('(' in name or not name) else name + '()'
        tv = [('style', '1'), ('ea_type', 'Sequence'),
              ('direction', 'Source -&gt; Destination'),
              ('linemode', '1'), ('linecolor', '-1'), ('linewidth', '0'),
              ('seqno', str(seq)), ('headStyle', '0'), ('lineStyle', '0'),
              ('privatedata1', 'Synchronous'), ('privatedata2', 'retval=void;'),
              ('privatedata3', pkind), ('privatedata4', '0'),
              ('ea_localid', str(seq + 100)),
              ('ea_sourceName', s.name), ('ea_targetName', r.name),
              ('ea_sourceType', 'Actor' if s.is_actor else 'Sequence'),
              ('ea_targetType', 'Actor' if r.is_actor else 'Sequence'),
              ('ea_sourceID', str(s.localid)), ('ea_targetID', str(r.localid)),
              ('src_visibility', 'Public'), ('src_isOrdered', 'false'),
              ('src_targetScope', 'instance'), ('src_changeable', 'none'),
              ('src_isNavigable', 'false'), ('src_containment', 'Unspecified'),
              ('src_style', 'Union=0;Derived=0;AllowDuplicates=0;Owned=0;Navigable=Non-Navigable;'),
              ('dst_visibility', 'Public'), ('dst_aggregation', '0'),
              ('dst_isOrdered', 'false'), ('dst_targetScope', 'instance'),
              ('dst_changeable', 'none'), ('dst_isNavigable', 'true'),
              ('dst_containment', 'Unspecified'),
              ('dst_style', 'Union=0;Derived=0;AllowDuplicates=0;Owned=0;Navigable=Navigable;'),
              ('privatedata5', 'SX=0;SY=0;EX=0;EY=0;$LLB=;LLT=;LMT=;LMB=;LRT=;LRB=;IRHS=;ILHS=;'),
              ('sequence_points', 'PtStartX=%d;PtStartY=%d;PtEndX=%d;PtEndY=%d;' % (sx, y, ex, y)),
              ('stateflags', 'Activation=0;'),
              ('virtualInheritance', '0'), ('diagram', DIAGID)]
        if name:
            tv.append(('mt', mt))
        for t, v in tv:
            w('\t\t\t\t\t\t\t\t\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v) if t != 'direction' else v))
        w('\t\t\t\t\t\t\t\t\t\t\t</UML:ModelElement.taggedValue>')
        w('\t\t\t\t\t\t\t\t\t\t</UML:Message>')
    w('\t\t\t\t\t\t\t\t\t</UML:Interaction.message>')
    w('\t\t\t\t\t\t\t\t</UML:Interaction>')
    w('\t\t\t\t\t\t\t</UML:Collaboration.interaction>')
    w('\t\t\t\t\t\t</UML:Collaboration>')

    # --- Actores ---
    for p in parts:
        if not p.is_actor:
            continue
        w('\t\t\t\t\t\t<UML:Actor name="%s" xmi.id="%s" visibility="public" namespace="%s" isRoot="false" isLeaf="false" isAbstract="false">'
          % (esc(p.name), gid(p.id), PKGID))
        w('\t\t\t\t\t\t\t<UML:ModelElement.taggedValue>')
        for t, v in [('isSpecification', 'false'), ('ea_stype', 'Actor'), ('ea_ntype', '0'),
                     ('version', '1.0'), ('isActive', 'false'), ('package', PKGID),
                     ('date_created', DATE), ('date_modified', DATE),
                     ('package_name', pkg_name), ('phase', '1.0'), ('author', AUTHOR),
                     ('status', 'Proposed'), ('tpos', '0'), ('ea_localid', str(p.localid)),
                     ('ea_eleType', 'element'),
                     ('style', 'BackColor=-1;BorderColor=-1;BorderWidth=-1;FontColor=-1;VSwimLanes=1;HSwimLanes=1;BorderStyle=0;')]:
            w('\t\t\t\t\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v)))
        w('\t\t\t\t\t\t\t</UML:ModelElement.taggedValue>')
        w('\t\t\t\t\t\t</UML:Actor>')

    # --- Fragmentos combinados (InteractionFragment) ---
    for fi, fr in enumerate(frags):
        fr['localid'] = 500 + fi
        ntype = OP_NTYPE.get(fr['op'], 0)
        # particiones (operandos/guardas)
        partitions = ''
        for g in fr['operands']:
            partitions += '@PAR;Name=%s;Size=100;GUID=%s;@ENDPAR;' % (g, brace(newg()))
        xref = ('$XREFPROP=$XID=%s$XID;$NAM=Partitions$NAM;$TYP=element property$TYP;'
                '$VIS=Public$VIS;$PAR=0$PAR;$DES=%s$DES;$CLT=%s$CLT;$SUP=<none>$SUP;$ENDXREF;'
                % (brace(newg()), partitions, brace(fr['id'])))
        w('\t\t\t\t\t\t<UML:Class xmi.id="%s" visibility="public" namespace="%s" isRoot="false" isLeaf="false" isAbstract="false">'
          % (gid(fr['id']), PKGID))
        w('\t\t\t\t\t\t\t<UML:ModelElement.taggedValue>')
        tv = [('isSpecification', 'false'), ('ea_stype', 'InteractionFragment'),
              ('ea_ntype', str(ntype)), ('version', '1.0'), ('isActive', 'false'),
              ('package', PKGID), ('date_created', DATE), ('date_modified', DATE),
              ('package_name', pkg_name), ('phase', '1.0'), ('author', AUTHOR),
              ('status', 'Proposed'), ('styleex', 'ConstructID=0;'), ('tpos', '0'),
              ('ea_localid', str(fr['localid'])), ('ea_eleType', 'element'),
              ('diagram', DIAGID),
              ('style', 'BackColor=-1;BorderColor=-1;BorderWidth=-1;FontColor=-1;VSwimLanes=1;HSwimLanes=1;BorderStyle=3;')]
        for t, v in tv:
            w('\t\t\t\t\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v)))
        w('\t\t\t\t\t\t\t\t<UML:TaggedValue tag="$ea_xref_property" value="%s"/>' % esc(xref))
        w('\t\t\t\t\t\t\t</UML:ModelElement.taggedValue>')
        w('\t\t\t\t\t\t</UML:Class>')

    w('\t\t\t\t\t</UML:Namespace.ownedElement>')
    w('\t\t\t\t</UML:Package>')
    w('\t\t\t</UML:Namespace.ownedElement>')
    w('\t\t</UML:Model>')

    # --- Diagrama ---
    w('\t\t<UML:Diagram name="%s" xmi.id="%s" diagramType="SequenceDiagram" owner="%s" toolName="Enterprise Architect 2.5">'
      % (esc(pkg_name), DIAGID, PKGID))
    w('\t\t\t<UML:ModelElement.taggedValue>')
    for t, v in [('version', '1.0'), ('author', AUTHOR), ('created_date', DATE),
                 ('modified_date', DATE), ('package', PKGID), ('type', 'Sequence'),
                 ('ea_localid', '1'),
                 ('EAStyle', 'ShowPrivate=1;ShowProtected=1;ShowPublic=1;Locked=0;Border=1;'
                             'HighlightForeign=1;PackageContents=1;SequenceNotes=0;Orientation=P;'
                             'Zoom=100;ConnectorNotation=UML 2.1;'),
                 ('styleex', 'SeqTopMargin=50;SwimlanesActive=1;TConnectorNotation=UML 2.1;')]:
        w('\t\t\t\t<UML:TaggedValue tag="%s" value="%s"/>' % (t, esc(v)))
    w('\t\t\t</UML:ModelElement.taggedValue>')
    w('\t\t\t<UML:Diagram.element>')
    seqn = 0
    # lifelines y actores
    for p in parts:
        seqn += 1
        w('\t\t\t\t<UML:DiagramElement geometry="Left=%d;Top=50;Right=%d;Bottom=%d;" subject="%s" seqno="%d" style="DUID=%s;"/>'
          % (p.left, p.right, bottom, gid(p.id), seqn, uuid.uuid4().hex[:8].upper()))
    # fragmentos
    for fr in frags:
        seqn += 1
        seqs = fr['seqs'] or [1]
        cov = [by_id[c] for c in fr['covered'] if c in by_id]
        if cov:
            fl = min(c.left for c in cov) - 25 + fr['depth'] * 10
            frr = max(c.right for c in cov) + 25 - fr['depth'] * 10
        else:
            fl, frr = 20, 700
        ftop = ymsg(min(seqs)) - 28
        fbot = ymsg(max(seqs)) + 16
        w('\t\t\t\t<UML:DiagramElement geometry="Left=%d;Top=%d;Right=%d;Bottom=%d;" subject="%s" seqno="%d" style="DUID=%s;"/>'
          % (fl, ftop, frr, fbot, gid(fr['id']), seqn, uuid.uuid4().hex[:8].upper()))
    # conectores (mensajes) con geometria nula
    for mid in order:
        w('\t\t\t\t<UML:DiagramElement geometry="SX=0;SY=0;EX=0;EY=0;Path=;" subject="%s" style=";Hidden=0;"/>'
          % gid(mid))
    w('\t\t\t</UML:Diagram.element>')
    w('\t\t</UML:Diagram>')
    w('\t</XMI.content>')
    w('\t<XMI.difference/>')
    w('\t<XMI.extensions xmi.extender="Enterprise Architect 2.5"/>')
    w('</XMI>')
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    src = sys.argv[1]
    dst = sys.argv[2]
    xml = build(src)
    with open(dst, 'w', encoding='cp1252', errors='xmlcharrefreplace') as f:
        f.write(xml)
    print('OK ->', dst)
