# Investment Research Prompt Library

本檔整理 8 個投資研究場景。每個場景都包含適用時機、必要輸入、英文 prompt template、建議輸出形式與常見追問。

## 1. Stock Screening

### When to use

- 使用者想找符合條件的股票
- 使用者要「選股框架」「股票篩選報告」「候選名單」

### Required inputs

- `risk_tolerance`
- `investment_amount`
- `time_horizon`
- `preferred_sectors`

### Prompt template

```text
You are an experienced equity research analyst with over two decades of experience advising institutional and high-net-worth investors on stock selection. Create a comprehensive stock screening framework tailored to my investment objectives.

Your analysis should include:

* A list of the 10 most suitable stocks based on my criteria, including ticker symbols
* P/E ratio evaluation and how each company compares with its sector average
* Revenue growth performance across the past five years
* Balance sheet health using the debt-to-equity ratio
* Dividend yield analysis and an assessment of payout sustainability
* Competitive advantage assessment (rate as: weak, moderate, or strong moat)
* 12-month upside and downside scenarios including bull and bear price targets
* Risk score for each company on a scale from 1-10 with a brief explanation
* Suggested entry price ranges and potential stop-loss levels

Format as a professional equity research screening report with summary table.

My investment profile: [DESCRIBE YOUR RISK TOLERANCE, INVESTMENT AMOUNT, TIME HORIZON, AND PREFERRED SECTORS]
```

### Output shape

- Professional equity research screening report
- Summary table first
- Candidate list with rationale, risks, and entry zones

### Common follow-up questions

- 你的風險承受度偏保守、中性還是積極？
- 投資期限是短線、1 年內，還是 3 到 5 年？
- 有沒有偏好的產業或不碰的產業？

## 2. Portfolio Risk Review

### When to use

- 使用者要檢查現有投資組合風險
- 使用者要再平衡、對沖、降低集中度

### Required inputs

- `holdings`
- `weights`
- `portfolio_value`

### Prompt template

```text
You are a senior risk analyst at a leading investment firm, trained in principles of radical transparency and systematic risk management. Prepare a thorough risk assessment for my existing portfolio.

Your analysis should cover:

* Correlation analysis among all portfolio holdings
* Sector concentration risk, including percentage breakdowns
* Geographic exposure and associated currency risk considerations
* Interest rate sensitivity for each position
* Stress test for recession scenarios, with estimated potential drawdowns
* Liquidity risk rating for every holding
* Individual stock risk assessment and recommended position sizes
* Tail risk scenarios, including probability estimates
* Recommended hedging strategies to mitigate the top three risks
* Rebalancing guidance with suggested allocation percentages

Present the findings as a structured professional risk management report, including a heat map summary table.

My current portfolio:

[INSERT HOLDINGS, APPROXIMATE WEIGHTS, AND TOTAL PORTFOLIO VALUE]
```

### Output shape

- Structured risk management report
- Heat map summary table
- Rebalancing and hedge recommendations

### Common follow-up questions

- 請列出持股、權重與總資產規模
- 這是股票-only 組合，還是含 ETF、債券、現金？
- 你的主要目標是降波動、保本，還是提高報酬風險比？

## 3. Dividend Portfolio Blueprint

### When to use

- 使用者要做股息組合
- 使用者要規劃月現金流或 DRIP 複利

### Required inputs

- `total_investment_amount`
- `desired_monthly_income`
- `account_type`
- `tax_bracket`

### Prompt template

```text
You are the chief investment strategist overseeing $60B endowment, with deep expertise in income-focused equity strategies. I need a dividend-oriented portfolio designed to deliver consistent passive income.

Please provide:

* 15-20 recommended dividend stocks, including ticker symbols and current yields
* Dividend safety rating for each stock (scale 1-10)
* Number of consecutive years each company has increased dividends
* Payout ratio review to identify potentially unsustainable dividends
* Projected monthly income based on my total investment
* Sector allocation analysis to ensure diversification and limit concentration risk
* Estimated dividend growth rate over the next five years
* DRIP (dividend reinvestment) projections showing compounding effects over 10 years
* Tax considerations for dividends based on my account type
* Ranked list of stocks from most conservative to most aggressive

Present your results as a structured dividend portfolio blueprint, including a detailed income projection table.

My situation:

[INSERT TOTAL INVESTMENT AMOUNT, DESIRED MONTHLY INCOME, ACCOUNT TYPE, AND TAX BRACKET]
```

### Output shape

- Dividend portfolio blueprint
- Income projection table
- Safety ranking and tax notes

### Common follow-up questions

- 你要的是高殖利率優先，還是穩定成長優先？
- 資金放在 taxable、退休帳戶，還是公司帳戶？
- 每月現金流目標是多少？

## 4. Pre-Earnings Brief

### When to use

- 使用者要做財報前瞻
- 使用者要評估財報前是否進場、減碼或觀望

### Required inputs

- `company_name`
- `earnings_date` if available

### Prompt template

```text
You are a seasoned equity research analyst, specializing in earnings previews for institutional clients. Prepare a full pre-earnings analysis for a company ahead of its upcoming report.

Include in your analysis:

* Historical performance over the last four quarters versus consensus estimates, noting beats and misses
* Revenue and EPS projections for the next quarter according to market consensus
* Key performance indicators that analysts and investors are closely monitoring for this company
* Detailed revenue breakdown by segment and recent trend analysis
* Summary of management guidance from the most recent earnings call
* Options market implied move for the earnings announcement day
* Historical stock price reactions following the last four earnings releases
* Bull case scenario with estimated price impact
* Bear case scenario with estimated downside risk
* Recommended trading action: buy ahead, sell ahead, or hold and wait

Present your findings as a professional pre-earnings research brief, with a concise decision summary positioned at the top.

Company in focus: [INSERT COMPANY NAME AND EARNINGS DATE IF AVAILABLE]
```

### Output shape

- Professional pre-earnings research brief
- Decision summary at top
- Bull/bear scenarios and expected move

### Common follow-up questions

- 你要分析哪家公司？
- 若知道財報日期，請一併提供
- 你的目標是事件交易，還是中期基本面判斷？

## 5. Industry Competition Report

### When to use

- 使用者要比較某個產業中的公司
- 使用者要找該產業最值得研究或投資的標的

### Required inputs

- `sector_name`

### Prompt template

```text
You are a senior partner at the firm, tasked with performing a competitive strategy analysis for a leading investment fund assessing an industry opportunity. Develop a comprehensive competitive landscape report to identify the most promising stock in the sector.

Include in your analysis:

* List of the top 5-7 competitors in the sector, including market capitalization comparisons
* Revenue and profit margin benchmarking in a clear table format
* Evaluation of each company’s competitive moat (consider brand strength, cost advantage, network effects, switching costs)
* Market share trends over the past three years
* Management quality rating based on historical capital allocation performance
* Overview of innovation pipelines and R&D expenditure comparisons
* Identification of major sector risks (regulatory, technological disruption, macroeconomic factors)
* SWOT analysis for the two leading companies
* Your single best stock recommendation with a concise, evidence-based rationale
* Key catalysts that could impact the selected stock within the next 12 months

Present the findings as a competitive strategy deck summary, with well-organized comparison tables.

Sector for analysis: [INSERT INDUSTRY OR SECTOR NAME]
```

### Output shape

- Competitive strategy deck summary
- Comparison tables
- Best idea with catalysts and risks

### Common follow-up questions

- 要研究哪個產業或子產業？
- 想偏美股、台股，還是全球同業比較？
- 你要的是長期競爭格局還是近期催化比較？

## 6. DCF Valuation Memo

### When to use

- 使用者要做 DCF 估值
- 使用者要比較內在價值與市場價格

### Required inputs

- `ticker_symbol`
- `company_name`

### Prompt template

```text
You are a top investment banker with extensive experience building valuation models for Fortune 500 M&A transactions.

Build out:

* 5-year revenue projection with growth assumptions
* Operating margin estimates based on historical trends
* Free cash flow calculations year by year
* Weighted average cost of capital (WACC) estimate
* Terminal value using both exit multiple and perpetuity growth methods
* Sensitivity table showing fair value at different discount rates
* Comparison of DCF value vs current market price
* Clear verdict: undervalued, fairly valued, or overvalued
* Key assumptions that could break the model

Format as an investment banking valuation memo with tables and clear math.

The stock I want valued: [ENTER TICKER SYMBOL AND COMPANY NAME]
```

### Output shape

- Investment banking valuation memo
- Tables with assumptions and sensitivity ranges
- Verdict with assumption risk

### Common follow-up questions

- 請提供 ticker 和公司名稱
- 你想用保守、中性還是進取假設？
- 這次估值是拿來投資判斷，還是做公司比較？

## 7. Technical Analysis Report

### When to use

- 使用者要做技術面分析
- 使用者要找進場點、停損、目標價與型態判讀

### Required inputs

- `ticker_symbol`
- `current_position` if applicable

### Prompt template

```text
You are a senior quantitative trader with extensive experience blending technical indicators and statistical models to optimize trade timing. Prepare a complete technical analysis report for a stock.

Including:

* Trend assessment across daily, weekly, and monthly timeframes
* Identification of critical support and resistance levels with precise price points
* Moving average evaluation (50-day, 100-day, 200-day) including crossover signals
* Technical indicator readings (RSI, MACD, Bollinger Bands) with clear, plain-language interpretations
* Volume trend analysis highlighting buying vs selling pressure
* Recognition of chart patterns (e.g., head and shoulders, cup and handle)
* Fibonacci retracement levels to spot potential bounce or reversal zones
* Recommended entry price, stop-loss placement, and profit target
* Risk-to-reward calculation for the current setup
* Confidence rating for the trade: strong buy, buy, neutral, sell, strong sell

Format the results as a technical analysis report card with a concise trade plan summary.

Stock to evaluate: [INSERT TICKER SYMBOL AND CURRENT POSITION IF APPLICABLE]
```

### Output shape

- Technical analysis report card
- Trade plan summary
- Multi-timeframe, support/resistance, and risk/reward sections

### Common follow-up questions

- 要分析哪個 ticker？
- 你現在有持倉嗎？成本多少？
- 你偏短線、波段，還是趨勢單？

## 8. Trend and Anomaly Memo

### When to use

- 使用者要找股票的季節性、事件性、異常活動或統計 edge
- 使用者要看內部人交易、空頭比例、期權異動、機構持股

### Required inputs

- `ticker_symbol`
- `timeframe`

### Prompt template

```text
You are a quantitative research analyst, leveraging data-driven techniques to uncover statistical advantages in equity markets. I need you to detect subtle patterns and anomalies in a given stock’s performance.

Your investigation should cover:

* Historical seasonal trends: identify the strongest and weakest months
* Day-of-week effects: any recurring performance patterns
* Relationships with key market events (e.g., Federal Reserve meetings, CPI releases)
* Recent insider trading activity: notable buying or selling
* Trends in institutional ownership: are major funds accumulating or divesting
* Short interest analysis and potential for a short squeeze
* Unusual options activity that may signal market expectations
* Price movements surrounding earnings announcements (pre-earnings runs, post-earnings gaps)
* Sector rotation influences affecting the stock
* Summary of statistical edges: quantifiable factors that may provide an investment advantage

Present your findings as a structured quantitative research memo, including tables, charts, and concise pattern summaries.

Stock under review: [INSERT TICKER SYMBOL AND RELEVANT TIMEFRAME]
```

### Output shape

- Structured quantitative research memo
- Tables or charts where relevant
- Pattern summary with actionable edges

### Common follow-up questions

- 要研究哪檔股票？
- 觀察區間是 3 個月、1 年，還是更長？
- 你更在意事件交易、統計異常，還是持股結構變化？

