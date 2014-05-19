
all: sans slab mono

sans:
	echo "BASEDIR=\"$(CURDIR)\"" > /tmp/makefonts.flw
	cat "scripts/build.py" >> /tmp/makefonts.flw
	open -nWa "$(FONTLAB)" /tmp/makefonts.flw

v2:
	echo "BASEDIR=\"$(CURDIR)\"" > /tmp/makefontsB.flw
	cat "scripts/build-v2.py" >> /tmp/makefontsB.flw
	open -nWa "$(FONTLAB)" /tmp/makefontsB.flw


slab:
	echo "BASEDIR=\"$(CURDIR)\"" > /tmp/makefonts.flw
	cat "scripts/build-slab.py" >> /tmp/makefonts.flw
	open -nWa "$(FONTLAB)" /tmp/makefonts.flw

slabitalic:
	echo "BASEDIR=\"$(CURDIR)\"" > /tmp/makefonts.flw
	cat "scripts/build-slabitalic.py" >> /tmp/makefonts.flw
	open -nWa "$(FONTLAB)" /tmp/makefonts.flw

mono:
	echo "BASEDIR=\"$(CURDIR)\"" > /tmp/makefonts.flw
	cat "scripts/build-monoV2.py" >> /tmp/makefonts.flw
	open -nWa "$(FONTLAB)" /tmp/makefonts.flw
