import unittest
from typing import Dict
import javalang
from punito.processing import parse_java_class, get_all_methods, get_function_with_individual_dependencies


class TestGetFunctionWithIndividualDependencies(unittest.TestCase):

    def test_no_dependencies(self):
        # Target method has no method calls → empty dependency blocks.
        java_code = """
        public class TestClass {
            public void target() {
                // no method calls
            }
        }
        """
        tree = parse_java_class(java_code)
        methods: Dict[str, javalang.tree.MethodDeclaration] = get_all_methods(tree)
        result = get_function_with_individual_dependencies(java_code, "target", methods)
        self.assertEqual(result, {}, "Expected empty dict when target has no calls.")

    def test_multiple_dependencies(self):
        # target() calls foo() and bar().
        # foo() calls baz(), bar() does nothing.
        java_code = """
        import java.util.*;
        public class TestClass {
            public void target() {
                foo();
                bar();
            }
            public void foo() {
                baz();
            }
            public void bar() {
                // does nothing
            }
            public void baz() {
                // does nothing
            }
        }
        """
        tree = parse_java_class(java_code)
        methods: Dict[str, javalang.tree.MethodDeclaration] = get_all_methods(tree)
        result = get_function_with_individual_dependencies(java_code, "target", methods)
        # Expected keys: "foo" and "bar"
        self.assertEqual(set(result.keys()), {"foo", "bar"})
        # Each block should include the target method code.
        for block in result.values():
            self.assertIn("public void target()", block)
        # For "foo", expect its own code and that of baz()
        self.assertIn("public void foo()", result["foo"])
        self.assertIn("public void baz()", result["foo"])
        # For "bar", expect its own code.
        self.assertIn("public void bar()", result["bar"])

    def test_circular_dependencies(self):
        # Circular dependency: target() calls foo(), foo() calls bar(), bar() calls foo()
        java_code = """
        public class TestClass {
            public void target() {
                foo();
            }
            public void foo() {
                bar();
            }
            public void bar() {
                foo();
            }
        }
        """
        tree = parse_java_class(java_code)
        methods: Dict[str, javalang.tree.MethodDeclaration] = get_all_methods(tree)
        result = get_function_with_individual_dependencies(java_code, "target", methods)
        # Only dependency is "foo", whose recursive dependencies include "bar"
        self.assertEqual(set(result.keys()), {"foo"})
        block = result["foo"]
        self.assertIn("public void foo()", block)
        self.assertIn("public void bar()", block)
        # Ensure target method is present
        self.assertIn("public void target()", block)

    def test_non_existent_dependency(self):
        # target() calls a method missing in the class.
        java_code = """
        public class TestClass {
            public void target() {
                missingMethod();
            }
            public void someOther() {
                // irrelevant method
            }
        }
        """
        tree = parse_java_class(java_code)
        methods: Dict[str, javalang.tree.MethodDeclaration] = get_all_methods(tree)
        result = get_function_with_individual_dependencies(java_code, "target", methods)
        # Although missingMethod() isn't defined, its key should be present.
        self.assertEqual(set(result.keys()), {"missingMethod"})
        # Since get_dependencies never finds missingMethod, only target() is included.
        block = result["missingMethod"]
        self.assertIn("public void target()", block)
        # There should be no method block for missingMethod.
        self.assertNotIn("public void missingMethod()", block)


    def test_nested_dependencies(self):
        # target() calls a() and b(), with deeper nested calls.
        java_code = """
        import java.util.*;
        public class TestClass {
            public void target() {
                a();
                b();
            }
            public void a() {
                c();
                d();
            }
            public void b() {
                i();
                j();
            }
            public void c() {
                e();
                f();
            }
            public void d() {
                // no nested call
            }
            public void e() {
                g();
            }
            public void f() {
                h();
            }
            public void g() {
                // leaf
            }
            public void h() {
                // leaf
            }
            public void i() {
                k();
            }
            public void j() {
                l();
                m();
            }
            public void k() {
                // leaf
            }
            public void l() {
                n();
            }
            public void m() {
                o();
            }
            public void n() {
                p();
            }
            public void o() {
                q();
            }
            public void p() {
                // leaf
            }
            public void q() {
                // leaf
            }
        }
        """
        tree = parse_java_class(java_code)
        methods = get_all_methods(tree)

        result = get_function_with_individual_dependencies(java_code, "target", methods, set())

        # Direct dependencies from target(): "a" and "b"
        self.assertEqual(set(result.keys()), {"a", "b"})

        # Dependency block for "a" should include: target, a, c, d, e, f, g, h
        a_block = result["a"]
        self.assertIn("public void target()", a_block)
        self.assertIn("public void a()", a_block)
        self.assertIn("public void c()", a_block)
        self.assertIn("public void d()", a_block)
        self.assertIn("public void e()", a_block)
        self.assertIn("public void f()", a_block)
        self.assertIn("public void g()", a_block)
        self.assertIn("public void h()", a_block)

        # Dependency block for "b" should include: target, b, i, j, k, l, m, n, o, p, q
        b_block = result["b"]
        self.assertIn("public void target()", b_block)
        self.assertIn("public void b()", b_block)
        self.assertIn("public void i()", b_block)
        self.assertIn("public void j()", b_block)
        self.assertIn("public void k()", b_block)
        self.assertIn("public void l()", b_block)
        self.assertIn("public void m()", b_block)
        self.assertIn("public void n()", b_block)
        self.assertIn("public void o()", b_block)
        self.assertIn("public void p()", b_block)
        self.assertIn("public void q()", b_block)

    def test_skip_missing_dependencies(self):
        # target() calls presentMethod() (defined) and missingMethod() (undefined).
        java_code = """
        public class TestClass {
            public void target() {
                presentMethod();
                missingMethod();
            }
            public void presentMethod() {
                String year = "2022";
            }
        }
        """
        tree = parse_java_class(java_code)
        methods = get_all_methods(tree)
        result = get_function_with_individual_dependencies(java_code, "target", methods)

        # Only presentMethod should be included since missingMethod has no code.
        self.assertEqual(set(result.keys()), {"presentMethod"})
        block = result["presentMethod"]
        self.assertIn("public void target()", block)
        self.assertIn("public void presentMethod()", block)
        self.assertNotIn("void missingMethod()", block)

if __name__ == '__main__':
    unittest.main()
