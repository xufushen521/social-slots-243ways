from __future__ import annotations

from pathlib import Path

import streamlit as st

from engine.feature import merge_sticky, scatter_positions
from engine.loader import list_presets, load_config
from engine.math_model import base_metrics
from engine.reels import draw_grid
from engine.ways import count_symbol, evaluate_ways


START_BALANCE = 1000.0

st.set_page_config(page_title="243 Ways Social", page_icon="🎰", layout="wide")


def fresh_feature() -> dict:
    return {
        "active": False,
        "kind": None,
        "left": 0,
        "multiplier": 1.0,
        "sticky": {},
        "total_awarded": 0,
        "win": 0.0,
    }


def ready_result(preset: dict) -> dict:
    grid = draw_grid(preset)
    scatter = preset.get("scatter", {})
    sc1 = count_symbol(grid, scatter["respins"]["symbol"]) if "respins" in scatter else 0
    sc2 = count_symbol(grid, scatter["free_spins"]["symbol"]) if "free_spins" in scatter else 0
    return {
        "kind": "ready",
        "grid": grid,
        "ways_wins": [],
        "win": 0.0,
        "sc1": sc1,
        "sc2": sc2,
        "message": "按 Spin 开始。",
    }


def capped(win: float, preset: dict, bet: float) -> float:
    return min(win, preset.get("max_win", 5000) * bet)


def do_base_spin(preset: dict, bet: float) -> None:
    if st.session_state.balance < bet:
        return

    st.session_state.balance -= bet
    grid = draw_grid(preset)
    wins = evaluate_ways(grid, preset, bet)
    win = capped(sum(item["win"] for item in wins), preset, bet)
    st.session_state.balance += win

    scatter = preset.get("scatter", {})
    respins = scatter.get("respins")
    free_spins = scatter.get("free_spins")
    sc1 = count_symbol(grid, respins["symbol"]) if respins else 0
    sc2 = count_symbol(grid, free_spins["symbol"]) if free_spins else 0

    feature = fresh_feature()
    message = "本次没有中奖。" if win == 0 else f"本次中奖 {win:.2f}。"

    if free_spins and sc2 >= free_spins["min_count"]:
        feature.update(
            {
                "active": True,
                "kind": "free",
                "left": free_spins["spins"],
                "multiplier": free_spins["multiplier"],
                "total_awarded": free_spins["spins"],
            }
        )
        message = f"{sc2} 个 SC2：进入 {free_spins['spins']} 次 Free Spin。"
    elif respins and sc1 >= respins["min_count"]:
        awarded = min(respins["awards"]["3"], respins["max_respins"])
        feature.update(
            {
                "active": True,
                "kind": "respin",
                "left": awarded,
                "multiplier": 1.0,
                "total_awarded": awarded,
                "sticky": scatter_positions(grid, respins["symbol"]),
            }
        )
        message = f"{sc1} 个 SC1：进入 {awarded} 次 Respin。"

    st.session_state.feature = feature
    st.session_state.result = {
        "kind": "base",
        "grid": grid,
        "ways_wins": wins,
        "win": win,
        "sc1": sc1,
        "sc2": sc2,
        "message": message,
    }


def do_feature_spin(preset: dict, bet: float) -> None:
    feature = st.session_state.feature
    if not feature["active"] or feature["left"] <= 0:
        return

    grid = draw_grid(
        preset,
        sticky=feature["sticky"] if feature["kind"] == "respin" else None,
    )
    wins = evaluate_ways(grid, preset, bet)
    multiplier = feature["multiplier"]
    win = capped(sum(item["win"] for item in wins) * multiplier, preset, bet)
    for item in wins:
        item["win"] *= multiplier

    st.session_state.balance += win
    feature["win"] += win
    scatter = preset.get("scatter", {})

    if feature["kind"] == "respin":
        block = scatter["respins"]
        sticky, new_count = merge_sticky(feature["sticky"], grid, block["symbol"])
        feature["sticky"] = sticky
        add = 0
        if new_count:
            room = block["max_respins"] - feature["total_awarded"]
            add = min(block["retrigger_add"], room)
            feature["total_awarded"] += add
        feature["left"] = feature["left"] - 1 + add
        message = f"Respin 中奖 {win:.2f}，新 SC1 {new_count} 个"
        if add:
            message += f"，续 {add} 次"
        message += "。"
    else:
        feature["left"] -= 1
        message = f"Free Spin 中奖 {win:.2f}（x{multiplier:.1f}），剩余 {feature['left']} 次。"

    if feature["left"] <= 0 or feature["win"] >= preset.get("max_win", 5000) * bet:
        feature["active"] = False
        message += f" Feature 结束，累计 {feature['win']:.2f}。"

    st.session_state.feature = feature
    st.session_state.result = {
        "kind": feature["kind"],
        "grid": grid,
        "ways_wins": wins,
        "win": win,
        "sc1": count_symbol(grid, scatter["respins"]["symbol"]) if "respins" in scatter else 0,
        "sc2": count_symbol(grid, scatter["free_spins"]["symbol"]) if "free_spins" in scatter else 0,
        "message": message,
    }


def do_feature_buy(preset: dict, bet: float) -> None:
    buy = preset.get("feature_buy")
    free_spins = preset.get("scatter", {}).get("free_spins")
    if not buy or not free_spins:
        return
    cost = bet * buy["cost_multiplier"]
    if st.session_state.balance < cost:
        return

    st.session_state.balance -= cost
    feature = fresh_feature()
    feature.update(
        {
            "active": True,
            "kind": "free",
            "left": free_spins["spins"],
            "multiplier": free_spins["multiplier"],
            "total_awarded": free_spins["spins"],
        }
    )
    st.session_state.feature = feature
    st.session_state.result = {
        "kind": "buy",
        "grid": draw_grid(preset),
        "ways_wins": [],
        "win": 0.0,
        "sc1": 0,
        "sc2": 0,
        "message": f"购买 Free Spin：花费 {cost:.2f}，进入 {free_spins['spins']} 次 Free Spin。",
    }


def render_grid(grid: list[list[str]], winning_symbols: set[str]) -> None:
    cells = ["<table style='border-collapse:separate;border-spacing:8px;margin:0 auto;'>"]
    for row in range(len(grid[0])):
        cells.append("<tr>")
        for reel in grid:
            symbol = reel[row]
            if symbol == "SC1":
                bg = "#93c5fd"
            elif symbol == "SC2":
                bg = "#fcd34d"
            else:
                bg = "#e5e7eb"
            border = "3px solid #16a34a" if symbol in winning_symbols else "1px solid #cbd5e1"
            cells.append(
                "<td style='width:74px;height:74px;text-align:center;"
                "vertical-align:middle;font-size:24px;font-weight:700;"
                f"background:{bg};color:#111827;border:{border};border-radius:12px;'>{symbol}</td>"
            )
        cells.append("</tr>")
    cells.append("</table>")
    st.markdown("".join(cells), unsafe_allow_html=True)


config_path = Path(__file__).with_name("config.json")
try:
    config = load_config(config_path)
except Exception as exc:
    st.error(f"配置读取失败：{exc}")
    st.stop()

presets = list_presets(config)
preset_name = st.sidebar.selectbox(
    "预设",
    presets,
    index=presets.index(config["default_preset"]),
)
preset = config["presets"][preset_name]

if st.session_state.get("active_preset") != preset_name:
    st.session_state.active_preset = preset_name
    st.session_state.balance = START_BALANCE
    st.session_state.bet = preset["bet"]["default"]
    st.session_state.feature = fresh_feature()
    st.session_state.result = ready_result(preset)

feature = st.session_state.feature
bet_options = preset["bet"]["levels"]
bet = st.sidebar.selectbox(
    "总下注",
    bet_options,
    index=bet_options.index(st.session_state.bet),
    format_func=lambda value: f"{value:.2f}",
    disabled=feature["active"],
)
st.session_state.bet = bet

if st.sidebar.button("重置余额"):
    st.session_state.balance = START_BALANCE
    st.session_state.feature = fresh_feature()
    st.session_state.result = ready_result(preset)
    st.rerun()

buy = preset.get("feature_buy")
if buy and not feature["active"]:
    buy_cost = bet * buy["cost_multiplier"]
    if st.sidebar.button(
        f"Feature Buy（{buy_cost:.2f}）",
        disabled=st.session_state.balance < buy_cost,
    ):
        do_feature_buy(preset, bet)
        st.rerun()
    st.sidebar.caption(f"买价 {buy['cost_multiplier']:.1f}x 总下注")

summary = preset.get("math_summary", {})
st.sidebar.metric("设计 RTP", f"{summary.get('total_rtp', 0):.2%}")

st.title("243 Ways Social")
st.caption(f"{preset_name} · 5×3 · 243 ways · Max Win {preset['max_win']}x")

feature = st.session_state.feature
metrics = st.columns(4)
metrics[0].metric("余额", f"{st.session_state.balance:.2f}")
metrics[1].metric("总下注", f"{bet:.2f}")
metrics[2].metric("本次中奖", f"{st.session_state.result['win']:.2f}")
if feature["active"]:
    label = "Free Spin" if feature["kind"] == "free" else "Respin"
    feature_status = f"{label} · {feature['left']} 次"
else:
    feature_status = "无"
metrics[3].metric("Feature", feature_status)

can_spin = feature["active"] or st.session_state.balance >= bet
if feature["active"]:
    button_label = f"{'Free Spin' if feature['kind'] == 'free' else 'Respin'}（剩 {feature['left']} 次）"
else:
    button_label = f"Spin（{bet:.2f}）"

if st.button(button_label, type="primary", use_container_width=True, disabled=not can_spin):
    if feature["active"]:
        do_feature_spin(preset, bet)
    else:
        do_base_spin(preset, bet)
    st.rerun()

if not can_spin:
    st.warning("余额不足，点左侧「重置余额」。")

result = st.session_state.result
st.subheader("本次结果")
if result["kind"] in {"free", "respin", "buy"}:
    st.info(result["message"])
elif result["win"] > 0:
    st.success(result["message"])
else:
    st.caption(result["message"])

winning_symbols = {item["symbol"] for item in result["ways_wins"]}
render_grid(result["grid"], winning_symbols)
st.caption("灰色 = 普通  |  蓝色 = SC1 Respin  |  黄色 = SC2 Free Spin  |  绿框 = 中奖")

if result["ways_wins"]:
    st.dataframe(
        [
            {
                "符号": item["symbol"],
                "连数": item["match"],
                "Ways": item["ways"],
                "赔率": item["pay"],
                "赢": item["win"],
            }
            for item in result["ways_wins"]
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.caption("普通 ways 中奖：无")

st.caption(f"SC1：{result['sc1']} 个  |  SC2：{result['sc2']} 个")

with st.expander("RTP 摘要（面试可讲）"):
    exact = base_metrics(preset)
    st.write(f"精确 base ways RTP：{exact['ways_rtp']:.2%}")
    st.write(f"Feature 贡献：{summary.get('feature_rtp', 0):.2%}")
    st.write(f"设计总 RTP：{summary.get('total_rtp', 0):.2%}")
    st.write(f"1M hit rate：{summary.get('hit_rate', 0):.2%}")
    st.write(f"1M SD：{summary.get('sd', 0):.3f}")
    st.write(f"1M 最大观察值：{summary.get('max_win_observed', 0):.2f}x")
    if summary.get("feature_buy_rtp"):
        st.write(
            f"Feature Buy：{preset['feature_buy']['cost_multiplier']:.1f}x，"
            f"RTP {summary['feature_buy_rtp']:.2%}"
        )
