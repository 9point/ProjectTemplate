from utils.RoutineID import RoutineID


def test_parse_dbid():
    rid = RoutineID.parse('tdb:1234')
    assert rid.rtype == 'tdb'
    assert rid.dbid == '1234'


def test_stringify_dbid():
    str_id = str(RoutineID.parse('wfdb:321'))
    assert str_id == 'wfdb:321'


def test_parse_tname():
    rid = RoutineID.parse('tname:hello_world')
    assert rid.rtype == 'tname'
    assert rid.project_name is None
    assert rid.routine_name == 'hello_world'
    assert rid.version is None


def test_parse_tname_with_projectname():
    rid = RoutineID.parse('tname:proj:hello_world')
    assert rid.rtype == 'tname'
    assert rid.project_name == 'proj'
    assert rid.routine_name == 'hello_world'
    assert rid.version is None


def test_parse_tname_with_version():
    rid = RoutineID.parse('tname:p:hello:1.0.0')
    assert rid.rtype == 'tname'
    assert rid.project_name == 'p'
    assert rid.routine_name == 'hello'
    assert rid.version == '1.0.0'


def test_stringify_tname():
    str_id = str(RoutineID.parse('wfname:p:h:1.0.1'))
    assert str_id == 'wfname:p:h:1.0.1'


def test_parse_wfname():
    rid = RoutineID.parse('wfname:hello_world')
    assert rid.rtype == 'wfname'
    assert rid.project_name is None
    assert rid.routine_name == 'hello_world'
    assert rid.version is None


def test_stringify_wfname():
    str_id = str(RoutineID.parse('wfname:proj:hello'))
    assert str_id == 'wfname:proj:hello'


def test_throws_if_invalid_rtype():
    try:
        RoutineID.parse('blah:123')
    except:
        return

    assert False


def test_throws_if_no_dbid():
    try:
        RoutineID.parse('dbid')
    except:
        return

    assert False


def test_throws_if_no_routinename():
    try:
        RoutineID.parse('tname')
    except:
        return

    assert False
