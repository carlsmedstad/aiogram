import datetime
from unittest.mock import patch

import pytest
from asynctest import CoroutineMock

from aiogram.api.client.session.base import BaseSession
from aiogram.utils.mixins import DataMixin


class TestBaseSession(DataMixin):
    def setup(self):
        self["__abstractmethods__"] = BaseSession.__abstractmethods__
        BaseSession.__abstractmethods__ = set()

    def teardown(self):
        BaseSession.__abstractmethods__ = self["__abstractmethods__"]

    def test_sync_close(self):
        session = BaseSession()

        with patch(
            "aiogram.api.session.base.BaseSession.close", new=CoroutineMock()
        ) as mocked_close:
            session.__del__()
            mocked_close.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_async_close(self):
        session = BaseSession()

        with patch(
            "aiogram.api.session.base.BaseSession.close", new=CoroutineMock()
        ) as mocked_close:
            session.__del__()
            mocked_close.assert_called_once_with()

    def test_prepare_value(self):
        session = BaseSession()

        now = datetime.datetime(
            year=2019, month=11, day=15, hour=12, minute=42, second=15, microsecond=0
        )

        assert session.prepare_value("text") == "text"
        assert session.prepare_value(["test"]) == '["test"]'
        assert session.prepare_value({"test": "ok"}) == '{"test": "ok"}'
        assert session.prepare_value(now) == "1573814535"
        assert isinstance(session.prepare_value(datetime.timedelta(minutes=2)), str)
        assert session.prepare_value(42) == "42"

    def test_clean_json(self):
        session = BaseSession()

        cleaned_dict = session.clean_json({"key": "value", "null": None})
        assert "key" in cleaned_dict
        assert "null" not in cleaned_dict

        cleaned_list = session.clean_json(["kaboom", 42, None])
        assert len(cleaned_list) == 2
        assert 42 in cleaned_list
        assert None not in cleaned_list
        assert cleaned_list[0] == "kaboom"

    def test_clean_json_with_nested_json(self):
        session = BaseSession()

        cleaned = session.clean_json(
            {
                "key": "value",
                "null": None,
                "nested_list": ["kaboom", 42, None],
                "nested_dict": {"key": "value", "null": None},
            }
        )

        assert len(cleaned) == 3
        assert "null" not in cleaned

        assert isinstance(cleaned["nested_list"], list)
        assert cleaned["nested_list"] == ["kaboom", 42]

        assert isinstance(cleaned["nested_dict"], dict)
        assert cleaned["nested_dict"] == {"key": "value"}

    def test_clean_json_not_json(self):
        session = BaseSession()

        assert session.clean_json(42) == 42