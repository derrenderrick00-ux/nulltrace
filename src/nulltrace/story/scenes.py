"""Canonical three-act chapter summaries; interactive story outlines."""
CHAPTERS={
1:('THE AWAKENING','Meridian Network Operations · 03:17','JONAH VALE: The office workstation reports a routing failure. Start with the basics; explain what each check proves.','UNKNOWN: You repaired the connection. But why was MIRROR-07 monitoring that workstation?'),
2:('THE INVISIBLE NETWORK','Meridian Network Operations · Network floor','JONAH VALE: Somebody omitted a network segment from the topology. Determine what can actually reach what.','MARA VOSS: A missing box on a diagram is not proof of malice. Find the physical and logical evidence.'),
3:('THE LANGUAGE OF MACHINES','Meridian Network Operations · Archive terminal','JONAH VALE: Follow the protocols. Those DNS records might be ordinary, or something more.','UNKNOWN: MIRROR is larger than the documentation suggests. But an unusual query proves very little alone.'),
4:('GHOST ROUTES','Meridian Network Operations · Network mapping room','MARA VOSS: The route report and the observed path do not agree. Work out where the evidence stops.','DR. IMANI KADE: Metadata can mislead. Routers can decline to respond without dropping forwarded traffic.'),
5:('THE PACKET FILES','Archive Room · Evidence Review','DR. IMANI KADE: There is a capture file. Protect the original and distinguish payloads from metadata.','MARA VOSS: Their report overstates the case. Show exactly what the packets do and do not tell us.'),
6:('THE OPEN DOORS','Meridian · Authorized Laboratory','JONAH VALE: We have written permission for the training server only. Do not scan the production network.','ELIAS ROOK: Finding an open port does not prove compromise. Document the exposure and your uncertainty.'),
7:('THE FORGOTTEN KEYS','Secure Archive · Training Vault','DR. IMANI KADE: A synthetic credential exercise explains how predictable passwords fail.','UNKNOWN: SPECTER is a shared operational identity. The evidence points to more than one actor.'),
8:('BEHIND THE BROWSER','MIRROR Local Web Laboratory · Authorization review','MARA VOSS: The MIRROR portal uses object IDs to serve case records. Does it check who requests them?','IMANI KADE: Changing an ID is not inherently wrong; the missing server-side access check is the defect.'),
9:('THE SHADOW NETWORK','Meridian Archive · Incident Response Room','JONAH VALE: MIRROR-07 exists in an independent archive, yet the official summary denies it. Compare sources.','ELIAS ROOK: A conflict between logs is not proof of intent. Preserve both, then seek independent review.'),
10:('THE NEXUS PROTOCOL','NEXUS Council · Final Evidence Hearing','IMANI KADE: This dossier is yours to defend. Every claim requires provenance, limits, and a remedy.','MARA VOSS: Whether you disclose to oversight, broadly, or restrict access determines the aftermath.'),
}

INTRO=(
    'YEAR 2038 // MERIDIAN NETWORK OPERATIONS',
    'Your first task is to diagnose a workstation connection. Your identity is yours; your origin as a junior technician is fixed.',
    'This is a story about what network evidence can prove—and what it cannot. Every live security task stays in a permitted training lab.'
)
