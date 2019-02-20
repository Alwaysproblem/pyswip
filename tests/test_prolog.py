# -*- coding: utf-8 -*-

# Copyright 2007 Yuce Tekol <yucetekol@gmail.com>
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


import unittest

from pyswip.prolog import Prolog, PrologError
from pyswip.term import NIL, atom, atoms, compound, functor, functors


class TestProlog(unittest.TestCase):

    p = Prolog()

    def test_asserta(self):
        result = self.p.assertz("parent(a, b)")
        self.assertEqual(None, result)

    def test_assertz(self):
        result = self.p.assertz("parent(a, b)")
        self.assertEqual(None, result)

    def test_query(self):
        result = list(self.p.query("a=a", normalize=False))[0]
        self.assertEqual(NIL, result)

        result = list(self.p.query("a=b"))
        self.assertEqual([], result)

        self.p.assertz("p(a)")
        r = list(self.p.query("p(X)", normalize=False))[0]
        self.assertEqual({atom("X"): atom("a")}, r.value.value)

        self.p.assertz("numi(42)")
        r = list(self.p.query("numi(N)"))[0]
        self.assertEqual({"N": 42}, r)

        self.p.assertz("numf(42.5)")
        r = list(self.p.query("numf(N)"))[0]
        self.assertEqual({"N": 42.5}, r)

        self.p.assertz("boolx(true)")
        r = list(self.p.query("boolx(B)"))[0]
        self.assertEqual({"B": True}, r)

    def test_query_tuple(self):
        self.p.assertz("tuple2((abc, def))")
        r = list(self.p.query("tuple2(T)", normalize=True))[0]
        self.assertEqual({"T": ("abc", "def")}, r)

        self.p.assertz("tuple3((a, b, c))")
        r = list(self.p.query("tuple3(T)"))[0]
        self.assertEqual({"T": ("a", "b", "c")}, r)

        self.p.assertz("tuple32((a, (b, c)))")
        r = list(self.p.query("tuple32(T)"))[0]
        self.assertEqual({"T": ("a", "b", "c")}, r)

    def test_query_list(self):
        self.p.assertz("list2([a, b])")
        r = list(self.p.query("list2(L)", normalize=False))[0]
        self.assertEqual({"L": ["a", "b"]}, r.norm_value)

        self.p.assertz("list3([a, b, c])")
        r = list(self.p.query("list3(L)"))[0]
        self.assertEqual({"L": ["a", "b", "c"]}, r)

        self.p.assertz("list32([a, [b, c]])")
        r = list(self.p.query("list32(L)"))[0]
        self.assertEqual({"L": ["a", ["b", "c"]]}, r)

    def test_atom(self):
        a1 = atom("atom1")
        a2 = atom("atom2")
        a11 = atom("atom1")
        self.assertEqual(a1, a1)
        self.assertEqual(a1, a11)
        self.assertNotEqual(a1, a2)

    def test_functor(self):
        f1 = functor("=", 2)
        f2 = functor("foo")
        f11 = functor("=", 2)
        self.assertEqual(f1, f1)
        self.assertEqual(f1, f11)
        self.assertNotEqual(f1, f2)

    def test_list_of_functor(self):
        p = self.p
        p.assertz("answer(a,b,[on(a), jump(a,b)])")
        r = next(p.query("answer(a,b,X)"))
        on, jump = functors("on", "jump")
        a, b = atoms("a", "b")
        target = {"X": [on(a), jump(a, b)]}
        self.assertTrue(r == target)
        # self.assertEqual(target, r)

    def test_multiple_answers(self):
        p = self.p
        p.retractall("foo(X)")
        p.assertz("foo(x1)")
        p.assertz("foo(x2)")
        r = list(p.query("foo(X)"))
        self.assertEqual(r, [{"X": "x1"}, {"X": "x2"}])

    def test_nested_queries(self):
        """
        SWI-Prolog cannot have nested queries called by the foreign function
        interface, that is, if we open a query and are getting results from it,
        we cannot open another query before closing that one.

        Since this is a user error, we just ensure that a appropriate error
        message is thrown.
        """
        p = self.p
        
        # Add something to the base
        p.assertz("father(john,mich)")
        p.assertz("father(john,gina)")
        p.assertz("mother(jane,mich)")

        somequery = "father(john, Y)"
        otherquery = "mother(jane, X)"

        # This should not throw an exception
        for _ in p.query(somequery):
            pass
        for _ in p.query(otherquery):
            pass
        
        with self.assertRaises(PrologError):
            for q in p.query(somequery):
                for j in p.query(otherquery):
                    # This should throw an error, another query was opened
                    pass

    def test_prolog_strings(self):
        """
        See: https://github.com/yuce/pyswip/issues/9
        """
        self.p.assertz('some_string_fact("abc")')
        r = list(self.p.query("some_string_fact(S)"))[0]
        self.assertEqual({"S": b"abc"}, r)

    def test_prolog_read_file(self):
        """
        See: https://github.com/yuce/pyswip/issues/10
        """
        self.p.consult("tests/fixtures/test_read.pl")
        list(self.p.query('read_file("tests/fixtures/test_read.pl", S)'))


    def test_functor_return(self):
        """
        pyswip should generate string representations of query results
        that are at least meaningful, preferably equal to what
        SWI-Prolog would generate. This test checks if this is true for
        `Functor` instance results.

        Not a formal issue, but see forum topic:
        https://groups.google.com/forum/#!topic/pyswip/Mpnfq4DH-mI
        """

        p = self.p
        p.consult("tests/fixtures/test_functor_return.pl")

        s, np, d, vp, v, n = functors("s", "np", "d", "vp", "v", "n")
        the, bat, eats, a, cat = atoms("the", "bat", "eats", "a", "cat")
        target = s(np(d(the), n(bat)), vp(v(eats), np(d(a), n(cat))))

        query = "sentence(Parse_tree, [the,bat,eats,a,cat], [])"
        # This should not throw an exception
        results = list(p.query(query))
        self.assertEqual(len(results), 1,
                         "Query should return exactly one result")
        ptree = results[0]["Parse_tree"]
        self.assertEqual(ptree, target)

        # A second test, based on what was posted in the forum
        p.assertz("friend(john,son(miki))")
        p.assertz("friend(john,son(kiwi))")
        p.assertz("friend(john,son(wiki))")
        p.assertz("friend(john,son(tiwi))")
        p.assertz("father(son(miki),kur)")
        p.assertz("father(son(kiwi),kur)")
        p.assertz("father(son(wiki),kur)")

        son = functor("son")
        miki = atom("miki")

        soln = [s["Y"] for s in p.query("friend(john,Y), father(Y,kur)",
                                        maxresult=1)]
        self.assertEqual(soln[0], son(miki))

    def test_register_foreign(self):
        """
        Callbacks can cause segv's

        https://code.google.com/p/pyswip/issues/detail?id=8
        """

        @Prolog.register
        def hello(t):
            calls_to_hello.append(t)

        calls_to_hello = []
        p = self.p
        p.assertz("parent(michael,john)")
        p.assertz("parent(michael,gina)")
        result = list(p.query("parent(michael,X), hello(X)"))
        self.assertEqual(len(calls_to_hello), 2)  # ['john', 'gina']
        self.assertEqual(len(result), 2)  # [{'X': 'john'}, {'X': 'gina'}]

    def test_errors(self):
        p = self.p
        p.assertz("foo(bar)")
        try:
            list(p.query("zzz(X)"))
        except PrologError as ex:
            self.assertEqual(ex.msg, "Does not exist: procedure /(zzz, 1)")
            return
        self.fail("PrologError was not raised")

