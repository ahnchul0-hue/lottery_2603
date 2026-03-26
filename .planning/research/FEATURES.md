# Feature Landscape

**Domain:** Lottery number prediction/analysis web application (Korean Lotto 6/45, machine-specific)
**Researched:** 2026-03-26
**Overall Confidence:** MEDIUM-HIGH

## Table Stakes

Features users expect from any lottery analysis tool. Missing any of these and the product feels amateurish or incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Hot/Cold Number Display** | Every lottery tool shows frequently/infrequently drawn numbers. Users immediately look for this. | Low | Straightforward frequency count from `new_res.json`. Display top-10 hot, top-10 cold per machine. |
| **Frequency Distribution Chart** | Bar chart of all 45 numbers and their draw counts is the baseline visualization. Universal across all tools. | Low | Simple bar chart per machine. Recharts or Chart.js. |
| **Number Generation (Multiple Sets)** | Users expect to walk away with actual number sets to play, not just charts. Minimum 5 sets. | Med | PROJECT.md specifies 5 strategies x 5 games = 25 sets. This is generous and good. |
| **Machine Selection (1/2/3)** | Core differentiator concept. Users must pick their machine before analysis. Without this, the app has no identity. | Low | 3-button selector. Filters all data by `호기` field. |
| **Odd/Even Balance Display** | Standard statistical measure shown by every competitor (동행복권 official site, 로또샘, 로또타파). Data already in `홀짝_비율`. | Low | Already pre-computed in dataset. Display distribution per machine. |
| **High/Low Balance Display** | Standard measure. Data already in `고저_비율`. Expected alongside odd/even. | Low | Already pre-computed. Display distribution per machine. |
| **Sum Range Analysis** | Total sum of winning numbers is a standard filter/display. Data already in `총합`. | Low | Already pre-computed. Show distribution histogram per machine. |
| **Clear Disclaimer** | Responsible design. "This is for entertainment/analysis purposes. Lottery draws are random. No guarantees." Required to avoid misleading users. | Low | Static text footer. Non-negotiable. |
| **Recent Draw History** | Users expect to see the raw data: last N draws for their selected machine. Builds trust and context. | Low | Paginated/scrollable table from `lottery_data` filtered by machine. |
| **Responsive Mobile Layout** | Most Korean lottery users check on mobile. Non-responsive = unusable for majority. | Med | React + CSS Grid/Flexbox. Design mobile-first. |

## Differentiators

Features that set this product apart. Not expected by default, but create competitive advantage or unique value.

### Tier 1 Differentiators (High Impact, Aligned with Core Value)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Machine-Specific Analysis (호기별 분석)** | This IS the core differentiator. No major competitor segments analysis by drawing machine. Most apps treat all draws as one pool. Our data shows observable tendencies per machine (1호기: 10, 37, 38 biased; 2호기: 7, 26 biased; 3호기: 35, 15, 43 biased). | Med | Requires per-machine filtering for every analysis. Not technically hard but architecturally pervasive. |
| **Time Decay Weighting** | Most tools use raw frequency (all draws equally weighted). Applying recency weighting is more sophisticated. Recent draws better reflect current machine conditions. Formula: `weight = decay_factor ^ weeks_since_draw`. | Med | Exponential decay is the standard approach (decay_factor ~0.98 per draw). PROJECT.md flags this as pending research. Recommend exponential decay with configurable decay_factor. |
| **5-Strategy Diversification** | Competitors typically offer 1-2 generation methods. Providing 5 distinct strategies (frequency, pattern, range, balance, composite) with clear explanations of each gives users both variety and education. | High | Core feature from PROJECT.md. Each strategy is a separate algorithm module. The composite strategy needs careful weighting design. |
| **Machine Bias Heatmap** | Visual heatmap showing which numbers each machine "favors" relative to expected frequency. Instantly communicates the core value proposition. | Med | 3x45 grid heatmap. Color intensity = deviation from expected frequency. Powerful visual that no competitor has for machine-specific data. |
| **Machine Comparison View** | Side-by-side comparison of all 3 machines showing their statistical profiles. Helps users understand WHY they should care about machine selection. | Med | Three-column layout comparing hot numbers, cold numbers, odd/even ratios, sum distributions. |

### Tier 2 Differentiators (Medium Impact, Nice-to-Have)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **AC Value Analysis** | AC value (Arithmetic Complexity) measures number dispersion. Data already in dataset. Most Korean tools show this but few explain it well. Per-machine AC profiles are unique. | Low | Already computed. Show distribution per machine. 1호기 has higher AC=5 ratio (more dispersed numbers). |
| **End-Digit Sum Pattern (끝수합)** | End-digit sum is a Korean-specific analysis metric. Data pre-computed. Per-machine end-digit profiles are unique (3호기: 79.7% same-ending-digit rate). | Low | Already in dataset. Show distribution per machine. |
| **Frequent Pair Analysis** | Show which number pairs appear together most often per machine. Already identified: 1호기(22,38), 2호기(7,26), 3호기(13,45). | Med | Requires O(n^2) pair counting per machine. Valuable pattern insight. |
| **Number Gap Tracking** | How many draws since each number last appeared per machine. "Overdue" numbers. Feeds into hot/cold analysis. | Low | Simple last-seen calculation per machine. |
| **Sliding Window Configuration** | Let users adjust the analysis window (last 50/100/all draws). Different windows reveal different patterns. | Med | Adds complexity to every calculation but provides flexibility. Default to last 100 draws, allow 50/100/200/all. |
| **Strategy Explanation Cards** | Each of the 5 strategies gets a clear explanation of how it works. Educates users and builds trust. | Low | Static/semi-static content cards. Transparency over magic. |
| **Print/Export Results** | Users want to take generated numbers to the lottery store. Print-friendly layout or copy-to-clipboard. | Low | CSS print styles + clipboard API. Simple but appreciated. |

### Tier 3 Differentiators (Lower Priority)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Consecutive Number Pattern** | Analysis of how often consecutive numbers (e.g., 7-8, 22-23) appear per machine. | Low | Simple adjacent-number detection. |
| **Number Zone Distribution** | Visual showing distribution across 5 zones (1-9, 10-19, 20-29, 30-39, 40-45) per machine. This is the "range strategy" basis. | Low | Zone bucketing per machine. Bar or pie chart. |
| **Draw Trend Timeline** | Interactive timeline showing how machine statistical profiles change over time. | High | Requires rolling-window calculations over time. Nice but complex. |
| **Dark/Light Mode** | Modern UI expectation for web apps. | Low | CSS custom properties toggle. |

## Anti-Features

Features to explicitly NOT build. These would harm the product, mislead users, or add complexity without value.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Win Probability / Accuracy Claims** | Lottery draws are random. Claiming any prediction accuracy (e.g., "83% accurate") is deceptive and damages credibility. Multiple scam products use this tactic. | Display statistical tendencies, not predictions. Frame as "analysis-based suggestions" not "predictions." |
| **AI/ML Branding** | LSTM/neural network approaches for lottery prediction are academically debunked for improving odds. Using "AI-powered" language is misleading marketing. Our statistical approach is honest and sufficient. | Call it "statistical analysis" and "data-driven." Be honest about methodology. |
| **User Accounts / Login** | PROJECT.md explicitly scopes this out. Adds auth complexity, privacy concerns, and GDPR-like obligations for zero benefit in a local tool. | Stateless, no persistence needed. Every visit starts fresh. |
| **Real-Time Draw Fetching** | Scraping or API-calling lottery sites adds fragility, maintenance burden, and legal risk. Dataset is static JSON covering 417 draws. | Ship with static `new_res.json`. Provide instructions to manually update. |
| **Wheeling Systems** | Full/abbreviated wheel generation is a complex combinatorial feature that serves a different use case (multi-ticket optimization). Out of scope for a prediction-focused tool. | Focus on generating quality individual 6-number sets. |
| **Number Filtering/Exclusion** | Letting users exclude specific numbers or force-include numbers adds UI complexity and undermines the statistical basis of the strategies. | Let strategies speak for themselves. Users can always ignore sets they don't like. |
| **Purchase Integration** | Automating lottery ticket purchase. Explicitly out of scope per PROJECT.md. Legal and regulatory minefield. | Show numbers clearly for manual purchase. |
| **Gamification / Streaks / Points** | Gamifying lottery analysis encourages unhealthy gambling behavior. Responsible design avoids this. | Present as a calm analytical tool, not an engagement-optimized game. |
| **Historical Backtesting Claims** | "Our strategy would have matched X% of past draws" is misleading overfitting. | If showing backtesting, clearly label as "historical analysis" not "validation." |
| **Multi-Lottery Support** | Supporting Powerball, Mega Millions, etc. dilutes focus. This tool is specifically for Korean Lotto 6/45 with machine data. | Korean Lotto 6/45 only. Deep rather than broad. |

## Feature Dependencies

```
Machine Selection (호기 선택)
  --> ALL analysis features (every feature filters by machine)
  --> ALL generation strategies (every strategy is machine-specific)

Data Loading & Parsing (new_res.json)
  --> Machine Selection
  --> Every analysis and generation feature

Time Decay Weighting Engine
  --> Frequency Strategy (weighted frequencies)
  --> Pattern Strategy (weighted pair frequencies)
  --> Composite Strategy (all weighted inputs)
  --> Hot/Cold Number Display (weighted vs raw toggle)

Frequency Analysis (raw counts per machine)
  --> Frequency Strategy (number generation)
  --> Hot/Cold Display
  --> Machine Bias Heatmap
  --> Machine Comparison View

Pattern Analysis (pairs, consecutive, end-digit)
  --> Pattern Strategy (number generation)
  --> Frequent Pair Analysis display
  --> Consecutive Number Pattern display

Zone/Range Analysis (distribution across 5 zones)
  --> Range Strategy (number generation)
  --> Number Zone Distribution chart

Balance Analysis (odd/even, high/low ratios)
  --> Balance Strategy (number generation)
  --> Odd/Even Display
  --> High/Low Display

Frequency Strategy + Pattern Strategy + Range Strategy + Balance Strategy
  --> Composite Strategy (weighted combination of all four)

Responsive Layout
  --> Print/Export (must work on mobile too)
```

## MVP Recommendation

### Phase 1: Core Analysis Engine + Basic UI

Prioritize (must ship):
1. **Data loading + machine selection** -- Foundation for everything
2. **Frequency analysis per machine** (hot/cold, frequency chart) -- Table stakes
3. **5 strategy number generation** -- The core promise of the product
4. **Basic statistics dashboard** (odd/even, high/low, sum range, AC, end-digit) -- All pre-computed in data
5. **Clear disclaimer** -- Responsible design
6. **Machine bias heatmap** -- THE differentiating visualization

### Phase 2: Enhanced Analysis + Polish

7. **Time decay weighting with configurable decay factor** -- Elevates all strategies
8. **Frequent pair analysis** -- Unique per-machine insight
9. **Machine comparison view** -- Side-by-side understanding
10. **Sliding window configuration** -- User control over analysis depth
11. **Strategy explanation cards** -- Trust and education
12. **Print/export** -- Practical utility

### Defer:
- **Draw trend timeline**: High complexity, low immediate value. Revisit after core is solid.
- **Dark mode**: Low effort but not essential for MVP.
- **Number gap tracking**: Nice-to-have, not core.

## Strategy Generation Detail

Each of the 5 strategies should produce 5 sets of 6 numbers (total 25 sets):

### Strategy 1: Frequency (빈도 전략)
- Weight each number by time-decayed frequency for the selected machine
- Sample numbers with probability proportional to weighted frequency
- Ensure basic constraints: numbers 1-45, no duplicates, sorted ascending

### Strategy 2: Pattern (패턴 전략)
- Use machine-specific frequent pairs as seeds
- Incorporate consecutive number tendencies and end-digit patterns
- Build sets around known machine biases (e.g., 1호기 seeds with 10, 37, 38)

### Strategy 3: Range (구간 전략)
- Distribute numbers across 5 zones (1-9, 10-19, 20-29, 30-39, 40-45)
- Match the machine's historical zone distribution profile
- Ensure each zone is represented proportionally to machine tendency

### Strategy 4: Balance (홀짝밸런스 전략)
- Target machine-specific odd/even ratio (not necessarily 3:3)
- Target machine-specific high/low ratio
- Target machine-specific sum range (middle of machine's historical distribution)
- AC value targeting based on machine profile

### Strategy 5: Composite (종합 전략)
- Weighted combination of all 4 strategies above
- Suggested weights: Frequency 30%, Pattern 25%, Range 20%, Balance 25%
- Final constraint enforcement: valid 6-number set, sorted, within machine's typical sum range

## Sources

### Lottery Analysis Tool Landscape
- [Top 10 Lottery Software & Analysis Tools for 2026](https://www.brsoftech.com/blog/best-lottery-software-and-analysis-tools/) -- Feature survey
- [Best 11 Lottery Software and Lotto Prediction Tools for 2026](https://lotterytexts.com/blog/best-lottery-software-and-prediction-tools/) -- Competitor features
- [16 Best Lottery Software & Prediction Tools in 2026](https://gamblingngo.com/guides/best-lottery-software/) -- Market overview

### Hot/Cold & Frequency Analysis
- [Hot, Warm, and Cold Numbers Strategy - LottoMetrics](https://www.lottometrics.app/strategies/hot-cold-numbers) -- Three-tier classification approach
- [Hot & Cold Numbers Strategy - LotteryLava](https://www.lotterylava.com/strategies/hot-cold-analysis) -- Window-based frequency analysis
- [Lottery Frequency Analysis 2025 - LotteryValley](https://www.lotteryvalley.com/lottery-strategy/frequency-analysis) -- Frequency methodology

### Time Decay & Statistical Methods
- [LottoPipeline - GitHub](https://github.com/Callam7/LottoPipeline) -- Exponential decay implementation (decay_factor = 0.98^weeks), Bayesian fusion, Monte Carlo
- [AI Lottery Algorithm Deconstruction - LinkedIn](https://www.linkedin.com/pulse/ai-lottery-algorithm-deconstruction-deep-dive-its-hot-md-golam-sarwar-pp5dc) -- Decay-weighted frequencies
- [Cracking the Lottery Code with AI - Medium](https://medium.com/@federico.rodenas/cracking-the-lottery-code-with-ai-how-arima-lstm-and-machine-learning-could-help-you-predict-the-82e0b6d6ba43) -- ARIMA/LSTM approaches (noted as not improving odds)

### Balance & Constraint Strategies
- [Odd Even, Low High, Sums - Saliu](https://saliu.com/strategy.html) -- Balance strategy mathematics
- [Best Lottery Strategies 2025 - LotteryValley](https://www.lotteryvalley.com/lottery-strategies) -- Sum range and zone distribution
- [The Best Lotto Combination Using Odd and Even Numbers - Medium](https://medium.com/@edvin.hiltner/how-to-use-odd-and-even-numbers-when-playing-lotteries-668e8b64dd79) -- 3:3 odd/even for 6-number games

### Korean Lottery Specific
- [동행복권 공식 통계](https://dhlottery.co.kr/gameResult.do?method=statByNumber) -- Official Korean lottery statistics
- [로또타파](https://lottotapa.com/stat/result_test_number.php) -- Korean lottery analysis platform (machine data source)

### Anti-Feature / Responsible Design Evidence
- [Lottery Defeated 2026 - Yahoo Finance](https://finance.yahoo.com/news/lottery-defeated-2026-ai-accuracy-193600868.html) -- False AI accuracy claims examined
- [Lottery Gap AI Scam Exposed - MalwareTips](https://malwaretips.com/blogs/lottery-gap-ai-scam/) -- Deceptive prediction service patterns
- [Can AI Really Predict Lottery Numbers? - ToolJunction](https://www.tooljunction.io/blog/artificial-intelligence-can-predict-lottery-numbers) -- Honest assessment of AI limitations
