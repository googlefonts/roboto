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

all: v2

v2:
	PYTHONPATH=$(PYTHONPATH):$(CURDIR)/scripts/lib python scripts/build-v2.py

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

# TODO: remove this build target once we are comfortable with the quality of
# the new toolchain
android-from-hinted:
	mkdir -p out/android
	for source in src/hinted/*.ttf; do \
	        unhinted=$$(mktemp); \
		touched=$$(mktemp); \
		subsetted=$$(mktemp); \
		final=out/android/$$(basename $$source); \
		python $$HOME/noto/nototools/drop_hints.py $$source $$unhinted && \
		python scripts/touchup_for_android.py $$unhinted $$touched && \
		python $$HOME/noto/nototools/subset.py $$touched $$subsetted && \
		python scripts/force_yminmax.py $$subsetted $$final && \
		rm $$touched $$subsetted; \
	done

web:
	mkdir -p out/web
	for source in src/hinted/*.ttf; do \
		basename=$$(basename $$source); \
		case $$source in \
			src/hinted/Roboto-*) unhinted=out/RobotoTTF/$$basename ;; \
			*) unhinted=out/RobotoCondensedTTF/$$basename ;; \
		esac; \
		touched=$$(mktemp); \
		final=out/web/$$(basename $$source); \
		python scripts/touchup_for_web.py $$source $$unhinted $$touched Roboto && \
		python scripts/subset_for_web.py $$touched $$final && \
		rm $$touched; \
	done

chromeos:
	mkdir -p out/chromeos
	for source in src/hinted/*.ttf; do \
		basename=$$(basename $$source); \
		case $$source in \
			src/hinted/Roboto-*) unhinted=out/RobotoTTF/$$basename ;; \
			*) unhinted=out/RobotoCondensedTTF/$$basename ;; \
		esac; \
		touched=$$(mktemp); \
		final=out/chromeos/$$(basename $$source); \
		python scripts/touchup_for_cros.py $$source $$unhinted $$touched Roboto && \
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
