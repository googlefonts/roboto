# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from fontbuild.features import updateFeature


def CreateAccNameList(font, acc_anchor_name):
	lst = []
	for g in font:
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
		for anchor in g.anchors:
			if anchor_name == anchor.name:
				g_list.append([g.name, anchor.x, anchor.y])
				break
	return g_list

def Create_mkmk1(accent_g_list, base_g_list, lookupname, acc_class):
	txt = "lookup " + lookupname + " {\n"
	#acc_class = "@MC_mkmk"
	for acc in accent_g_list:
		txt += "  markClass " + acc[0] + " <anchor " + `int(acc[1])` + " " + `int(acc[2])` + "> " + acc_class +";\n"
	
	for base in base_g_list:
		txt += "  pos mark " + base[0] + " <anchor " + `int(base[1])` + " " + `int(base[2])` + "> mark " + acc_class + ";\n"
	
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
  text += Create_mkmk1(accent_mark_list, base_mark_list, "mkmk1", "@MC_mkmk_top")
  
  accent_name_list = []
  accent_mark_list = []
  base_mark_list = []
  anchor_name = "mkmkbottom_acc"
  acc_anchor_name = "_markbottom"
  accent_name_list = CreateAccNameList(font, acc_anchor_name)
  accent_mark_list = CreateAccGlyphList(font, accent_name_list, acc_anchor_name)
  base_mark_list = CreateGlyphList(font, accent_name_list, anchor_name)
  text += Create_mkmk1(accent_mark_list, base_mark_list, "mkmk2", "@MC_mkmk_bottom")

  text += "} mkmk;\n"

  updateFeature(font, "mkmk", text)
