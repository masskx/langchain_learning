#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mcp_explorer.py — 可视化演示 Weather MCP 的完整工作过程（四角色版）

这个脚本用一个真实例子，展示 MCP 官方架构里的四个角色是怎么配合的：

    用户(User)  ⇄  MCP Host(宿主)  ⇄  MCP Client(客户端)  ⇄  MCP Server(服务器)

关键认知：MCP 协议（JSON-RPC）只存在于 Client ⇄ Server 之间。
「用户提问 → Host 分析 → 让 Client 去调工具」这三步是应用内部的事，不属于 MCP。

演示例子：用户在 Claude Code 里问「旧金山现在天气怎么样？」
脚本会真实启动 weather MCP 服务器，走一遍 initialize / tools/list / tools/call，
把真实的 JSON-RPC 消息抓下来，再和用户/Host/Client 的应用层消息拼成完整时序图，
最后生成 mcp_workflow.html。

用法：
    python mcp_explorer.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
from pathlib import Path

# ---- weather MCP 服务器的启动命令（就是 ~/.claude.json 里配的那个）----
SERVER_CMD = [
    r"D:/DevSpace/langchain/.venv/Scripts/python.exe",
    r"D:/DevSpace/langchain/jupyter/mcp/weather.py",
]

OUTPUT_HTML = Path(__file__).with_name("mcp_workflow.html")

# 演示用的真实例子：旧金山的预报
DEMO_QUESTION = "旧金山现在天气怎么样？"
DEMO_CITY = "旧金山（San Francisco）"
DEMO_LAT, DEMO_LON = 37.7749, -122.4194

# 四个生命线：0=用户 1=Host 2=Client 3=Server
USER, HOST, CLIENT, SERVER = 0, 1, 2, 3

LIFELINES = [
    {"name": "用户", "sub": "User"},
    {"name": "MCP Host", "sub": "宿主 · Claude Code"},
    {"name": "MCP Client", "sub": "客户端"},
    {"name": "MCP Server", "sub": "weather 服务器"},
]


class McpClient:
    """极简 MCP stdio 客户端：一行行写/读 JSON-RPC。"""

    def __init__(self, cmd: list[str]):
        self._seq = 0
        self._t0 = time.perf_counter()
        self.proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8",
        )
        # 服务器把 HTTP 日志打到 stderr，起线程吸走避免缓冲塞满
        self._stderr = threading.Thread(target=self._drain_stderr, daemon=True)
        self._stderr.start()

    def _drain_stderr(self):
        for _line in self.proc.stderr:
            pass

    def _now(self) -> float:
        return round((time.perf_counter() - self._t0) * 1000, 1)

    def _send(self, msg: dict):
        self.proc.stdin.write(json.dumps(msg, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()

    def _mk(self, kind: str, frm: int, to: int, label: str, desc: str,
            payload: dict, method: str = "", msg_id=None) -> dict:
        return {
            "kind": kind, "from": frm, "to": to, "label": label, "desc": desc,
            "payload": payload, "method": method, "id": msg_id, "t": self._now(),
        }

    def exchange(self, method: str, params: dict, label: str, desc: str):
        """发一个请求并等待同 id 的响应，返回 (请求事件, 响应事件)。"""
        self._seq += 1
        mid = self._seq
        msg = {"jsonrpc": "2.0", "id": mid, "method": method, "params": params}
        req_ev = self._mk("request", CLIENT, SERVER, label, desc, msg, method, mid)
        self._send(msg)
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("服务器提前关闭了 stdout（进程可能崩溃）")
            resp = json.loads(line)
            if resp.get("id") == mid:
                resp_ev = self._mk("response", SERVER, CLIENT, f"{label} · 结果",
                                   f"服务器对「{label}」的回应。", resp, method, mid)
                return req_ev, resp_ev, resp.get("result", {})

    def notify(self, method: str, params: dict, label: str, desc: str):
        """发一个通知（无 id，无响应）。"""
        msg = {"jsonrpc": "2.0", "method": method, "params": params}
        return self._mk("notification", CLIENT, SERVER, label, desc, msg, method)

    def close(self):
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.terminate()
        except Exception:
            pass


# ---- 合成事件（应用层 / 系统 / 阶段分隔）----

def app_event(frm: int, to: int, label: str, desc: str, payload) -> dict:
    return {"kind": "app", "from": frm, "to": to, "label": label, "desc": desc,
            "payload": payload if isinstance(payload, dict) else {"内容": payload},
            "method": "", "id": None, "t": None}


def system_event(label: str, desc: str, payload=None) -> dict:
    return {"kind": "system", "from": None, "to": None, "label": label, "desc": desc,
            "payload": payload if isinstance(payload, dict) else {"说明": payload or ""},
            "method": "", "id": None, "t": None}


def phase_event(label: str) -> dict:
    return {"kind": "phase", "from": None, "to": None, "label": label, "desc": "",
            "payload": {}, "method": "", "id": None, "t": None}


def extract_tool_text(result: dict) -> str:
    """从 tools/call 的 result 里抠出文本（MCP 2.0 的 content 结构）。"""
    for c in result.get("content", []) if isinstance(result, dict) else []:
        if isinstance(c, dict) and c.get("type") == "text":
            return c.get("text", "")
    sc = result.get("structuredContent") if isinstance(result, dict) else None
    if isinstance(sc, str):
        return sc
    return str(result)


def run_demo() -> list[dict]:
    """真实走一遍完整流程，返回按时间排好序的事件列表。"""
    events: list[dict] = []

    # ---------- 阶段一：建立连接（启动时，一次性） ----------
    events.append(system_event(
        "Host 启动天气服务器",
        "Claude Code（Host）启动时，按配置把 weather MCP 服务器作为子进程跑起来。",
        {"command": SERVER_CMD[0], "args": SERVER_CMD[1:]},
    ))

    client = McpClient(SERVER_CMD)

    req, resp, _ = client.exchange(
        "initialize",
        {"protocolVersion": "2024-11-05", "capabilities": {},
         "clientInfo": {"name": "Claude Code", "version": "1.0"}},
        label="initialize",
        desc="MCP 握手：Client 报身份、协商协议版本、声明能力。这是双方说的第一句话。",
    )
    events += [req, resp]

    events.append(client.notify(
        "notifications/initialized", {},
        label="initialized",
        desc="通知：Client 告诉 Server「初始化完成，可以干活了」。通知没有 id，Server 不回话。",
    ))

    req, resp, tool_result = client.exchange(
        "tools/list", {},
        label="tools/list",
        desc="工具发现：Client 问「你有哪些工具？」，Server 返回工具名和参数规范（schema）。",
    )
    events += [req, resp]
    tool_names = [t.get("name") for t in tool_result.get("tools", [])]

    events.append(system_event(
        "Host 把工具登记给 LLM",
        "Host 拿到工具列表后，把「有 get_alerts、get_forecast 两个工具可用」这件事告诉 LLM。"
        "以后 LLM 就能在需要时选择调用它们。",
        {"可用工具": tool_names},
    ))

    # ---------- 阶段二：用户提问（每次都会发生） ----------
    events.append(phase_event("阶段二 · 用户提问（每次对话都会发生）"))

    events.append(app_event(
        USER, HOST, "💬 提问",
        f"用户在 Claude Code 里输入：{DEMO_QUESTION}",
        {"用户输入": DEMO_QUESTION},
    ))

    events.append(system_event(
        "🤖 LLM 分析意图",
        "LLM 判断：这个问题需要实时天气数据，自己没有，但有个 get_forecast 工具能查。"
        f"于是决定调用它，参数取 {DEMO_CITY} 的坐标 ({DEMO_LAT}, {DEMO_LON})。",
        {"决策": "调用工具", "工具": "get_forecast", "参数": {"latitude": DEMO_LAT, "longitude": DEMO_LON}},
    ))

    events.append(app_event(
        HOST, CLIENT, "指示调用 get_forecast",
        "Host 把 LLM 的意图转成指令，交给 MCP Client 去执行（这一步是应用内部，不属于 MCP）。",
        {"指令": "调用 get_forecast", "参数": {"latitude": DEMO_LAT, "longitude": DEMO_LON}},
    ))

    req, resp, forecast_result = client.exchange(
        "tools/call",
        {"name": "get_forecast", "arguments": {"latitude": DEMO_LAT, "longitude": DEMO_LON}},
        label="tools/call · get_forecast",
        desc=f"真正的 MCP 调用：Client 请求执行 get_forecast，查 {DEMO_CITY} 的预报。"
             "Server 内部会去调用 weather.gov 的 API。",
    )
    events += [req, resp]

    forecast_text = extract_tool_text(forecast_result)
    events.append(app_event(
        CLIENT, HOST, "工具结果回传",
        "Client 把 Server 返回的预报数据原样交回给 Host（也是应用内部）。",
        {"预报数据(截取)": forecast_text[:300]},
    ))

    events.append(system_event(
        "🤖 LLM 生成回答",
        "LLM 拿到预报数据后，把它整理成一句自然语言，准备回复用户。",
        {"示意回答": f"{DEMO_CITY}接下来天气如下：\n" + forecast_text[:200]},
    ))

    events.append(app_event(
        HOST, USER, "回答用户",
        "Host 把 LLM 生成的回答显示给用户。至此一次完整的工具调用闭环结束。",
        {"最终回答(示意)": forecast_text[:300]},
    ))

    client.close()
    return events


# ======================================================================
#  下面是生成 HTML 时序图的部分
# ======================================================================

def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_diagram_svg(events: list[dict]) -> str:
    """把事件渲染成四生命线的 SVG 时序图。"""
    X = [130, 400, 680, 950]   # 四条生命线的 x 坐标
    W = 1120
    TOP, STEP, SYS_STEP = 150, 96, 46

    # 先算每行 y
    rows = []
    y = TOP
    for ev in events:
        rows.append((ev, y))
        if ev["kind"] in ("system", "phase"):
            y += SYS_STEP
        else:
            y += STEP
    H = y + 30

    parts = [f'<svg viewBox="0 0 {W} {H}" class="diagram" role="img" aria-label="MCP 四角色时序图">']
    parts.append("<defs>")
    parts.append(
        '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto">'
        '<path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker>'
    )
    parts.append("</defs>")

    # 四个参与者框
    for i, lf in enumerate(LIFELINES):
        cx = X[i]
        parts.append(f'<text x="{cx}" y="54" class="actor-name" text-anchor="middle">{_esc(lf["name"])}</text>')
        parts.append(f'<rect x="{cx-75}" y="66" width="150" height="34" rx="8" class="actor-box"/>')
        parts.append(f'<text x="{cx}" y="88" class="actor-role" text-anchor="middle">{_esc(lf["sub"])}</text>')
        parts.append(f'<line x1="{cx}" y1="112" x2="{cx}" y2="{H-16}" class="lifeline"/>')

    for i, (ev, y) in enumerate(rows):
        kind = ev["kind"]

        if kind == "system":
            parts.append(
                f'<g class="msg sys" data-idx="{i}" transform="translate(0,{y-16})">'
                f'<rect x="40" y="0" width="{W-80}" height="28" rx="14" class="sys-pill"/>'
                f'<text x="{W/2}" y="19" class="sys-text" text-anchor="middle">⚙ {_esc(ev["label"])}</text>'
                f'</g>'
            )
            continue

        if kind == "phase":
            parts.append(
                f'<g class="msg phase" data-idx="{i}" transform="translate(0,{y-14})">'
                f'<line x1="40" y1="14" x2="{W-40}" y2="14" class="phase-line"/>'
                f'<rect x="{W/2-200}" y="2" width="400" height="24" rx="12" class="phase-pill"/>'
                f'<text x="{W/2}" y="18" class="phase-text" text-anchor="middle">{_esc(ev["label"])}</text>'
                f'</g>'
            )
            continue

        fx, tx = X[ev["from"]], X[ev["to"]]
        cls = kind  # request / response / notification / app
        parts.append(f'<g class="msg {cls}" data-idx="{i}" style="animation-delay:{i*60}ms">')
        parts.append(f'<line x1="{fx}" y1="{y}" x2="{tx}" y2="{y}" class="arrow {cls}" marker-end="url(#arrow)"/>')

        # 数据流向动画（MCP 请求/响应才有）
        if kind in ("request", "response"):
            direction = "flow-right" if fx < tx else "flow-left"
            parts.append(f'<line x1="{fx}" y1="{y}" x2="{tx}" y2="{y}" class="flow {cls} {direction}"/>')

        mid = (fx + tx) / 2
        parts.append(f'<circle cx="{mid}" cy="{y}" r="11" class="halo {cls}"/>')
        parts.append(f'<text x="{mid}" y="{y-10}" class="msg-label" text-anchor="middle">{_esc(ev["label"])}</text>')
        parts.append(f'<circle cx="{mid}" cy="{y}" r="4" class="dot {cls}"/>')
        parts.append("</g>")

    parts.append("</svg>")
    return "".join(parts)


def build_steps_html(events: list[dict]) -> str:
    kind_cn = {
        "system": "系统", "phase": "阶段", "request": "MCP 请求 →",
        "response": "MCP 响应 ←", "notification": "MCP 通知", "app": "应用层",
    }
    out = []
    for i, ev in enumerate(events):
        out.append(
            f'<div class="step" data-idx="{i}" style="animation-delay:{i*50}ms">'
            f'<span class="step-idx">{i}</span>'
            f'<span class="step-tag tag-{ev["kind"]}">{kind_cn.get(ev["kind"], ev["kind"])}</span>'
            f'<div class="step-body"><div class="step-title">{_esc(ev["label"])}</div>'
            f'<div class="step-desc">{_esc(ev["desc"])}</div></div>'
            f'</div>'
        )
    return "".join(out)


def build_html(events: list[dict]) -> str:
    diagram = build_diagram_svg(events)
    steps = build_steps_html(events)
    events_json = json.dumps(events, ensure_ascii=False)
    return HTML_TEMPLATE.replace("__DIAGRAM__", diagram) \
                        .replace("__STEPS__", steps) \
                        .replace("__EVENTS__", events_json)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Weather MCP 工作过程可视化（四角色）</title>
<style>
  :root {
    color-scheme: light;
    --surface:   #fcfcfb;
    --page:      #f9f9f7;
    --ink:       #0b0b0b;
    --ink-2:     #52514e;
    --muted:     #898781;
    --grid:      #e1e0d9;
    --baseline:  #c3c2b7;
    --border:    rgba(11,11,11,0.10);
    --req:       #2a78d6;   /* MCP 请求：蓝 */
    --resp:      #1baf7a;   /* MCP 响应：青绿 */
    --notif:     #eb6834;   /* MCP 通知：橙 */
    --app:       #4a3aa7;   /* 应用层：紫 */
    --sys:       #898781;
    --req-bg:    #eef4fc;
    --resp-bg:   #e9f7f1;
    --notif-bg:  #fdf1ea;
    --app-bg:    #eeeafb;
    --sys-bg:    #f0efec;
  }
  @media (prefers-color-scheme: dark) {
    :root:where(:not([data-theme="light"])) {
      color-scheme: dark;
      --surface:   #1a1a19;
      --page:      #0d0d0d;
      --ink:       #ffffff;
      --ink-2:     #c3c2b7;
      --muted:     #898781;
      --grid:      #2c2c2a;
      --baseline:  #383835;
      --border:    rgba(255,255,255,0.10);
      --req:       #3987e5;
      --resp:      #199e70;
      --notif:     #d95926;
      --app:       #9085e9;
      --sys:       #898781;
      --req-bg:    #1c2a3a;
      --resp-bg:   #14291f;
      --notif-bg:  #322118;
      --app-bg:    #26223d;
      --sys-bg:    #2a2a28;
    }
  }
  :root[data-theme="dark"] {
    color-scheme: dark;
    --surface:   #1a1a19;
    --page:      #0d0d0d;
    --ink:       #ffffff;
    --ink-2:     #c3c2b7;
    --muted:     #898781;
    --grid:      #2c2c2a;
    --baseline:  #383835;
    --border:    rgba(255,255,255,0.10);
    --req:       #3987e5;
    --resp:      #199e70;
    --notif:     #d95926;
    --app:       #9085e9;
    --sys:       #898781;
    --req-bg:    #1c2a3a;
    --resp-bg:   #14291f;
    --notif-bg:  #322118;
    --app-bg:    #26223d;
    --sys-bg:    #2a2a28;
  }

  * { box-sizing: border-box; }
  body { margin: 0; background: var(--page); color: var(--ink);
         font-family: system-ui, -apple-system, "Segoe UI", sans-serif; line-height: 1.6; }
  .wrap { max-width: 1140px; margin: 0 auto; padding: 40px 24px 80px; }
  h1 { font-size: 26px; margin: 0 0 6px; }
  .sub { color: var(--ink-2); margin: 0 0 28px; }
  .card { background: var(--surface); border: 1px solid var(--border);
          border-radius: 14px; padding: 20px; margin-bottom: 24px; }
  .card.diagram-card { overflow-x: auto; }

  .legend { display: flex; gap: 16px; flex-wrap: wrap; align-items: center; }
  .legend span { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: var(--ink-2); }
  .sw { width: 22px; height: 3px; border-radius: 2px; }
  .sw.request { background: var(--req); }
  .sw.response { background: var(--resp); }
  .sw.notification { background: var(--notif); background-image: repeating-linear-gradient(90deg, transparent 0 3px, var(--page) 3px 5px); }
  .sw.app { background: var(--app); background-image: repeating-linear-gradient(90deg, transparent 0 3px, var(--page) 3px 5px); }
  .sw.system { background: var(--sys); }

  .toolbar { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-bottom: 12px; }
  button { font: inherit; font-size: 13px; cursor: pointer; border: 1px solid var(--border);
           background: var(--surface); color: var(--ink); border-radius: 8px; padding: 6px 12px; }
  button:hover { border-color: var(--muted); }
  button.primary { background: var(--req); color: #fff; border-color: var(--req); }
  button.ghost { margin-left: auto; }

  .diagram { width: 100%; height: auto; display: block; min-width: 900px; }
  .lifeline { stroke: var(--baseline); stroke-width: 2; }
  .actor-name { font-size: 14px; font-weight: 600; fill: var(--ink); }
  .actor-role { font-size: 11px; fill: var(--ink-2); }
  .actor-box { fill: var(--surface); stroke: var(--baseline); stroke-width: 1.5; }
  .arrow { stroke-width: 2.5; transition: stroke-width .15s ease; }
  .arrow.request { stroke: var(--req); }
  .arrow.response { stroke: var(--resp); }
  .arrow.notification { stroke: var(--notif); stroke-dasharray: 6 5; }
  .arrow.app { stroke: var(--app); stroke-dasharray: 6 5; }
  .dot { fill: var(--surface); stroke-width: 2; }
  .dot.request { stroke: var(--req); }
  .dot.response { stroke: var(--resp); }
  .dot.notification { stroke: var(--notif); }
  .dot.app { stroke: var(--app); }
  .msg-label { font-size: 13px; fill: var(--ink); }
  .msg { cursor: pointer; }
  .msg.sys, .msg.phase { cursor: default; }
  .sys-pill { fill: var(--sys-bg); }
  .sys-text { font-size: 13px; fill: var(--ink-2); }
  .phase-line { stroke: var(--baseline); stroke-width: 1; stroke-dasharray: 4 6; }
  .phase-pill { fill: var(--req-bg); stroke: var(--req); stroke-width: 1; }
  .phase-text { font-size: 13px; fill: var(--req); font-weight: 600; }
  .msg.active .arrow { stroke-width: 4; }

  /* ---- 动态效果 ---- */
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
  @keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
  .msg  { animation: fadeIn .45s ease both; }
  .step { animation: fadeUp .45s ease both; }
  .flow { fill: none; stroke-width: 2.5; stroke-linecap: round; stroke-dasharray: 3 11; opacity: .6; }
  .flow.request  { stroke: var(--req); }
  .flow.response { stroke: var(--resp); }
  .flow.flow-right { animation: flowRight 1.1s linear infinite; }
  .flow.flow-left  { animation: flowLeft  1.1s linear infinite; }
  @keyframes flowRight { to { stroke-dashoffset: -14; } }
  @keyframes flowLeft  { to { stroke-dashoffset:  14; } }
  .halo { fill: none; stroke-width: 2; opacity: 0; }
  .halo.request { stroke: var(--req); }
  .halo.response { stroke: var(--resp); }
  .halo.notification { stroke: var(--notif); }
  .halo.app { stroke: var(--app); }
  .msg.active .halo { animation: haloPulse 1.1s ease-in-out infinite; }
  @keyframes haloPulse { 0%, 100% { opacity: 0; } 50% { opacity: .45; } }

  .detail { min-height: 120px; }
  .detail h3 { margin: 0 0 6px; font-size: 15px; }
  .kind-badge { font-size: 12px; color: var(--ink-2); }
  .detail .desc { color: var(--ink-2); font-size: 14px; margin-bottom: 12px; }
  pre { background: var(--page); border: 1px solid var(--border); border-radius: 10px;
        padding: 14px; overflow-x: auto; font-size: 12.5px; line-height: 1.5;
        font-family: ui-monospace, "Cascadia Code", Consolas, monospace; margin: 0; }
  .k { color: var(--req); }
  .s { color: var(--resp); }
  .n { color: var(--notif); }

  .step { display: flex; gap: 12px; padding: 12px 4px; border-bottom: 1px solid var(--grid); align-items: flex-start; }
  .step:last-child { border-bottom: none; }
  .step-idx { width: 26px; height: 26px; border-radius: 50%; background: var(--sys-bg); color: var(--ink-2);
              display: inline-flex; align-items: center; justify-content: center; font-size: 12px; flex: none; }
  .step-tag { font-size: 11px; padding: 2px 8px; border-radius: 10px; flex: none; margin-top: 3px; }
  .tag-request { background: var(--req-bg); color: var(--req); }
  .tag-response { background: var(--resp-bg); color: var(--resp); }
  .tag-notification { background: var(--notif-bg); color: var(--notif); }
  .tag-app { background: var(--app-bg); color: var(--app); }
  .tag-system, .tag-phase { background: var(--sys-bg); color: var(--ink-2); }
  .step-title { font-weight: 600; font-size: 14px; }
  .step-desc { color: var(--ink-2); font-size: 13px; }
  .step.active { background: var(--req-bg); border-radius: 8px; }
</style>
</head>
<body>
<div class="wrap">
  <h1>🌤 Weather MCP 四角色工作过程</h1>
  <p class="sub">一个真实例子：用户在 Claude Code 里问「旧金山现在天气怎么样？」。点任意箭头看完整消息。</p>

  <div class="card diagram-card">
    <div class="toolbar">
      <div class="legend">
        <span><i class="sw request"></i>MCP 请求（Client→Server）</span>
        <span><i class="sw response"></i>MCP 响应（Server→Client）</span>
        <span><i class="sw notification"></i>MCP 通知</span>
        <span><i class="sw app"></i>应用层消息（非 MCP）</span>
        <span><i class="sw system"></i>系统/内部</span>
      </div>
      <button class="ghost" id="themeBtn" onclick="toggleTheme()">🌙 深色</button>
    </div>
    <div class="toolbar">
      <button onclick="step(-1)">◀ 上一步</button>
      <button class="primary" onclick="play()" id="playBtn">▶ 自动播放</button>
      <button onclick="step(1)">下一步 ▶</button>
      <span id="stepCounter" style="font-size:13px;color:var(--ink-2)"></span>
    </div>
    __DIAGRAM__
  </div>

  <div class="card detail" id="detail">
    <h3>👆 点击上面的箭头查看消息详情</h3>
    <div class="desc">这里会显示那条消息的完整 JSON 和解释。</div>
  </div>

  <div class="card">
    <h3 style="margin:0 0 4px">📖 四角色是怎么分工的</h3>
    <p style="margin:0 0 12px;color:var(--ink-2);font-size:13px">
      <b>用户</b>只说人话；<b>MCP Host</b> 是那个 AI 应用（Claude Code），里面跑着 LLM；
      <b>MCP Client</b> 负责和服务器「说 MCP 协议」；<b>MCP Server</b> 是真正干活的工具。
      关键点：<b>MCP 协议（蓝/青绿/橙色的线）只出现在 Client ⇄ Server 之间</b>，
      用户 ⇄ Host ⇄ Client 那几段（紫色虚线）是应用自己内部的事，不属于 MCP。
      （在 Claude Code 里，Host 和 Client 常常打包在一起，但概念上它们是两个角色。）
    </p>
    <div id="steps">__STEPS__</div>
  </div>
</div>

<script>
  const EVENTS = __EVENTS__;
  let current = -1;
  let timer = null;

  function toggleTheme() {
    const cur = document.documentElement.getAttribute('data-theme');
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    document.getElementById('themeBtn').textContent = next === 'dark' ? '☀️ 浅色' : '🌙 深色';
  }
  function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function highlight(json) {
    let s = JSON.stringify(json, null, 2);
    s = esc(s);
    s = s.replace(/(&quot;.*?&quot;)(\s*:)/g, '<span class="k">$1</span>$2');
    s = s.replace(/: (&quot;.*?&quot;)/g, ': <span class="s">$1</span>');
    s = s.replace(/: (-?\d+(\.\d+)?)/g, ': <span class="n">$1</span>');
    return s;
  }
  function show(i) {
    if (i < 0 || i >= EVENTS.length) return;
    current = i;
    document.querySelectorAll('.msg').forEach((el, idx) => el.classList.toggle('active', idx === i));
    document.querySelectorAll('.step').forEach((el, idx) => el.classList.toggle('active', idx === i));
    const ev = EVENTS[i];
    const kindC = {request:'MCP 请求', response:'MCP 响应', notification:'MCP 通知',
                   app:'应用层', system:'系统', phase:'阶段'}[ev.kind] || ev.kind;
    const detail = document.getElementById('detail');
    detail.innerHTML =
      '<h3>' + esc(ev.label) + ' <span class="kind-badge">(' + kindC + ')</span></h3>' +
      '<div class="desc">' + esc(ev.desc) + '</div>' +
      '<pre>' + highlight(ev.payload) + '</pre>';
    detail.style.animation = 'none';
    void detail.offsetWidth;
    detail.style.animation = 'fadeUp .3s ease';
    document.getElementById('stepCounter').textContent = (i + 1) + ' / ' + EVENTS.length;
  }
  function step(d) { show(current + d); }
  function play() {
    if (timer) { clearInterval(timer); timer = null; document.getElementById('playBtn').textContent = '▶ 自动播放'; return; }
    document.getElementById('playBtn').textContent = '⏸ 暂停';
    show(current < 0 ? 0 : current);
    timer = setInterval(function () {
      if (current >= EVENTS.length - 1) { clearInterval(timer); timer = null; document.getElementById('playBtn').textContent = '▶ 自动播放'; return; }
      show(current + 1);
    }, 1500);
  }
  document.querySelectorAll('.msg').forEach(el => el.addEventListener('click', () => show(parseInt(el.dataset.idx, 10))));
  document.querySelectorAll('.step').forEach(el => el.addEventListener('click', () => show(parseInt(el.dataset.idx, 10))));
  show(0);
</script>
</body>
</html>
"""


def print_terminal_summary(events: list[dict]):
    print("\n======== Weather MCP 四角色工作过程 ========\n")
    names = [lf["name"] for lf in LIFELINES]
    for i, ev in enumerate(events):
        if ev["kind"] in ("system", "phase"):
            print(f"[{i:02d}]   ⚙  {ev['label']}")
        else:
            frm = names[ev["from"]]
            to = names[ev["to"]]
            print(f"[{i:02d}] {frm} → {to}  ·  {ev['label']}")
        print(f"      {ev['desc']}")
    print("\n已生成可视化文件:", OUTPUT_HTML)


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    events = run_demo()
    html = build_html(events)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print_terminal_summary(events)


if __name__ == "__main__":
    main()
