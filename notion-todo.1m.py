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
from datetime import date, datetime


class DisplayItem:
    def __init__(self, title="", body="", status="", end="") -> None:
        self.title = title
        self.body = body
        self.status = status
        self.end = end

    def getEmoji(self):
        if self.status == "进行中":
            return ":construction:"
        if self.status == "准备进行":
            return ":rocket:"
        return ""

    def getEndTips(self):
        if self.end != "":
            endTime = datetime.strptime(self.end, "%Y-%m-%d")
            return "〆"+endTime.month.__str__()+"/"+endTime.day.__str__()
        return ""

    def to_display(self):
        print(self.getEmoji() + " " + self.getEndTips() + " " + self.title)
        print("----")
        print(self.body)


def printTodo(todo=""):
    print(":construction: "+todo)


conn = http.client.HTTPSConnection("api.notion.com")
payload = json.dumps({
    "filter": {
        "or": [
            {
                "property": "Status",
                "select": {
                    "equals": "进行中"
                }
            },
            {
                "property": "Status",
                "select": {
                    "equals": "准备进行"
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
doingList = []
planList = []


if len(j["results"]) > 0:
    for item in j["results"]:
        if showTitle == "" and item["properties"]["Status"]["select"]["name"] == "进行中":
            showTitle = item["properties"]["Name"]["title"][0]["text"]["content"]

        showBody = ""
        if len(item["properties"]["Tag"]["multi_select"]) > 0:
            showBody += "--"
            for tag in item["properties"]["Tag"]["multi_select"]:
                showBody += "["+tag["name"]+"] "

        if item["properties"]["tapd"]["url"] is not None:
            showBody += "\r\n"
            showBody += "--"
            showBody += "点击打开Tapd | href=" + item["properties"]["tapd"]["url"]

        end = ""
        if item["properties"]["Date"]["date"] is not None:
            end = item["properties"]["Date"]["date"]["end"]
            showBody += "\r\n"
            showBody += "--"
            showBody += item["properties"]["Date"]["date"]["start"] + \
                " - " + item["properties"]["Date"]["date"]["end"]

        if item["properties"]["Status"]["select"]["name"] == "进行中":
            doingList.append(DisplayItem(item["properties"]["Name"]["title"][0]["text"]
                             ["content"], showBody, item["properties"]["Status"]["select"]["name"], end))
        if item["properties"]["Status"]["select"]["name"] == "准备进行":
            planList.append(DisplayItem(item["properties"]["Name"]["title"][0]["text"]
                            ["content"], showBody, item["properties"]["Status"]["select"]["name"], end))


printTodo(showTitle)
print("---")
if len(doingList) == 0:
    print(":tada: 没有进行中的TODO")
for item in doingList:
    if item is not None:
        item.to_display()

print("---")
if len(planList) == 0:
    print(":coffee: 没有待进行的TODO")
for item in planList:
    if item is not None:
        item.to_display()
