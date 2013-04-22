###############################################################################
##
##  Copyright 2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

__all__ = ["Cases",
           "caseClasstoId",
           "caseClasstoIdTuple",
           "caseIdtoIdTuple",
           "caseIdTupletoId",
           "CasesIndices",
           "CasesById",
           ]

WampCaseCategories = {"1": "Publish and Subscribe",
                      "2": "Remote Procedure Calls"}
WampCaseSubCategories = {"1.1"}


from wampcase1 import *

## all WAMP test cases
##
Cases = []
Cases.extend(WampCase1_x_x)



## WampCase1_2_3 => '1.2.3'
##
def caseClasstoId(klass):
   return '.'.join(klass.__name__[8:].split("_"))

## WampCase1_2_3 => (1, 2, 3)
##
def caseClasstoIdTuple(klass):
   return tuple([int(x) for x in klass.__name__[8:].split("_")])

## '1.2.3' => (1, 2, 3)
##
def caseIdtoIdTuple(id):
   return tuple([int(x) for x in id.split('.')])

## (1, 2, 3) => '1.2.3'
##
def caseIdTupletoId(idt):
   return '.'.join([str(x) for x in list(idt)])

## Index:
## "1.2.3" => Index (1-based) of WampCase1_2_3 in WampCases
##
CasesIndices = {}
i = 1
for c in Cases:
   CasesIndices[caseClasstoId(c)] = i
   i += 1

## Index:
## "1.2.3" => Case1_2_3
##
CasesById = {}
for c in Cases:
   CasesById[caseClasstoId(c)] = c
