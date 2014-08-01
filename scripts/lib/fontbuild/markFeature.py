from FL import *

aliases = [["uni0430", "a"], ["uni0435", "e"], ["uni0440", "p"], ["uni0441", "c"], ["uni0445", "x"], ["uni0455", "s"], ["uni0456", "i"], ["uni0471", "psi"]]

def GetAliaseName(gname):
	for i in range (len(aliases)):
		if (gname == aliases[i][1]):
			return aliases[i][0]
	return None		

def CreateAccNameList(font, acc_anchor_name):
	lst = []
	for g in font.glyphs:
		for anchor in g.anchors:
			if acc_anchor_name == anchor.name:
				lst.append(g.name)
	return lst

def CreateAccGlyphList(font, acc_list, acc_anchor_name):
	g_list = []
	for g in font.glyphs:
		if g.name in acc_list:
			for anchor in g.anchors:
				if acc_anchor_name == anchor.name:
					g_list.append([g.name, anchor.x, anchor.y])
					break
	return g_list


def CreateGlyphList(font, acc_list, anchor_name):
	g_list = []
	for g in font.glyphs:
		if g.name in acc_list:
			continue
		for anchor in g.anchors:
			if anchor_name == anchor.name:
				g_list.append([g.name, anchor.x, anchor.y])
				break
	return g_list

def Create_mark_lookup(accent_g_list, base_g_list, lookupname, acc_class):
	txt = "lookup " + lookupname + " {\n"
	
	for acc in accent_g_list:
		txt += "  markClass " + acc[0] + " <anchor " + `acc[1]` + " " + `acc[2]` + "> " + acc_class +";\n"	
	
	for base in base_g_list:
		txt += "  pos base " + base[0] + " <anchor " + `base[1]` + " " + `base[2]` + "> mark " + acc_class + ";\n"
		base2 = GetAliaseName(base[0])
		if (None == base2):
			continue
		txt += "  pos base " + base2 + " <anchor " + `base[1]` + " " + `base[2]` + "> mark " + acc_class + ";\n"	

	txt += "} " + lookupname + ";\n"
	
	return txt

##### main ##############
def GenerateFeature_mark(font):
  text = "feature mark {\n"

  accent_name_list = []
  accent_mark_list = []
  base_mark_list = []
  anchor_name = "top"
  acc_anchor_name = "_mark" + anchor_name
  accent_name_list = CreateAccNameList(font, acc_anchor_name)
  accent_mark_list = CreateAccGlyphList(font, accent_name_list, acc_anchor_name)
  base_mark_list = CreateGlyphList(font, accent_name_list, anchor_name)
  text += Create_mark_lookup(accent_mark_list, base_mark_list, "mark1", "@MC_top")

  accent_name_list = []
  accent_mark_list = []
  base_mark_list = []
  anchor_name = "bottom"
  acc_anchor_name = "_mark" + anchor_name
  accent_name_list = CreateAccNameList(font, acc_anchor_name)
  accent_mark_list = CreateAccGlyphList(font, accent_name_list, acc_anchor_name)
  base_mark_list = CreateGlyphList(font, accent_name_list, anchor_name)
  text += Create_mark_lookup(accent_mark_list, base_mark_list, "mark2", "@MC_bottom")


  text += "} mark;\n"
  mark = Feature("mark", text)

  not_exist = True
  for n in range(len(font.features)):
    if ('mark' == font.features[n].tag):
      font.features[n] = mark
      not_exist = False

  if (not_exist):
    font.features.append(mark)
