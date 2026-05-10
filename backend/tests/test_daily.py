from unittest.mock import patch, AsyncMock, MagicMock
from httpx import Response
import pytest
import io
import zipfile
import respx

from utils.daily import (
    get_update,
    stream_csv,
    parse_event,
    parse_mentions,
    parse_gkg,

    EVENT_COLUMNS,
    GKG_COLUMNS,
    MENTIONS_COLUMNS
)

def create_mock_zips(filename: list[str], content: list[str]) -> bytes:

    zip_buffer = io.BytesIO()

    csvs = zip(filename, content)

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file, cont in csvs:
            zf.writestr(file, cont)

    zip_buffer.seek(0)

    return zip_buffer.getvalue()

# Run using: pytest -v -s
@respx.mock
@pytest.mark.asyncio
async def test_get_update():
    url = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"

    row1 = "0 hash1 http://data.gdeltproject.org/gdeltv2/1111.export.CSV.zip"
    row2 = "1 hash2 http://data.gdeltproject.org/gdeltv2/2222.mentions.CSV.zip"
    row3 = "2 hash3 http://data.gdeltproject.org/gdeltv2/3333.gkg.csv.zip"

    respx.get(url).mock(
        return_value=Response(200, text="\n".join([row1, row2, row3]))
    )

    response = await get_update()

    assert response == [
        "http://data.gdeltproject.org/gdeltv2/1111.export.CSV.zip",
        "http://data.gdeltproject.org/gdeltv2/2222.mentions.CSV.zip",
        "http://data.gdeltproject.org/gdeltv2/3333.gkg.csv.zip"
    ]

@respx.mock
@pytest.mark.asyncio
async def test_get_update_error():
    url = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"

    respx.get(url).mock(
        return_value=Response(500, text="")
    )

    with pytest.raises(Exception, match="GDELT API Down"):
        await get_update()

@respx.mock
@pytest.mark.asyncio
async def test_stream_csv():
    url = "http://data.gdeltproject.org/mock.zip"
    
    cols = ["FakeCol1", "FakeCol2"]
    fake_csv = "val1\tval2\nval3\tval4"
    fake_zip = create_mock_zips(["fake.csv"], [fake_csv])

    respx.get(url).mock(
        return_value=Response(200, content=fake_zip)
    )

    parsed_csv = [row async for row in stream_csv(url, cols)]

    assert parsed_csv == [
        {'FakeCol1': 'val1', 'FakeCol2': 'val2'}, 
        {'FakeCol1': 'val3', 'FakeCol2': 'val4'}
    ]

@respx.mock
@pytest.mark.asyncio
async def test_stream_csv_api_down():
    url = "http://data.gdeltproject.org/mock.zip"
    
    cols = ["FakeCol1", "FakeCol2"]
    fake_csv = "val1\tval2\nval3\tval4"
    fake_zip = create_mock_zips(["fake.csv"], [fake_csv])

    respx.get(url).mock(
        return_value=Response(500, content=fake_zip)
    )

    with pytest.raises(Exception, match="GDELT API Down"):
        gen = stream_csv(url, cols)

        async for _ in gen:
            pass


@respx.mock
@pytest.mark.asyncio
async def test_stream_csv_improp_fmt():
    url = "http://data.gdeltproject.org/mock.zip"
    
    cols = ["FakeCol1", "FakeCol2"]
    fake_csv = "val1\tval2\nval3\tval4"
    fake_zip = create_mock_zips(["fake.csv", "extra.csv"], [fake_csv, ""])

    respx.get(url).mock(
        return_value=Response(200, content=fake_zip)
    )

    with pytest.raises(Exception, match="Improper CSV Format"):
        gen = stream_csv(url, cols)

        async for _ in gen:
            pass

@respx.mock
@pytest.mark.asyncio
@pytest.mark.parametrize("columns, func", [
    (EVENT_COLUMNS, parse_event),
    (MENTIONS_COLUMNS, parse_mentions),
    (GKG_COLUMNS, parse_gkg),
])
async def test_parse_event(columns, func):
    url = "http://data.gdeltproject.org/mock.zip"
    
    vals = [str(i) for i in range(0, len(columns))]
    fake_csv = "\t".join(vals)
    fake_zip = create_mock_zips(["fake.csv"], [fake_csv])

    respx.get(url).mock(
        return_value=Response(200, content=fake_zip)
    )

    parsed_csv = [row async for row in await func(url)]

    res = dict()
    for col, val in zip(columns, vals):
        res[col] = val

    
    assert parsed_csv[0] == res
    