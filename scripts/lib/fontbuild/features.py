import string

def CreateFeaFile(font, path):
	fea_text = font.ot_classes
	for cls in font.classes:
		text = "@" + cls + "];\n"
		text = string.replace(text, ":", "= [")
		text = string.replace(text, "\'", "")
		fea_text += text	
	for fea in font.features:
		fea_text += fea.value
	fea_text = string.replace(fea_text, "\r\n", "\n")	
	fout = open(path, "w")
	fout.write(fea_text)
	fout.close()