import pytest

# pytest files must end with _test.py


def mult(a, b):
    return a * b


def test_1():
    assert mult(3, 6) == 18


'''
fixture dictates a function which can generate values, and be passed as an argument to the test function

@pytest.fixture -- will mean this fixture runs on each individual test function that uses it
@pytest.fixture(scope="module") -- will mean this fixture will run once per test file
@pytest.fixture(scope="session") -- will mean this fixture will run once per test session
All 3 still need to be added to the fixture that needs it as a parameter

@pytest.fixture(autouse=True) -- will mean this fixture is passed to every test automatically

@pytest.fixture(autouse=True, scope="session") -- all functions will be passed this fixture, and it will have only been called once
'''

# @pytest.fixture(scope="module")
# def data():
#     pass
#     # db = psql()
#     # conn = db.connect()
#     # curs = conn.cursor()
#     # yield curs
#     # curs.close()
#     # conn.close()

# def test_2(data):
#     assert mult(data['name']) == 'Test Daly'


# Can put tests in a class to encapsulate common parameters
class TestExample:
    a = 1
    b = 2

    def test_3(self):
        assert mult(self.a, self.b) == 2
        assert mult(self.a, self.b) == 4
