
all: sans slab mono

sans:
	echo "BASEDIR=\"$(CURDIR)\"" > /tmp/makefonts.flw
	cat "scripts/build.py" >> /tmp/makefonts.flw
	open -nWa "$(FONTLAB)" /tmp/makefonts.flw

v2:
	echo "BASEDIR=\"$(CURDIR)\"" > /tmp/makefontsB.py
	cat "scripts/build-v2.py" >> /tmp/makefontsB.py
	python /tmp/makefontsB.py

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

crunch:
	mkdir -p out/crunched
	cd third_party/fontcrunch && \
	for source in ../../out/RobotoTTF/*.ttf ../../out/RobotoCondensedTTF/*.ttf; do \
		python fontcrunch.py gen $$source; \
	done && \
	$(MAKE) -j8 && \
	for source in ../../out/RobotoTTF/*.ttf ../../out/RobotoCondensedTTF/*.ttf; do \
		python fontcrunch.py pack $$source ../../out/crunched/$$(basename $$source) >/dev/null; \
	done

android:
	mkdir -p out/android
	for source in out/crunched/*.ttf; do \
		touched=$$(mktemp); \
		subsetted=$$(mktemp); \
		final=out/android/$$(basename $$source); \
		python scripts/touchup_for_android.py $$source $$touched && \
		python $$HOME/noto/nototools/subset.py $$touched $$subsetted && \
		python scripts/force_yminmax.py $$subsetted $$final && \
		rm $$touched $$subsetted; \
	done

glass: out/android/Roboto-Thin.ttf
	mkdir -p out/glass
	python scripts/touchup_for_glass.py $< out/glass/Roboto-Thin.ttf

web:
	mkdir -p out/web
	for source in hinted/*.ttf; do \
		touched=$$(mktemp); \
		final=out/web/$$(basename $$source); \
		python scripts/touchup_for_web.py $$source $$touched Roboto && \
		python scripts/subset_for_web.py $$touched $$final && \
		rm $$touched; \
	done

chromeos:
	mkdir -p out/chromeos
	for source in hinted/*.ttf; do \
		touched=$$(mktemp); \
		final=out/chromeos/$$(basename $$source); \
		python scripts/touchup_for_web.py $$source $$touched Roboto && \
		python $$HOME/noto/nototools/subset.py $$touched $$final && \
		rm $$touched; \
	done

test: test-android test-coverage test-general

test-general:
	python scripts/run_general_tests.py

test-exhaustive:
	python scripts/run_exhaustive_tests.py

test-android:
	python scripts/run_android_tests.py

test-web:
	python scripts/run_web_tests.py

test-coverage:
	python scripts/coverage_test.py
