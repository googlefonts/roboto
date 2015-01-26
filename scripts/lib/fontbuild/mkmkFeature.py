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
		for anchor in g.anchors:
			if anchor_name == anchor.name:
				g_list.append([g.name, anchor.x, anchor.y])
				break
	return g_list

def Create_mkmk1(accent_g_list, base_g_list, lookupname):
	txt = "lookup " + lookupname + " {\n"
	acc_class = "@MC_mkmk"
	for acc in accent_g_list:
		txt += "  markClass " + acc[0] + " <anchor " + `acc[1]` + " " + `acc[2]` + "> " + acc_class +";\n"
	
	for base in base_g_list:
		txt += "  pos mark " + base[0] + " <anchor " + `base[1]` + " " + `base[2]` + "> mark " + acc_class + ";\n"
	
	txt += "} " + lookupname + ";\n"
	
	return txt


##### main ##############
def GenerateFeature_mkmk(font):
  text = "feature mkmk {\n"

  accent_name_list = []
  accent_mark_list = []
  base_mark_list = []
  anchor_name = "mkmktop"
  acc_anchor_name = "_marktop"
  accent_name_list = CreateAccNameList(font, acc_anchor_name)
  accent_mark_list = CreateAccGlyphList(font, accent_name_list, acc_anchor_name)
  base_mark_list = CreateGlyphList(font, accent_name_list, anchor_name)
  text += Create_mkmk1(accent_mark_list, base_mark_list, "mkmk1")

  text += "} mkmk;\n"
  mkmk = Feature("mkmk", text)

  not_exist = True
  for n in range(len(font.features)):
    if ('mkmk' == font.features[n].tag):
      font.features[n] = mkmk
      not_exist = False

  if (not_exist):
    font.features.append(mkmk)
