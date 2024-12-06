import random

rag_ob = {
    "messages": [
        {
            "dataId": "vjXRCrE957xeGJHL9OcpPF5S",
            "role": "user",
            "content": "魔方大厦"
        }
    ],
    "nodes": [
        {
            "nodeId": "userGuide",
            "name": "系统配置",
            "intro": "",
            "flowNodeType": "userGuide",
            "isEntry": True,
            "inputs": [],
            "outputs": [],
            "version": "481"
        },
        {
            "nodeId": "workflowStartNodeId",
            "name": "流程开始",
            "avatar": "core/workflow/template/workflowStart",
            "intro": "",
            "flowNodeType": "workflowStart",
            "isEntry": True,
            "inputs": [
                {
                    "key": "userChatInput",
                    "renderTypeList": [
                        "reference",
                        "textarea"
                    ],
                    "valueType": "string",
                    "label": "workflow:user_question",
                    "toolDescription": "workflow:user_question",
                    "required": True
                }
            ],
            "outputs": [
                {
                    "id": "userChatInput",
                    "key": "userChatInput",
                    "label": "common:core.module.input.label.user question",
                    "type": "static",
                    "valueType": "string"
                },
                {
                    "id": "userFiles",
                    "key": "userFiles",
                    "label": "app:workflow.user_file_input",
                    "description": "app:workflow.user_file_input_desc",
                    "type": "static",
                    "valueType": "arrayString"
                }
            ],
            "version": "481"
        },
        {
            "nodeId": "7BdojPlukIQw",
            "name": "AI 对话",
            "avatar": "core/workflow/template/aiChat",
            "intro": "AI 大模型对话",
            "flowNodeType": "chatNode",
            "showStatus": True,
            "isEntry": False,
            "inputs": [
                {
                    "key": "model",
                    "renderTypeList": [
                        "settingLLMModel",
                        "reference"
                    ],
                    "label": "",
                    "valueType": "string",
                    "value": "SuperGPT"
                },
                {
                    "key": "temperature",
                    "renderTypeList": [
                        "hidden"
                    ],
                    "label": "",
                    "value": 0,
                    "valueType": "number",
                    "min": 0,
                    "max": 10,
                    "step": 1
                },
                {
                    "key": "maxToken",
                    "renderTypeList": [
                        "hidden"
                    ],
                    "label": "",
                    "value": 2000,
                    "valueType": "number",
                    "min": 100,
                    "max": 4000,
                    "step": 50
                },
                {
                    "key": "isResponseAnswerText",
                    "renderTypeList": [
                        "hidden"
                    ],
                    "label": "",
                    "value": True,
                    "valueType": "boolean"
                },
                {
                    "key": "quoteTemplate",
                    "renderTypeList": [
                        "hidden"
                    ],
                    "label": "",
                    "valueType": "string"
                },
                {
                    "key": "quotePrompt",
                    "renderTypeList": [
                        "hidden"
                    ],
                    "label": "",
                    "valueType": "string"
                },
                {
                    "key": "systemPrompt",
                    "renderTypeList": [
                        "textarea",
                        "reference"
                    ],
                    "max": 3000,
                    "valueType": "string",
                    "label": "core.ai.Prompt",
                    "description": "core.app.tip.chatNodeSystemPromptTip",
                    "placeholder": "core.app.tip.chatNodeSystemPromptTip",
                    "value": ""
                },
                {
                    "key": "history",
                    "renderTypeList": [
                        "numberInput",
                        "reference"
                    ],
                    "valueType": "chatHistory",
                    "label": "core.module.input.label.chat history",
                    "required": True,
                    "min": 0,
                    "max": 30,
                    "value": 6
                },
                {
                    "key": "userChatInput",
                    "renderTypeList": [
                        "reference",
                        "textarea"
                    ],
                    "valueType": "string",
                    "label": "用户问题",
                    "required": True,
                    "toolDescription": "用户问题",
                    "value": [
                        "workflowStartNodeId",
                        "userChatInput"
                    ]
                },
                {
                    "key": "quoteQA",
                    "renderTypeList": [
                        "settingDatasetQuotePrompt"
                    ],
                    "label": "",
                    "debugLabel": "知识库引用",
                    "description": "",
                    "valueType": "datasetQuote",
                    "value": [
                        "iKBoX2vIzETU",
                        "quoteQA"
                    ]
                },
                {
                    "key": "aiChatVision",
                    "renderTypeList": [
                        "hidden"
                    ],
                    "label": "",
                    "valueType": "boolean",
                    "value": True
                }
            ],
            "outputs": [
                {
                    "id": "history",
                    "key": "history",
                    "required": True,
                    "label": "core.module.output.label.New context",
                    "description": "core.module.output.description.New context",
                    "valueType": "chatHistory",
                    "type": "static"
                },
                {
                    "id": "answerText",
                    "key": "answerText",
                    "required": True,
                    "label": "core.module.output.label.Ai response content",
                    "description": "core.module.output.description.Ai response content",
                    "valueType": "string",
                    "type": "static"
                }
            ],
            "version": "481"
        },
        {
            "nodeId": "iKBoX2vIzETU",
            "name": "知识库搜索",
            "avatar": "core/workflow/template/datasetSearch",
            "intro": "调用“语义检索”和“全文检索”能力，从“知识库”中查找可能与问题相关的参考内容",
            "flowNodeType": "datasetSearchNode",
            "showStatus": True,
            "isEntry": False,
            "inputs": [
                {
                    "key": "datasets",
                    "renderTypeList": [
                        "selectDataset",
                        "reference"
                    ],
                    "label": "core.module.input.label.Select dataset",
                    "value": [
                        {
                            "datasetId": "672b243ae05b1f7c0c0bd9d5"
                        }
                    ],
                    "valueType": "selectDataset",
                    "list": [],
                    "required": True
                },
                {
                    "key": "datasetTop_k",
                    "renderTypeList": [
                        "hidden"
                    ],
                    "label": "",
                    "value": 10,
                    "valueType": "number"
                },
                {
                    "key": "rerank_threshold",
                    "renderTypeList": [
                        "hidden"
                    ],
                    "label": "",
                    "value": 0,
                    "valueType": "number"
                },
                {
                    "key": "similarity",
                    "renderTypeList": [
                        "selectDatasetParamsModal"
                    ],
                    "label": "",
                    "value": 0.1,
                    "valueType": "number"
                },
                {
                    "key": "limit",
                    "renderTypeList": [
                        "hidden"
                    ],
                    "label": "",
                    "value": 1500,
                    "valueType": "number"
                },
                {
                    "key": "searchMode",
                    "renderTypeList": [
                        "hidden"
                    ],
                    "label": "",
                    "valueType": "string",
                    "value": "fullTextRecall"
                },
                {
                    "key": "usingReRank",
                    "renderTypeList": [
                        "hidden"
                    ],
                    "label": "",
                    "valueType": "boolean",
                    "value": False
                },
                {
                    "key": "datasetSearchUsingExtensionQuery",
                    "renderTypeList": [
                        "hidden"
                    ],
                    "label": "",
                    "valueType": "boolean",
                    "value": False
                },
                {
                    "key": "datasetSearchExtensionModel",
                    "renderTypeList": [
                        "hidden"
                    ],
                    "label": "",
                    "valueType": "string"
                },
                {
                    "key": "datasetSearchExtensionBg",
                    "renderTypeList": [
                        "hidden"
                    ],
                    "label": "",
                    "valueType": "string",
                    "value": ""
                },
                {
                    "key": "userChatInput",
                    "renderTypeList": [
                        "reference",
                        "textarea"
                    ],
                    "valueType": "string",
                    "label": "用户问题",
                    "required": True,
                    "toolDescription": "需要检索的内容",
                    "value": [
                        "workflowStartNodeId",
                        "userChatInput"
                    ]
                }
            ],
            "outputs": [
                {
                    "id": "quoteQA",
                    "key": "quoteQA",
                    "label": "core.module.Dataset quote.label",
                    "description": "workflow:special_array_format",
                    "type": "static",
                    "valueType": "datasetQuote"
                }
            ],
            "version": "481"
        }
    ],
    "edges": [
        {
            "source": "workflowStartNodeId",
            "target": "iKBoX2vIzETU",
            "sourceHandle": "workflowStartNodeId-source-right",
            "targetHandle": "iKBoX2vIzETU-target-left",
            "status": "waiting"
        },
        {
            "source": "iKBoX2vIzETU",
            "target": "7BdojPlukIQw",
            "sourceHandle": "iKBoX2vIzETU-source-right",
            "targetHandle": "7BdojPlukIQw-target-left",
            "status": "waiting"
        }
    ],
    "variables": {
        "cTime": "2024-11-06 17:22:49 Wednesday"
    },
    "appId": "672b2ab5e05b1f7c0c0bdcd0",
    "appName": "调试-webpcm-test",
    "chatConfig": {
        "questionGuide": False,
        "ttsConfig": {
            "type": "web"
        },
        "whisperConfig": {
            "open": False,
            "autoSend": False,
            "autoTTSResponse": False
        },
        "scheduledTriggerConfig": {
            "cronString": "",
            "timezone": "Asia/Shanghai",
            "defaultPrompt": ""
        },
        "chatInputGuide": {
            "open": False,
            "textList": [],
            "customUrl": ""
        },
        "variables": [],
        "welcomeText": "",
        "fileSelectConfig": {
            "canSelectFile": False,
            "canSelectImg": False,
            "maxFiles": 10
        }
    },
    "detail": True,
    "stream": False
}



def custom_alphabet(alphabet, size):
    """Generate a random string of given size from the provided alphabet."""
    return ''.join(random.choice(alphabet) for _ in range(size))


def get_nanoid(size=12):
    """Generate a NanoID with a specified size, ensuring the first character is lowercase."""
    if size < 1:
        raise ValueError("Size must be at least 1")

    lowercase_alphabet = 'abcdefghijklmnopqrstuvwxyz'
    full_alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

    # Ensure the first character is lowercase
    first_char = random.choice(lowercase_alphabet)

    if size == 1:
        return first_char

    # Generate the rest of the NanoID
    random_str = custom_alphabet(full_alphabet, size - 1)

    return f"{first_char}{random_str}"

omega_rag_request_obj = {
        "messages": [
            {
                # "dataId": "kaeT6snXRn6iDBjqu34hWGUG",
                "dataId": get_nanoid(12),
                "role": "user",
                "content": "机顶盒开机报错775"
            }
        ],
        "variables": {
            "cTime": "2024-11-15 17:32:44 Friday"
        },
        # "responseChatItemId": "i9ihZ7gVj5j0BKESZvptmg3w",
        "responseChatItemId": get_nanoid(12),
        "appId": "672b2ab5e05b1f7c0c0bdcd0",
        # "chatId": "lhtdm1lJ1lyO",
        "chatId": get_nanoid(12),
        "chatSource": "online",
        "detail": True,
        "stream": False
    }

import datetime
def get_cur_time():
    curr_time = datetime.datetime.now()
    timestamp = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S ')
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # print(timestamp + weekdays[datetime.date.today().weekday()])
    return timestamp + weekdays[datetime.date.today().weekday()]


def get_request_param(question, appid):
    payload = {}
    payload["messages"] = [{
        # "dataId": "f1cxNsgkgjJdTjA0LK4YSWY4",
        "dataId": get_nanoid(24),
        "role": "user",
        "content": question}]
    # payload["variables"] = {"cTime": "2024-11-26 10:51:13 Tuesday"}
    payload["variables"] = {"cTime": get_cur_time()}
    # payload["responseChatItemId"] = "bwtfJeV7qMYJxz5edIiDfDDX"
    payload["responseChatItemId"] = get_nanoid(24)
    # payload["appId"] = "672b2ab5e05b1f7c0c0bdcd0"
    payload["appId"] = appid
    payload["chatId"] = get_nanoid(12)
    # payload["chatId"] = "uHEJytyvwlBE"
    payload["chatSource"] = "online"
    payload["detail"] = True
    payload["stream"] = False
    return payload
