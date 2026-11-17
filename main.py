# CBBTC 1-minute trend follower (agent-fun/bars-replay/v1)
#
# Strategy: enter long when the normalized slope of the last LOOKBACK closes is
# clearly positive, exit when the slope turns clearly negative or price breaks a
# trailing stop below its post-entry peak. Long only, one full-size position.
#
# Deterministic: depends only on the bar stream; no clock, env or randomness.

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYM = None           # the single universe symbol, resolved from hello
LOOKBACK = 240       # closes behind the slope (4 hours at 1-minute bars)
ENTER = 3e-5         # slope (fraction per minute) above which we go long
EXIT = -3e-5         # slope below which we exit
TRAIL = 0.008        # 0.8% trailing stop from the post-entry peak
MAX_SLIP = 150       # slippage cap in bps (1.5%)

_closes = []
_peak = 0.0
_in = False


def _slope(y):
    k = len(y)
    mx = (k - 1) / 2.0
    my = sum(y) / k
    num = sum((i - mx) * (y[i] - my) for i in range(k))
    den = sum((i - mx) ** 2 for i in range(k))
    return (num / den) / y[-1]


def on_batch(state, batch):
    global SYM, _peak, _in
    if SYM is None:
        SYM = next(iter(state.symbols))
    c = state.close(SYM)
    if c is None:
        return []
    price = c / 1e6  # price_scale 6 -> USDC

    _closes.append(price)
    if state.warming_up:
        return []

    held = state.positions.get(SYM)
    qty = held.qty if held else 0
    if qty > 0:
        _in = True
        if price > _peak:
            _peak = price

    if not _in:
        if len(_closes) < LOOKBACK or state.cash <= 0:
            return []
        if _slope(_closes[-LOOKBACK:]) > ENTER:
            _in = True
            _peak = price
            return [{"side": "buy", "symbol": SYM,
                     "notional_quote_units": state.cash,
                     "max_slippage_bps": MAX_SLIP}]
        return []

    # holding (or the buy was just rejected -> qty 0)
    if qty <= 0:
        _in = False
        return []
    if _slope(_closes[-LOOKBACK:]) < EXIT or price < _peak * (1.0 - TRAIL):
        _in = False
        return [{"side": "sell", "symbol": SYM, "qty": qty,
                 "max_slippage_bps": MAX_SLIP}]
    return []


if __name__ == "__main__":
    makefun_bars.run(on_batch)