# tantan · HTTP 探测与 Zabbix 集成示例

一组 Python 脚本，用目标清单批量探测 HTTP 服务，将状态码和响应耗时写入 JSON，并演示如何通过 Zabbix API 批量创建监控项、图形和触发器。

[本地验证](#本地验证) · [指标说明](#指标说明) · [Zabbix 集成](#zabbix-集成)

> 项目按 Python 3.7 和历史依赖编写，适合在隔离环境中复现实验。现代 Python 与 Zabbix 版本的兼容性需按目标环境验证。

## 本地验证

采集和读取指标可以在本机完成，无需连接 Zabbix。运行前，请用自己的测试目标替换随仓库提供的旧清单。采集会请求清单中的主地址和后端地址，并覆盖根目录的结果文件。

```bash
git clone https://github.com/kinzun/tantan.git
cd tantan
python3.7 -m venv .venv
source .venv/bin/activate
python -m pip install wheel
python -m pip install tornado==6.0.3 pycurl==7.43.0.3 xlrd==1.2.0 chardet==3.0.4
```

以上是本地采集所需的依赖版本。完整的历史依赖见 [requirements.txt](requirements.txt)。

在 `bin/urls_alone.xlsx` 的 `Sheet1` 中保留首行为表头，用下面一行替换原有数据。脚本按列的位置读入这六项。

| 业务名 | 主 URL | 响应文本 | 预期状态码 | 后端 URL | 响应类型 |
| --- | --- | --- | --- | --- | --- |
| 本地测试 | `http://127.0.0.1:8000/` | 留空 | `200` | `http://127.0.0.1:8000/` | 留空 |

在另一个终端启动本地 HTTP 服务，然后回到已激活虚拟环境的终端运行采集。状态码读取示例预期返回 `200`。

```bash
# 另一个终端，在任意空目录运行
python3 -m http.server 8000 --bind 127.0.0.1

# 回到 tantan 仓库目录
python run_m.py
python read_time_code.py 'http%3A%2F%2F127.0.0.1%3A8000%2F'
```

## 指标说明

[采集入口](run_m.py) 使用 Tornado 和 PycURL 发起请求。结果保存在根目录的 `url_time_info.json`，以 URL 经 `urllib.parse.quote_plus` 编码后的值为键。后端结果在对应主目标的 `backend_real` 下。读取脚本的第一个参数是编码后的主 URL，可选的第二个参数是编码后的后端 URL。

| 读取脚本 | JSON 字段 | 含义 |
| --- | --- | --- |
| [read_time_code.py](read_time_code.py) | `code` | HTTP 状态码 |
| [read_time_connect.py](read_time_connect.py) | `connect` | 从请求开始到连接建立，单位为秒 |
| [read_time_start.py](read_time_start.py) | `starttransfer` | 从请求开始到收到首字节，单位为秒 |
| [read_time_total.py](read_time_total.py) | `total` | 请求总耗时，单位为秒 |

## Zabbix 集成

- [zabbix_api.py](zabbix_api.py) 封装 Zabbix JSON-RPC 调用，以及主机、监控项、图形和触发器相关操作。
- [create_zabix_task.py](create_zabix_task.py) 展示如何批量配置监控项、图形和触发器。直接运行会向配置的 Zabbix 实例写入配置。请先检查脚本中的连接和主机设置、现有监控键及目标版本的 API，并在测试实例上验证。[Zabbix API 文档](https://www.zabbix.com/documentation/current/en/manual/api)
- [bin/read_xlsx.py](bin/read_xlsx.py) 解析目标表格，[record/](record/) 保存早期实验脚本。
