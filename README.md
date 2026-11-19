# November 19, 2026 — The Daily Globe

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Irgirival/makefun-news-image-20261119-xxcode2/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Irgirival/makefun-news-image-20261119-xxcode2/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

A one-page newspaper front page summing up the world news of
Thursday, November 19, 2026 — drawn entirely in code.

The lead story is the first-ever three-way summit of Donald Trump,
Xi Jinping and Vladimir Putin in Shenzhen, on the sidelines of the
APEC forum. Also on the page: Ukraine strikes the Crimean Bridge
for the third time in a week, Iran attacks Gulf states after a U.S.
strike on Qeshm Island, the International Court of Justice rules on
the Myanmar Rohingya genocide case, Anthropic prices the biggest
IPO in history at $81.3 billion ahead of its Nasdaq debut as ANT,
the IAEA says North Korea has expanded uranium enrichment, and
Hakeem Jeffries is set to become the first African-American Speaker
of the U.S. House. The ticker adds Voyager 1 nearing one light-day
from Earth, the EU approving its Indonesia trade pact, Australia
sanctioning Israeli settlements, and India–Japan 2+2 defence talks.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` uses only the Python standard library. It renders the front
page with a hand-built 5x7 bitmap font at 2x supersampling, downsamples
it to 1024x1024, and writes a deterministic PNG to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`).

---

<sub>Entered on [make.fun](https://make.fun/?ref=kfz6780b&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
