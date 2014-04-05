#!/usr/bin/python
# -*- coding:Utf-8 -*-


import baron
from redbaron import (RedBaron, NameNode, EndlNode, IntNode, AssignmentNode,
                      PassNode, NodeList)


def test_empty():
    RedBaron("")


def test_is_list():
    assert [] == list(RedBaron(""))


def test_name():
    red = RedBaron("a\n")
    assert len(red) == 2
    assert isinstance(red[0], NameNode)
    assert isinstance(red[1], EndlNode)
    assert red[0].value == "a"


def test_int():
    red = RedBaron("1\n")
    assert isinstance(red[0], IntNode)
    assert red[0].value == 1


def test_assign():
    red = RedBaron("a = 2")
    assert isinstance(red[0], AssignmentNode)
    assert isinstance(red[0].value, IntNode)
    assert red[0].value.value == 2
    assert isinstance(red[0].target, NameNode)
    assert red[0].target.value == "a"


def test_binary_operator():
    red = RedBaron("z +  42")
    assert red[0].value == "+"
    assert isinstance(red[0].first, NameNode)
    assert red[0].first.value == "z"
    assert isinstance(red[0].second, IntNode)
    assert red[0].second.value == 42

    red = RedBaron("z  -      42")
    assert red[0].value == "-"
    assert isinstance(red[0].first, NameNode)
    assert red[0].first.value == "z"
    assert isinstance(red[0].second, IntNode)
    assert red[0].second.value == 42


def test_pass():
    red = RedBaron("pass")
    assert isinstance(red[0], PassNode)


def test_copy():
    red = RedBaron("a")
    name = red[0]
    assert name.value == name.copy().value
    assert name is not name.copy()


def test_dumps():
    some_code = "ax + (z * 4)"
    red = RedBaron(some_code)
    assert some_code == red.dumps()


def test_fst():
    some_code = "ax + (z * 4)"
    red = RedBaron(some_code)
    assert baron.parse(some_code) == red.fst()


def test_get_helpers():
    red = RedBaron("a")
    assert red[0]._get_helpers() == []
    red = RedBaron("import a")
    assert red[0]._get_helpers() == ['modules', 'names']


def test_help_is_not_crashing():
    some_code = "ax + (z * 4)"
    red = RedBaron(some_code)
    red.help()
    red[0].help()


def test_assign_on_string_value():
    some_code = "ax + (z * 4)"
    red = RedBaron(some_code)
    binop = red[0]
    assert binop.first.value == "ax"
    binop.first.value = "pouet"
    assert binop.first.value == "pouet"


def test_assign_on_object_value():
    some_code = "ax + (z * 4)"
    red = RedBaron(some_code)
    binop = red[0]
    assert binop.first.value == "ax"
    binop.first = "pouet"  # will be parsed as a name
    assert binop.first.value == "pouet"
    assert binop.first.type == "name"
    binop.first = "42"  # will be parsed as a int
    assert binop.first.value == 42
    assert binop.first.type == "int"


def test_assign_on_object_value_fst():
    some_code = "ax + (z * 4)"
    red = RedBaron(some_code)
    binop = red[0]
    binop.first = {"type": "name", "value": "pouet"}
    assert binop.first.value == "pouet"
    assert binop.first.type == "name"


def test_assign_node_list():
    red = RedBaron("[1, 2, 3]")
    l = red[0]
    l.value = "pouet"
    assert l.value[0].value == "pouet"
    assert l.value[0].type == "name"
    assert isinstance(l.value, NodeList)
    l.value = ["pouet"]
    assert l.value[0].value == "pouet"
    assert l.value[0].type == "name"
    assert isinstance(l.value, NodeList)


def test_assign_node_list_fst():
    red = RedBaron("[1, 2, 3]")
    l = red[0]
    l.value = {"type": "name", "value": "pouet"}
    assert l.value[0].value == "pouet"
    assert l.value[0].type == "name"
    assert isinstance(l.value, NodeList)
    l.value = [{"type": "name", "value": "pouet"}]
    assert l.value[0].value == "pouet"
    assert l.value[0].type == "name"
    assert isinstance(l.value, NodeList)


def test_assign_node_list_mixed():
    red = RedBaron("[1, 2, 3]")
    l = red[0]
    l.value = ["plop", {"type": "comma", "first_formatting": [], "second_formatting": []}, {"type": "name", "value": "pouet"}]
    assert l.value[0].value == "plop"
    assert l.value[0].type == "name"
    assert l.value[1].type == "comma"
    assert l.value[2].value == "pouet"
    assert l.value[2].type == "name"
    assert isinstance(l.value, NodeList)


def test_parent():
    red = RedBaron("a = 1 + caramba")
    assert red.parent is None
    assert red[0].parent is red
    assert red[0].on_attribute == "root"
    assert red[0].target.parent is red[0]
    assert red[0].target.on_attribute == "target"
    assert red[0].value.parent is red[0]
    assert red[0].value.on_attribute == "value"
    assert red[0].value.first.parent is red[0].value
    assert red[0].value.first.on_attribute == "first"
    assert red[0].value.second.parent is red[0].value
    assert red[0].value.second.on_attribute == "second"

    red = RedBaron("[1, 2, 3]")
    assert red.parent is None
    assert red[0].parent is red
    assert map(lambda x: x.parent, red[0].value) == [red[0]]*5
    assert map(lambda x: x.on_attribute, red[0].value) == ["value"]*5


def test_parent_copy():
    red = RedBaron("a = 1 + caramba")
    assert red[0].value.copy().parent is None


def test_parent_assign():
    red = RedBaron("a = 1 + caramba")
    assert red[0].target.parent is red[0]
    red[0].target = "plop"
    assert red[0].target.parent is red[0]
    assert red[0].target.on_attribute == "target"
    red[0].target = {"type": "name", "value": "pouet"}
    assert red[0].target.parent is red[0]
    assert red[0].target.on_attribute == "target"
    red[0].target = NameNode({"type": "name", "value": "pouet"})
    assert red[0].target.parent is red[0]
    assert red[0].target.on_attribute == "target"

    red = RedBaron("[1, 2, 3]")
    assert map(lambda x: x.parent, red[0].value) == [red[0]]*5
    assert map(lambda x: x.on_attribute, red[0].value) == ["value"]*5
    red[0].value = "pouet"
    assert map(lambda x: x.parent, red[0].value) == [red[0]]
    assert map(lambda x: x.on_attribute, red[0].value) == ["value"]
    red[0].value = ["pouet"]
    assert map(lambda x: x.parent, red[0].value) == [red[0]]
    assert map(lambda x: x.on_attribute, red[0].value) == ["value"]
    red[0].value = {"type": "name", "value": "plop"}
    assert map(lambda x: x.parent, red[0].value) == [red[0]]
    assert map(lambda x: x.on_attribute, red[0].value) == ["value"]
    red[0].value = [{"type": "name", "value": "plop"}]
    assert map(lambda x: x.parent, red[0].value) == [red[0]]
    assert map(lambda x: x.on_attribute, red[0].value) == ["value"]
    red[0].value = NameNode({"type": "name", "value": "pouet"})
    assert map(lambda x: x.parent, red[0].value) == [red[0]]
    assert map(lambda x: x.on_attribute, red[0].value) == ["value"]
    red[0].value = [NameNode({"type": "name", "value": "pouet"})]
    assert map(lambda x: x.parent, red[0].value) == [red[0]]
    assert map(lambda x: x.on_attribute, red[0].value) == ["value"]


def test_node_next():
    red = RedBaron("[1, 2, 3]")
    assert red.next is None
    assert red[0].next is None
    inner = red[0].value
    assert inner[0].next == inner[1]
    assert inner[1].next == inner[2]
    assert inner[2].next == inner[3]
    assert inner[3].next == inner[4]
    assert inner[4].next is None


def test_node_previous():
    red = RedBaron("[1, 2, 3]")
    assert red.previous is None
    assert red[0].previous is None
    inner = red[0].value
    assert inner[4].previous == inner[3]
    assert inner[3].previous == inner[2]
    assert inner[2].previous == inner[1]
    assert inner[1].previous == inner[0]
    assert inner[0].previous is None


def test_node_next_generator():
    red = RedBaron("[1, 2, 3]")
    assert list(red[0].value[2].next_generator()) == list(red[0].value[3:])


def test_node_previous_generator():
    red = RedBaron("[1, 2, 3]")
    assert list(red[0].value[2].previous_generator()) == list(reversed(red[0].value[:2]))


def test_map():
    red = RedBaron("[1, 2, 3]")
    assert red('int').map(lambda x: x.value) == NodeList([1, 2, 3])


def test_filter():
    red = RedBaron("[1, 2, 3]")
    assert red[0].value.filter(lambda x: x.type != "comma") == red('int')
    assert isinstance(red[0].value.filter(lambda x: x.type != "comma"), NodeList)


def test_append_item_comma_list_empty():
    red = RedBaron("[]")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"


def test_append_item_comma_list_one():
    red = RedBaron("[1]")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"


def test_append_item_comma_list_one_comma():
    red = RedBaron("[1,]")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"


def test_append_item_comma_list_empty_trailing():
    red = RedBaron("[]")
    r = red[0]
    r.append_value("4", trailing=True)
    assert r.value.dumps() == "4,"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"


def test_append_item_comma_list_one_trailing():
    red = RedBaron("[1]")
    r = red[0]
    r.append_value("4", trailing=True)
    assert r.value.dumps() == "1, 4,"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"


def test_append_item_comma_list_one_comma_trailing():
    red = RedBaron("[1,]")
    r = red[0]
    r.append_value("4", trailing=True)
    assert r.value.dumps() == "1, 4,"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"


def test_append_item_comma_set():
    red = RedBaron("{1}")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    # FIXME: bug in baron, can't parse next stuff
    # red = RedBaron("{1,}")
    # r = red[0]
    # r.append_value("4")
    # assert r.value.dumps() == "1, 4"
    # assert r.value[-1].parent is r
    # assert r.value[-1].on_attribute == "value"
    # assert r.value[-2].parent is r
    # assert r.value[-2].on_attribute == "value"


def test_append_item_comma_tuple():
    red = RedBaron("()")
    r = red[0]
    r.append_value("4")
    # should add a comma for a single item tuple
    assert r.value.dumps() == "4,"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    red = RedBaron("(1,)")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"
    red = RedBaron("(1, 2)")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 2, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"


def test_append_item_comma_tuple_without_parenthesis():
    red = RedBaron("1,")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"
    red = RedBaron("1, 2")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 2, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"


def test_append_item_comma_dict_empty():
    red = RedBaron("{}")
    r = red[0]
    r.append_value(key="a", value="b")
    assert r.value.dumps() == "a: b"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    red = RedBaron("{1: 2}")
    r = red[0]
    r.append_value(key="a", value="b")
    assert r.value.dumps() == "1: 2, a: b"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    red = RedBaron("{1: 2,}")
    r = red[0]
    r.append_value(key="a", value="b")
    assert r.value.dumps() == "1: 2, a: b"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"


def test_append_item_comma_list_node():
    red = RedBaron("[]")
    r = red[0]
    r.append_value(IntNode({"value": "4", "type": "int"}))
    assert r.value.dumps() == "4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"


def test_append_item_comma_repr():
    red = RedBaron("`1`")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"


def test_indent_root():
    red = RedBaron("pouet")
    assert red[0].indentation == ""
    red = RedBaron("pouet\nplop\npop")
    assert map(lambda x: x.indentation, red) == ["", "", "", "", ""]


def test_in_while():
    red = RedBaron("while a:\n    pass\n")
    assert red[0].value[-2].indentation == "    "
