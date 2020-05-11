from . import deserialize, serialize


def test_serialize_number():
    num1_expected = 123
    num1_actual = deserialize(serialize(num1_expected))
    assert num1_expected is num1_actual

    num2_expected = 0.123
    num2_actual = deserialize(serialize(num2_expected))
    assert num2_expected is num2_actual

    num3_expected = 1e-14
    num3_actual = deserialize(serialize(num3_expected))
    assert num3_expected is num3_actual


def test_serialize_string():
    str1_expected = 'hello world'
    str1_actual = deserialize(serialize(str1_expected))
    assert str1_expected is str1_actual


def test_serialize_list():
    list1_expected = [1, 2, 3]
    list1_actual = deserialize(serialize(list1_expected))
    assert list1_expected == list1_actual

    list2_expected = ['a', 'b', 'c']
    list2_actual = deserialize(serialize(list2_expected))
    assert list2_expected == list2_actual


def test_serialize_nested_list():
    list1_expected = [[1, 2, 3], [4], [5, 6]]
    list1_actual = deserialize(serialize(list1_expected))
    assert list1_expected == list1_actual


def test_serialize_dict():
    dict1_expected = dict(a=1, b=2)
    dict1_actual = deserialize(serialize(dict1_expected))
    assert dict1_expected == dict1_actual


def test_serialize_nested_dict():
    dict1_expected = dict(a=1, b=dict(c=2))
    dict1_actual = deserialize(serialize(dict1_expected))
    assert dict1_expected == dict1_actual
