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


from datetime import date
import re
from random import randint
import string

class InstanceNames:
    "Class that allows easy setting of FontLab name fields. TODO: Add proper italic flags"
    
    foundry = ""
    build = "0000"
    version = "1.0"
    year = date.today().year
    designer = "Christian Robertson"
    license = "Licensed under the Apache License, Version 2.0"
    licenseURL = "http://www.apache.org/licenses/LICENSE-2.0"
    
    def __init__(self,names):
        if type(names) == type(" "):
            names = names.split("/")
        #print names            
        self.longfamily =      names[0]
        self.longstyle =       names[1]
        self.shortstyle =      names[2]
        self.subfamilyAbbrev = names[3]

        self.width =           self._getWidth()
        self.italic =          self._getItalic()
        self.weight =          self._getWeight()
        self.fullname =        "%s %s" %(self.longfamily, self.longstyle)
        self.postscript =      re.sub(' ','', self.longfamily) + "-" + re.sub(' ','',self.longstyle)
        
        if self.subfamilyAbbrev != "" and self.subfamilyAbbrev != None and self.subfamilyAbbrev != "Rg":
            self.shortfamily = "%s %s" %(self.longfamily, self.longstyle.split()[0])
        else:
            self.shortfamily = self.longfamily
    
    def setRFNames(self,f, version=1, versionMinor=0):
        f.info.familyName = self.longfamily
        f.info.styleName = self.longstyle
        f.info.styleMapFamilyName = self.shortfamily
        f.info.styleMapStyleName = self.shortstyle.lower()
        f.info.versionMajor = version
        f.info.versionMinor = versionMinor
        f.info.year = self.year
        #f.info.copyright = "Font data copyright %s %s" %(self.foundry, self.year)
        f.info.trademark = "%s is a trademark of %s." %(self.longfamily, self.foundry)
        
        f.info.openTypeNameDesigner = "Christian Robertson"
        f.info.openTypeNameDesignerURL = self.foundry + ".com"
        f.info.openTypeNameManufacturer = self.foundry
        f.info.openTypeNameManufacturerURL = self.foundry + ".com"
        f.info.openTypeNameLicense = self.license
        f.info.openTypeNameLicenseURL = self.licenseURL
        f.info.openTypeNameVersion = "Version %i.%i" %(version,versionMinor)
        f.info.openTypeNameUniqueID = "%s:%s:%s" %(self.foundry, self.fullname, self.year)
        # f.info.openTypeNameDescription = ""        
        # f.info.openTypeNameCompatibleFullName = "" 
        # f.info.openTypeNameSampleText = ""
        if (self.subfamilyAbbrev != "Rg"):
            f.info.openTypeNamePreferredFamilyName = self.longfamily 
            f.info.openTypeNamePreferredSubfamilyName = self.longstyle 
        
        f.info.openTypeOS2WeightClass = self._getWeightCode(self.weight)
        f.info.macintoshFONDName = re.sub(' ','',self.longfamily) + " " + re.sub(' ','',self.longstyle)
        f.info.postscriptFontName = f.info.macintoshFONDName.replace(" ", "-")
        if self.italic:
            f.info.italicAngle = -12.0
        
    
    def setFLNames(self,flFont):
        
        from FL import NameRecord
        
        flFont.family_name =      self.shortfamily
        flFont.mac_compatible =   self.fullname 
        flFont.style_name =       self.longstyle 
        flFont.full_name =        self.fullname 
        flFont.font_name =        self.postscript 
        flFont.font_style =       self._getStyleCode()
        flFont.menu_name =        self.shortfamily 
        flFont.apple_name =       re.sub(' ','',self.longfamily) + " " + re.sub(' ','',self.longstyle) 
        flFont.fond_id =          randint(1000,9999) 
        flFont.pref_family_name = self.longfamily 
        flFont.pref_style_name =  self.longstyle 
        flFont.weight =           self.weight 
        flFont.weight_code =      self._getWeightCode(self.weight) 
        flFont.width =            self.width
        if len(self.italic):
            flFont.italic_angle = -12

        fn = flFont.fontnames
        fn.clean()
        #fn.append(NameRecord(0,1,0,0,     "Font data copyright %s %s" %(self.foundry, self.year) ))
        #fn.append(NameRecord(0,3,1,1033,  "Font data copyright %s %s" %(self.foundry, self.year) ))
        fn.append(NameRecord(0,1,0,0,     "Copyright %s %s Inc. All Rights Reserved." %(self.year, self.foundry) ))
        fn.append(NameRecord(0,3,1,1033,  "Copyright %s %s Inc. All Rights Reserved." %(self.year, self.foundry) ))
        fn.append(NameRecord(1,1,0,0,     self.longfamily ))
        fn.append(NameRecord(1,3,1,1033,  self.shortfamily ))
        fn.append(NameRecord(2,1,0,0,     self.longstyle ))
        fn.append(NameRecord(2,3,1,1033,  self.longstyle ))
        #fn.append(NameRecord(3,1,0,0,     "%s:%s:%s" %(self.foundry, self.longfamily, self.year) ))
        #fn.append(NameRecord(3,3,1,1033,  "%s:%s:%s" %(self.foundry, self.longfamily, self.year) ))
        fn.append(NameRecord(3,1,0,0,     "%s:%s:%s" %(self.foundry, self.fullname, self.year) ))
        fn.append(NameRecord(3,3,1,1033,  "%s:%s:%s" %(self.foundry, self.fullname, self.year) ))        
        fn.append(NameRecord(4,1,0,0,     self.fullname ))
        fn.append(NameRecord(4,3,1,1033,  self.fullname ))
        #fn.append(NameRecord(5,1,0,0,     "Version %s%s; %s" %(self.version, self.build, self.year) ))
        #fn.append(NameRecord(5,3,1,1033,  "Version %s%s; %s" %(self.version, self.build, self.year) ))
        fn.append(NameRecord(5,1,0,0,     "Version %s; %s" %(self.version, self.year) ))
        fn.append(NameRecord(5,3,1,1033,  "Version %s; %s" %(self.version, self.year) ))
        fn.append(NameRecord(6,1,0,0,     self.postscript ))
        fn.append(NameRecord(6,3,1,1033,  self.postscript ))
        fn.append(NameRecord(7,1,0,0,     "%s is a trademark of %s." %(self.longfamily, self.foundry) ))
        fn.append(NameRecord(7,3,1,1033,  "%s is a trademark of %s." %(self.longfamily, self.foundry) ))
        fn.append(NameRecord(9,1,0,0,     self.foundry ))
        fn.append(NameRecord(9,3,1,1033,  self.foundry ))
        fn.append(NameRecord(11,1,0,0,    self.foundry + ".com" ))
        fn.append(NameRecord(11,3,1,1033, self.foundry + ".com" ))
        fn.append(NameRecord(12,1,0,0,    self.designer ))
        fn.append(NameRecord(12,3,1,1033, self.designer ))
        fn.append(NameRecord(13,1,0,0,    self.license ))
        fn.append(NameRecord(13,3,1,1033, self.license ))
        fn.append(NameRecord(14,1,0,0,    self.licenseURL ))
        fn.append(NameRecord(14,3,1,1033, self.licenseURL ))
        if (self.subfamilyAbbrev != "Rg"):
            fn.append(NameRecord(16,3,1,1033, self.longfamily ))
            fn.append(NameRecord(17,3,1,1033, self.longstyle))
        #else:
            #fn.append(NameRecord(17,3,1,1033,""))
        #fn.append(NameRecord(18,1,0,0, re.sub("Italic","It", self.fullname)))
    
    def _getSubstyle(self, regex):
        substyle = re.findall(regex, self.longstyle)
        if len(substyle) > 0:
            return substyle[0]
        else:
            return ""

    def _getItalic(self):
        return self._getSubstyle(r"Italic|Oblique|Obliq")

    def _getWeight(self):
        w = self._getSubstyle(r"Extrabold|Superbold|Super|Fat|Black|Bold|Semibold|Demibold|Medium|Light|Thin")
        if w == "":
            w = "Regular"
        return w

    def _getWidth(self):
        w = self._getSubstyle(r"Condensed|Extended|Narrow|Wide")
        if w == "":
            w = "Normal"
        return w
    
    def _getStyleCode(self):
        #print "shortstyle:", self.shortstyle
        styleCode = 0
        if self.shortstyle == "Bold":
            styleCode = 32
        if self.shortstyle == "Italic":
            styleCode = 1
        if self.shortstyle == "Bold Italic":
            styleCode = 33
        if self.longstyle  == "Regular":
            styleCode = 64
        return styleCode
        
    def _getWeightCode(self,weight):
        if weight == "Thin":
            return 250
        elif weight == "Light":
            return 300    
        elif weight == "Bold":
            return 700
        elif weight == "Medium":
            return 500
        elif weight == "Semibold":
            return 600
        elif weight == "Black":
            return 900
        elif weight == "Fat":
            return 900

        return 400
        
def setNames(f,names,foundry="",version="1.0",build="0000"):
    InstanceNames.foundry = foundry
    InstanceNames.version = version
    InstanceNames.build = build
    i = InstanceNames(names)
    i.setFLNames(f)


def setNamesRF(f, names, foundry="", version="1.0"):
    InstanceNames.foundry = foundry
    i = InstanceNames(names)
    version, versionMinor = [int(num) for num in version.split(".")]
    i.setRFNames(f, version=version, versionMinor=versionMinor)
