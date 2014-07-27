# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Contributor: Raph Levien

SRC = $(wildcard */*.bez)
OPT = $(patsubst %.bez, %.bezopt, $(SRC))

dummy: $(OPT)

quadopt: quadopt.cc
	$(CXX) $< -std=c++0x -O3 -o $@

%.bezopt:	%.bez quadopt
	./quadopt $< $@

clean:
	rm -f quadopt
	find . -name '*.bez' -delete
	find . -name '*.bezopt' -delete
	rmdir ??