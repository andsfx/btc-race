# cbBTC 1-minute trend follower (agent-fun/bars-replay/v1)
#
# Deterministic long-only strategy. Compute the normalized least-squares slope
# of the last LOOKBACK closes: enter long with full cash when the slope rises
# above ENTER, exit when the slope falls below EXIT or price breaks TRAIL below
# its post-entry peak. Standard library only; depends on the bar stream, never
# on the clock, the environment or randomness.

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYM = None          # the single universe symbol, resolved from hello
LOOKBACK = 240      # closes behind the slope (4 hours of 1-minute bars)
ENTER = 3.2e-5      # normalized slope (fraction per minute) above which we go long
EXIT = -3e-5        # normalized slope below which we exit
TRAIL = 0.008       # 0.8% trailing stop below the post-entry peak
MAX_SLIP = 150      # slippage cap in bps (1.5%)

_closes = []        # raw closes, oldest first
_peak = 0           # best close since entry (raw units)
_in = False         # whether we hold (or just bought) the position


def _slope(y):
    """Normalized least-squares slope: per-bar trend divided by the last close."""
    k = len(y)
    mx = (k - 1) / 2.0
    my = sum(y) / float(k)
    num = sum((i - mx) * (y[i] - my) for i in range(k))
    den = sum((i - mx) ** 2 for i in range(k))
    return (num / den) / float(y[-1])


def on_batch(state, batch):
    global SYM, _peak, _in
    if SYM is None:
        SYM = next(iter(state.symbols))
    c = state.close(SYM)
    if c is None:
        return []          # no bar for the symbol yet
    _closes.append(c)
    if state.warming_up:
        return []          # orders on warm-up bars are rejected

    held = state.positions.get(SYM)
    qty = held.qty if held else 0

    if not _in:
        if len(_closes) < LOOKBACK or state.cash <= 0:
            return []
        if _slope(_closes[-LOOKBACK:]) > ENTER:
            _in = True
            _peak = c
            return [{"side": "buy", "symbol": SYM,
                     "notional_quote_units": state.cash,
                     "max_slippage_bps": MAX_SLIP}]
        return []

    # Holding (or the buy was just rejected -> qty 0).
    if qty <= 0:
        _in = False
        return []
    if c > _peak:
        _peak = c
    if _slope(_closes[-LOOKBACK:]) < EXIT or c < _peak * (1.0 - TRAIL):
        _in = False
        return [{"side": "sell", "symbol": SYM, "qty": qty,
                 "max_slippage_bps": MAX_SLIP}]
    return []


if __name__ == "__main__":
    makefun_bars.run(on_batch)