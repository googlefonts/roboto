
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

android:
	rm -rf out/android/temp
	mkdir --parents out/android/temp
	for f in out/RobotoTTF/*.ttf out/RobotoCondensedTTF/*.ttf; do \
		temp_location=out/android/temp/$$(basename $$f); \
		final_location=out/android/$$(basename $$f); \
		python scripts/touchup_for_android.py $$f $$temp_location; \
		python $$HOME/noto/nototools/subset.py $$temp_location $$final_location; \
	done
