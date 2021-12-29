#!/usr/bin/env PYTHONIOENCODING=UTF-8 TIME_ZONE='Asia/Shanghai' USE_TZ=True python3
#
#  <xbar.title>notion todo提醒</xbar.title>
#  <xbar.version>v1.0</xbar.version>
#  <xbar.author>蒙德伊彼</xbar.author>
#  <xbar.author.github>git@github.com:cangyan/xbar-notion-todo.git</xbar.author.github>
#  <xbar.desc>将指定notion database条件过滤后输出</xbar.desc>
#  <xbar.image></xbar.image>
#  <xbar.dependencies></xbar.dependencies>
#  <xbar.var>string(XBAR_NOTION_TOKEN="abc"): Notion Token.</xbar.var>
#  <xbar.var>string(XBAR_NOTION_DB_TODO="0123"): Notion DB Id.</xbar.var>

import http.client
import json
import os


def printTodo(todo=""):
    print(":construction: "+todo)


conn = http.client.HTTPSConnection("api.notion.com")
payload = json.dumps({
    "filter": {
        "and": [
            {
                "property": "Status",
                "select": {
                    "equals": "进行中"
                }
            }
        ]
    }
})
headers = {
    'Notion-Version': '2021-08-16',
    'Authorization': 'Bearer '+os.getenv("XBAR_NOTION_TOKEN"),
    'Content-Type': 'application/json'
}

conn.request("POST", "/v1/databases/" +
             os.getenv("XBAR_NOTION_DB_TODO")+"/query", payload, headers)
res = conn.getresponse()
data = res.read()

# print(data.decode("utf-8"))
j = json.loads(data.decode("utf-8"))

#############################################################################

showTitle = ""
showBody = ""


if len(j["results"]) > 0:
    for item in j["results"]:
        showTitle = item["properties"]["Name"]["title"][0]["text"]["content"]
        if len(item["properties"]["Tag"]["multi_select"]) > 0:
            showBody += "--"
            for tag in item["properties"]["Tag"]["multi_select"]:
                showBody += "["+tag["name"]+"] "
            showBody += "\r\n"
        if item["properties"]["tapd"]["url"]:

            showBody += "--" + item["properties"]["tapd"]["url"] + "\r\n"
        if item["properties"]["Date"]["date"]["start"] and item["properties"]["Date"]["date"]["end"]:
            showBody += "--" + item["properties"]["Date"]["date"]["start"] + \
                " - " + item["properties"]["Date"]["date"]["end"]

        break

printTodo(showTitle)
print("---")
print(showTitle + "| size=14")
print("----")
print(showBody)
