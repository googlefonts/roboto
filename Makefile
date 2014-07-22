
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
	mkdir -p out/android
	for source in out/RobotoTTF/*.ttf out/RobotoCondensedTTF/*.ttf; do \
	        touched=$$(mktemp); \
	        subsetted=$$(mktemp); \
		final=out/android/$$(basename $$source); \
		python scripts/touchup_for_android.py $$source $$touched; \
		python $$HOME/noto/nototools/subset.py $$touched $$subsetted; \
		python scripts/force_yminmax.py $$subsetted $$final; \
		rm $$touched $$subsetted; \
	done

glass: out/android/Roboto-Thin.ttf
	mkdir -p out/glass
	python scripts/touchup_for_glass.py $< out/glass/Roboto-Thin.ttf
