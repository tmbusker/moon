import pytest
from io import StringIO, BytesIO
from cmm.tests.cmm_fixtures import AuthUserAdmin


csv_data = ','.join(AuthUserAdmin.csv_headers) + '\n'
csv_data += 'password,tester1,2023/09/16,False\n'
csv_data += 'password,tester2,2023/09/16,False\n'
csv_data += 'password,tester3,2023/09/16,False\n'
csv_data += 'password,tester4,2023/09/16,False\n'
csv_data += 'password,tester5,2023/09/16,False\n'


@pytest.fixture
def csv_file():
    str_io = StringIO(csv_data)
    byte_buffer = BytesIO(str_io.getvalue().encode())
    byte_buffer.name = 'test.csv'
    return byte_buffer
