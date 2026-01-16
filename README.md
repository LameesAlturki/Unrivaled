# Unrivaled Basketball Analytics

A passion project analyzing the 2026 Unrivaled Basketball season. I'm using data to answer questions that intrigue me as I watch the games.

---

## Question 1: What Player's Impact Their Teams Most, and How?

Watching the first weeks of the 2026 season of Unrivaled, I wondered which players matter to their team's success more? and is Chelsea Gray's flying form shooting wise is equavilant to Alanna Smith's defensive work? Should Marina Mabery's individual efforts be dismissed just because the Lunar Owls keep losing? so here I am

To get an answer, I built a metric to quantify player impact and decompose it into scoring and rebounding contributions.

### Impact Formula

```
IMPACT = PTS + 1.5×OREB + DREB - TO
```

Where:
- **PTS**: Points scored
- **DREB**: Defensive rebounds
- **OREB**: Offensive rebounds (weighted 1.5x cuz it leads to extra posession which is more valuable than DREB)
- **TO**: Turnovers (negative impact)

### Methodology

**1. Impact Decomposition**

For each player, I calculate:
- **Scoring Impact**: Points, adjusted for turnover responsibility
- **Rebounding Impact**: Weighted rebounds (1.5×OREB + DREB), adjusted for turnover responsibility

**2. Turnover Allocation**

Turnovers are split between scoring and rebounding based on correlation. If a player's impact fluctuates more with their scoring than rebounding, more of their turnovers are attributed to scoring impact and vice versa.

**3. Player Profiling**

For each player across all games:
- **Impact Ratios**: Percentage of total impact from scoring vs rebounding
- **Impact Correlations**: Which component (scoring or rebounding) drives their impact variability

### Results as of Jan 16

<p align="center">
  <img src="which_players_impact_teams/player_impact_composition.png" width="900">
</p>

### Notes

- **Normalization**: All metrics are averaged per game, allowing fair comparison between players with different numbers of games played
- **Correlation Weighting**: Turnover allocation uses absolute correlation values normalized to sum to 1, with 50-50 split as fallback.

### Output Files

| File | Description |
|------|-------------|
| `player_box_scores_impact.csv` | Game-by-game box scores with calculated impact |
| `player_scoring_vs_rebounding_impact.csv` | Player summary with ratios and correlations |
| `player_impact_composition.png` | Visualization of impact composition |

---

## Data Source

All data scraped from [Unrivaled Basketball Stats](https://www.unrivaled.basketball/stats/player)
