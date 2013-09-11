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

__all__ = ("CaseSet",)


import re


class CaseSet:

   def __init__(self, CaseBasename, Cases, CaseCategories, CaseSubCategories):
      self.CaseBasename = CaseBasename
      self.Cases = Cases
      self.CaseCategories = CaseCategories
      self.CaseSubCategories = CaseSubCategories

      ## Index:
      ## "1.2.3" => Index (1-based) of Case1_2_3 in Cases
      ##
      self.CasesIndices = {}
      i = 1
      for c in self.Cases:
         self.CasesIndices[self.caseClasstoId(c)] = i
         i += 1

      ## Index:
      ## "1.2.3" => Case1_2_3
      ##
      self.CasesById = {}
      for c in self.Cases:
         self.CasesById[self.caseClasstoId(c)] = c


   def caseClasstoId(self, klass):
      """
      Class1_2_3 => '1.2.3'
      """
      l = len(self.CaseBasename)
      return '.'.join(klass.__name__[l:].split("_"))


   def caseClasstoIdTuple(self, klass):
      """
      Class1_2_3 => (1, 2, 3)
      """
      l = len(self.CaseBasename)
      return tuple([int(x) for x in klass.__name__[l:].split("_")])


   def caseIdtoIdTuple(self, id):
      """
      '1.2.3' => (1, 2, 3)
      """
      return tuple([int(x) for x in id.split('.')])


   def caseIdTupletoId(self, idt):
      """
      (1, 2, 3) => '1.2.3'
      """
      return '.'.join([str(x) for x in list(idt)])


   def caseClassToPrettyDescription(self, klass):
      """
      Truncates the rest of the description after the first HTML tag
      and coalesces whitespace
      """
      return ' '.join(klass.DESCRIPTION.split('<')[0].split())


   def resolveCasePatternList(self, patterns):
      """
      Return list of test cases that match against a list of case patterns.
      """
      specCases = []
      for c in patterns:
         if c.find('*') >= 0:
            s = c.replace('.', '\.').replace('*', '.*')
            p = re.compile(s)
            t = []
            for x in self.CasesIndices.keys():
               if p.match(x):
                  t.append(self.caseIdtoIdTuple(x))
            for h in sorted(t):
               specCases.append(self.caseIdTupletoId(h))
         else:
            specCases.append(c)
      return specCases


   def parseSpecCases(self, spec):
      """
      Return list of test cases that match against case patterns, minus exclude patterns.
      """
      specCases = self.resolveCasePatternList(spec["cases"])
      if spec.has_key("exclude-cases"):
         excludeCases = self.resolveCasePatternList(spec["exclude-cases"])
      else:
         excludeCases = []
      c = list(set(specCases) - set(excludeCases))
      cases = [self.caseIdTupletoId(y) for y in sorted([self.caseIdtoIdTuple(x) for x in c])]
      return cases


   def parseExcludeAgentCases(self, spec):
      """
      Parses "exclude-agent-cases" from the spec into a list of pairs
      of agent pattern and case pattern list.
      """
      if spec.has_key("exclude-agent-cases"):
         ee = spec["exclude-agent-cases"]
         pats1 = []
         for e in ee:
            s1 = "^" + e.replace('.', '\.').replace('*', '.*') + "$"
            p1 = re.compile(s1)
            pats2 = []
            for z in ee[e]:
               s2 = "^" + z.replace('.', '\.').replace('*', '.*') + "$"
               p2 = re.compile(s2)
               pats2.append(p2)
            pats1.append((p1, pats2))
         return pats1
      else:
         return []


   def checkAgentCaseExclude(self, patterns, agent, case):
      """
      Check if we should exclude a specific case for given agent.
      """
      for p in patterns:
         if p[0].match(agent):
            for pp in p[1]:
               if pp.match(case):
                  return True
      return False


   def getCasesByAgent(self, spec):
      caseIds = self.parseSpecCases(spec)
      epats = self.parseExcludeAgentCases(spec)
      res = []
      for server in spec['servers']:
         agent = server['agent']
         res2 = []
         for caseId in caseIds:
            if not self.checkAgentCaseExclude(epats, agent, caseId):
               res2.append(self.CasesById[caseId])
         if len(res2) > 0:
            o = {}
            o['agent'] = str(server['agent'])
            o['url'] = str(server['url'])
            o['auth'] = server.get('auth', None)
            o['cases'] = res2
            res.append(o)
      return res
