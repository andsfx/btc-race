# btc-race

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/andsfx/btc-race/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/andsfx/btc-race/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

A 1-minute trend-following bot for Coinbase Wrapped BTC (cbBTC) on the make.fun
bars-replay harness. It reads one OHVLC bar per minute from an Orca Whirlpool
cbBTC/USDC pool and answers buy/sell orders. Long only, one full-size position,
deterministic (no clock, env or randomness).

Enter the live 24-hour race: https://make.fun/bounty/btc-race-24h-20261117-0603

## Strategy

- Compute the normalized least-squares slope of the last 240 closes.
- Enter long with full cash when the slope is clearly positive (`ENTER`).
- Exit when the slope turns clearly negative (`EXIT`) or price breaks a 0.8%
  trailing stop below its post-entry peak.

## Run

The bot is driven by the harness (Python 3.13, stdlib only):

```sh
python3 -P -s main.py
```

`vendor/makefun_bars.py` is the bars-replay protocol shim from the competition
kit. The bot runs twice per grade; it depends only on the bar stream, so the two
runs are byte-identical.