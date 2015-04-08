from fontbuild.features import updateFeature


aliases = [["uni0430", "a"], ["uni0435", "e"], ["uni0440", "p"], ["uni0441", "c"], ["uni0445", "x"], ["uni0455", "s"], ["uni0456", "i"], ["uni0471", "psi"]]

def GetAliaseName(gname):
	for i in range (len(aliases)):
		if (gname == aliases[i][1]):
			return aliases[i][0]
	return None		

def CreateAccNameList(font, acc_anchor_name, bCombAccentOnly = True):
	#combrange = range(0x0300,0x0370) + range(0x1AB0,0x1ABF) + range(0x1DC0,0x1DE0)
	lst = []
	for g in font:
		if bCombAccentOnly and g.width != 0: #((g.unicode < 0x0300) or (g.unicode > 0x362)):
			continue
		for anchor in g.anchors:
			if acc_anchor_name == anchor.name:
				lst.append(g.name)
	return lst

def CreateAccGlyphList(font, acc_list, acc_anchor_name):
	g_list = []
	for g in font:
		if g.name in acc_list:
			for anchor in g.anchors:
				if acc_anchor_name == anchor.name:
					g_list.append([g.name, anchor.x, anchor.y])
					break
	return g_list


def CreateGlyphList(font, acc_list, anchor_name):
	g_list = []
	for g in font:
		if g.name in acc_list:
			continue
		for anchor in g.anchors:
			if anchor_name == anchor.name:
				g_list.append([g.name, anchor.x, anchor.y])
				break
	return g_list

def Create_mark_lookup(accent_g_list, base_g_list, lookupname, acc_class, lookAliases = True):
	txt = "lookup " + lookupname + " {\n"
	
	for acc in accent_g_list:
		txt += "  markClass " + acc[0] + " <anchor " + `acc[1]` + " " + `acc[2]` + "> " + acc_class +";\n"	
	
	for base in base_g_list:
		txt += "  pos base " + base[0] + " <anchor " + `base[1]` + " " + `base[2]` + "> mark " + acc_class + ";\n"
		if (lookAliases):
			base2 = GetAliaseName(base[0])
			if (None == base2):
				continue
			txt += "  pos base " + base2 + " <anchor " + `base[1]` + " " + `base[2]` + "> mark " + acc_class + ";\n"	

	txt += "} " + lookupname + ";\n"
	
	return txt

##### main ##############
def GenerateFeature_mark(font):

  combination_anchor_list = [
	["top", "_marktop", True, True],
	["bottom", "_markbottom", True, True],
	["top_dd", "_marktop_dd", True, False],	
	["bottom_dd", "_markbottom_dd", True, False],
	["rhotichook", "_markrhotichook", False, False],
	["top0315", "_marktop0315", False, False],
	["parent_top", "_markparent_top", False, False],
	["parenthesses.w1", "_markparenthesses.w1", False, False],
	["parenthesses.w2", "_markparenthesses.w2", False, False],
	["parenthesses.w3", "_markparenthesses.w3", False, False]	
  ]

  text = "feature mark {\n"

  for n in range(len(combination_anchor_list)):
	
	accent_name_list = []
	accent_mark_list = []
	base_mark_list = []
	
	anchors_pair = combination_anchor_list[n]
	anchor_name = anchors_pair[0]
	acc_anchor_name = anchors_pair[1]
	comb_accent_only = anchors_pair[2]
	expand_to_composits = anchors_pair[3]
	lookupname = "mark"+`n+1`
	classname = "@MC_" + anchor_name

	accent_name_list = CreateAccNameList(font, acc_anchor_name, comb_accent_only)
	accent_mark_list = CreateAccGlyphList(font, accent_name_list, acc_anchor_name)
	base_mark_list = CreateGlyphList(font, accent_name_list, anchor_name)
	text += Create_mark_lookup(accent_mark_list, base_mark_list, lookupname, classname, expand_to_composits)

  text += "} mark;\n"

  updateFeature(font, "mark", text)
