# btc-race

A 1-minute trend-following bot for Coinbase Wrapped BTC (cbBTC) on the make.fun
bars-replay harness. It reads one OHLCV bar per minute from an Orca Whirlpool
cbBTC/USDC pool and answers with buy/sell orders. Long only, one full-size
position, entirely deterministic (no clock, env or randomness).

## Strategy

- Compute the normalized slope of the last 240 closes.
- Enter long when the slope is clearly positive (`ENTER`).
- Exit when the slope turns clearly negative (`EXIT`) or price breaks a 0.8%
  trailing stop below its post-entry peak.

Tuning constants live at the top of `main.py`.

## Run

The bot is driven by the harness (Python 3.13, stdlib only):

```sh
python3 -P -s main.py
```

`vendor/makefun_bars.py` is the bars-replay protocol shim from the competition
kit. The bot runs twice per grade; both runs must produce byte-identical
orders, and it depends only on the bar stream, so they do.

[owner]: andsfx
[repo]: btc-race