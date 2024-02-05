# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import sys

from Tea.exceptions import TeaException
from typing import List

from alibabacloud_dyvmsapi20170525.client import Client as DyvmsapiClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_darabonba_env.client import Client as EnvClient
from alibabacloud_dyvmsapi20170525 import models as dyvmsapi_models
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_tea_console.client import Client as ConsoleClient
from alibabacloud_darabonba_number.client import Client as NumberClient


class Sample:
    def __init__(self):
        #pass
        phone_number = sys.argv[1] #接收语音通知的手机号码 string '13899988776'
        tts_code = sys.argv[2] #已通过审核的语音验证码模板ID '123'
        tts_param= sys.argv[3] #语音验证码模板参数 '{\"code\":\"123\"}' "{\"AckNum\":\"123\"}"
        play_times= sys.argv[4] #播放次数 '1'
        speed = sys.argv[5] #播放速度 '111'
        out_id = sys.argv[6] #预留的扩展字段 'qdwxqdwx'
        volume = sys.argv[7] #播放音量 '100'
    @staticmethod
    def create_dyvmsapi_client() -> DyvmsapiClient:
        """
        使用AK&SK初始化账号Client
        """
        config = open_api_models.Config(
            access_key_id=EnvClient.get_env('AK'),  #AK
            access_key_secret=EnvClient.get_env('SK')   #SK
        )
        return DyvmsapiClient(config)

    @staticmethod
    def single_call_by_tts(
        client: DyvmsapiClient,
        called_number: str,
        tts_code: str,
    ) -> dyvmsapi_models.SingleCallByTtsResponse:
        req = dyvmsapi_models.SingleCallByTtsRequest(
            called_number=called_number,
            tts_code=tts_code
        )
        resp = client.single_call_by_tts(req)
        if not UtilClient.equal_string(resp.body.code, 'OK'):
            raise TeaException({
                'code': resp.body.code,
                'message': resp.body.message
            })
        ConsoleClient.log(f'------------singleCallByTts success-------------')
        return resp

    @staticmethod
    async def single_call_by_tts_async(
        client: DyvmsapiClient,
        called_number: str,
        tts_code: str,
    ) -> dyvmsapi_models.SingleCallByTtsResponse:
        req = dyvmsapi_models.SingleCallByTtsRequest(
            called_number=called_number,
            tts_code=tts_code
        )
        resp = await client.single_call_by_tts_async(req)
        if not UtilClient.equal_string(resp.body.code, 'OK'):
            raise TeaException({
                'code': resp.body.code,
                'message': resp.body.message
            })
        ConsoleClient.log(f'------------singleCallByTts success-------------')
        return resp

    @staticmethod
    def query_call_detail_by_call_id(
        client: DyvmsapiClient,
        call_id: str,
        query_time: int,
    ) -> None:
        req = dyvmsapi_models.QueryCallDetailByCallIdRequest(
            call_id=call_id,
            prod_id=11000000300006,
            query_date=query_time
        )
        resp = client.query_call_detail_by_call_id(req)
        ConsoleClient.log(f'------------语音验证码{call_id}详情-------------')
        ConsoleClient.log(UtilClient.to_jsonstring(UtilClient.to_map(resp)))

    @staticmethod
    async def query_call_detail_by_call_id_async(
        client: DyvmsapiClient,
        call_id: str,
        query_time: int,
    ) -> None:
        req = dyvmsapi_models.QueryCallDetailByCallIdRequest(
            call_id=call_id,
            prod_id=11000000300006,
            query_date=query_time
        )
        resp = await client.query_call_detail_by_call_id_async(req)
        ConsoleClient.log(f'------------语音验证码{call_id}详情-------------')
        ConsoleClient.log(UtilClient.to_jsonstring(UtilClient.to_map(resp)))

    @staticmethod
    def main(
        args: List[str],
    ) -> None:
        # 接收语音通知的手机号码
        called_number = args[0]
        # 已通过审核的语音验证码模板ID
        tts_code = args[1]
        # 指定通话发生的时间，格式为Unix时间戳，单位毫秒。会查询这个时间点对应的一整天的记录
        query_time = NumberClient.parse_long(args[3])
        client = Sample.create_dyvmsapi_client()
        single_call_by_tts_resp = Sample.single_call_by_tts(client, called_number, tts_code)
        Sample.query_call_detail_by_call_id(client, single_call_by_tts_resp.body.call_id, query_time)

    @staticmethod
    async def main_async(
        args: List[str],
    ) -> None:
        # 接收语音通知的手机号码
        called_number = args[0]
        # 已通过审核的语音验证码模板ID
        tts_code = args[1]
        # 指定通话发生的时间，格式为Unix时间戳，单位毫秒。会查询这个时间点对应的一整天的记录
        query_time = NumberClient.parse_long(args[3])
        client = Sample.create_dyvmsapi_client()
        single_call_by_tts_resp = await Sample.single_call_by_tts_async(client, called_number, tts_code)
        await Sample.query_call_detail_by_call_id_async(client, single_call_by_tts_resp.body.call_id, query_time)


if __name__ == '__main__':
    Sample.main(sys.argv[1:])