# CDN流量采样推送接口文档

## 1. 基本说明

- 模块：CDN流量采样推送
- 接口路径：`/system/cdn/traffic/samples`
- 请求方法：`POST`
- 代码入口：[CdnTrafficController.java](D:/workspace/idc/idc_bill_rehearsal_platfrom/wx-system/src/main/java/com/wxdata/archetype/modules/idc/controller/CdnTrafficController.java)
- 鉴权说明：该接口已加入 Shiro 白名单，不校验 `X-Access-Token`
- 返回结构：统一使用 `Result<T>`

```json
{
  "success": true,
  "message": "",
  "code": 0,
  "result": {},
  "timestamp": 1710000000000
}
```

## 2. 接口说明

- 用途：接收某个客户某一天的流量采样点数据
- 特点：支持重复推送，同一客户同一 `sampleTime` 按最新值覆盖
- 入库单位：统一换算成 `Mbps`

## 3. 业务规则

- 一个客户同一个 `sampleTime` 只保留一条数据
- 重复推送时按最新值覆盖原记录
- 所有流量值统一换算成 `Mbps` 落库
- 当前支持单位：
  - `Mbps`
  - `M`
  - `Gbps`
  - `G`
- `sampleTime` 必须落在 `statDate` 当天
- `trafficValue` 不能为负数

## 4. 请求体

```json
{
  "customerId": "cust_1001",
  "customerName": "网宿科技股份有限公司",
  "statDate": "2026-06-09",
  "sourceType": "api",
  "batchNo": "cdn-20260609-001",
  "remark": "日采样补数",
  "samples": [
    {
      "sampleTime": "2026-06-09 00:00:00",
      "trafficValue": 125.36,
      "trafficUnit": "Mbps"
    },
    {
      "sampleTime": "2026-06-09 00:05:00",
      "trafficValue": 0.53,
      "trafficUnit": "Gbps"
    }
  ]
}
```

## 5. 字段说明

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `customerId` | `string` | 是 | 客户ID |
| `customerName` | `string` | 是 | 客户名称 |
| `statDate` | `string` | 是 | 统计日期，格式 `yyyy-MM-dd` |
| `sourceType` | `string` | 否 | 数据来源，空时默认 `api` |
| `batchNo` | `string` | 否 | 批次号 |
| `remark` | `string` | 否 | 备注 |
| `samples` | `array` | 是 | 采样点列表，不能为空 |
| `samples[].sampleTime` | `string` | 是 | 采样时间，格式 `yyyy-MM-dd HH:mm:ss` |
| `samples[].trafficValue` | `number` | 是 | 流量值，不能小于 `0` |
| `samples[].trafficUnit` | `string` | 否 | 流量单位，支持 `Mbps/M/Gbps/G`，空时按 `Mbps` 处理 |

## 6. 成功返回

```json
{
  "success": true,
  "message": "",
  "code": 0,
  "result": {
    "totalCount": 2,
    "createdCount": 1,
    "updatedCount": 1,
    "failedCount": 0
  },
  "timestamp": 1710000000000
}
```

## 7. 返回字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `totalCount` | `number` | 本次接收采样点总数 |
| `createdCount` | `number` | 新增条数 |
| `updatedCount` | `number` | 覆盖更新条数 |
| `failedCount` | `number` | 失败条数，当前实现固定为 `0` |

## 8. 失败场景

- `customerId不能为空`
- `customerName不能为空`
- `statDate不能为空`
- `statDate格式必须为yyyy-MM-dd`
- `samples不能为空`
- `samples存在空元素`
- `sampleTime不能为空`
- `sampleTime格式必须为yyyy-MM-dd HH:mm:ss`
- `trafficValue不能为空`
- `trafficValue不能为负数`
- `sampleTime必须落在statDate当天`
- `暂不支持的流量单位: xxx`
