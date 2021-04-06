import asyncio

import pytest
import numpy as np

from backend_utils.information_processor import InformationProcessor


@pytest.fixture
def info_processor():
    return InformationProcessor()


@pytest.fixture
def single_message_unity():
    return "0,0,0:0,0,0,1"


@pytest.fixture
def multi_message():
    return "0,0,0:0,0,0,1|2,2,2:0,0,0,1X"


class TestInformationProcessor():

    @pytest.mark.asyncio
    async def test_process_individual_message(self,
                                              info_processor: InformationProcessor,
                                              single_message_unity: str):
        result = await info_processor._process_individual_information(single_message_unity)
        res_pos, res_rot = result

        assert res_pos == [0, 0, 0]
        assert res_rot == [0, 0, 0, 1]

    @pytest.mark.asyncio
    async def test_process_hololens(self, info_processor: InformationProcessor,
                                    multi_message: str):
        res_pos, res_rot = await info_processor.process_hololens_data(multi_message)
        assert res_pos == [1, 1, 1]
        assert res_rot == [0, 0, 0, 1]
