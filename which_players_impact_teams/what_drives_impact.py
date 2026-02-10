import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np

def collect_player_box_scores():
    url = "https://www.unrivaled.basketball/stats/player" # main stats page
    response = requests.get(url)
    html_content = response.text

    # players links to access box scores
    players = [
        f"https://www.unrivaled.basketball{a['href']}"
        for a in BeautifulSoup(html_content, "html.parser").find_all("a", href=True)
        if "/player/" in a['href']
    ]

    all_players_impact = []
    for player in players:
        # Reading box score table from the player page
        tables = pd.read_html(player)
        box_scores = tables[0]
        player_name = player.split("/")[-1].split("-")[0].replace("-", " ").title() + " "+ player.split("/")[-1].split("-")[1].replace("-", " ").title()
        box_scores['PLAYER'] = player_name
        
        # Str to numbers
        numeric_cols = ['PTS', 'REB', 'OREB', 'DREB', 'TO']
        for col in numeric_cols:
            box_scores[col] = pd.to_numeric(box_scores[col])
        
        box_scores['IMPACT'] = box_scores['PTS'] + 1.5*box_scores['OREB'] + box_scores['DREB'] - box_scores['TO']

        all_players_impact.append(box_scores)


    # Combining all players into a single DataFrame
    df_impact = pd.concat(all_players_impact, ignore_index=True)
    df_impact.to_csv("which_players_impact_teams/player_box_scores_impact.csv", index=False)

def analyse_player_impact():
    df_impact = pd.read_csv("which_players_impact_teams/player_box_scores_impact.csv")

    df_impact['SCORING_IMPACT'] = df_impact['PTS']
    df_impact['REBOUNDING_IMPACT'] = 1.5 * df_impact['OREB'] + df_impact['DREB']
    player_contributions=df_impact[['PLAYER','SCORING_IMPACT','REBOUNDING_IMPACT']]

    # contribution ratios per game
    # How much of this player’s overall impact comes from scoring or rebounding?
    df_impact['SCORING_Ratio'] = df_impact['SCORING_IMPACT'] / df_impact['IMPACT']
    df_impact['REBOUNDING_Ratio'] = df_impact['REBOUNDING_IMPACT'] / df_impact['IMPACT']

    # Aggregating by player for all games to get average ratios
    player_contributions = df_impact.groupby('PLAYER')[['SCORING_Ratio','REBOUNDING_Ratio']].mean()

    #Compute correlation with overall impact per player
    # When this player’s impact goes up or down, does rebounding/scoring go up or down with it?
    player_corr = df_impact.groupby('PLAYER').apply(
        lambda x: pd.Series({
            'SCORING_Corr2Impcat': x['IMPACT'].corr(x['SCORING_IMPACT']),
            'REBOUNDING_Corr2Impcat': x['IMPACT'].corr(x['REBOUNDING_IMPACT'])
        })
    )

    # summary table
    player_summary = player_contributions.join(player_corr)
    # print(player_summary)
    player_summary.to_csv("which_players_impact_teams/player_scoring_vs_rebounding_impact.csv")

def report():
    df_impact = pd.read_csv("which_players_impact_teams/player_box_scores_impact.csv")
    df_summary = pd.read_csv("which_players_impact_teams/player_scoring_vs_rebounding_impact.csv")

    df_impact = df_impact.merge(df_summary[['PLAYER', 'SCORING_Corr2Impcat', 'REBOUNDING_Corr2Impcat']], 
                                on='PLAYER', how='left')

    # Calculate correlation weights (normalize so they sum to 1)
    df_impact['total_corr'] = df_impact['SCORING_Corr2Impcat'].abs() + df_impact['REBOUNDING_Corr2Impcat'].abs()
    df_impact['scoring_weight'] = df_impact['SCORING_Corr2Impcat'].abs() / df_impact['total_corr']
    df_impact['rebounding_weight'] = df_impact['REBOUNDING_Corr2Impcat'].abs() / df_impact['total_corr']
    # cases where correlations might be NaN or zero
    df_impact['scoring_weight'] = df_impact['scoring_weight'].fillna(0.5)
    df_impact['rebounding_weight'] = df_impact['rebounding_weight'].fillna(0.5)

    # Calculate scoring and rebounding impact with weighted turnovers
    df_impact['SCORING_IMPACT'] = df_impact['PTS'] - (df_impact['TO'] * df_impact['scoring_weight'])
    df_impact['REBOUNDING_IMPACT'] = (1.5 * df_impact['OREB'] + df_impact['DREB']) - (df_impact['TO'] * df_impact['rebounding_weight'])

    # Aggregate by player to get average impacts per game (normalized)
    player_totals = df_impact.groupby('PLAYER').agg({
        'IMPACT': 'mean',
        'SCORING_IMPACT': 'mean',
        'REBOUNDING_IMPACT': 'mean'
    }).reset_index()

    # Sorting by average impact
    player_totals = player_totals.sort_values('IMPACT', ascending=True)

    # Who matters most, and how their impact is composed
    fig1, ax1 = plt.subplots(figsize=(12, 10))

    y_pos = np.arange(len(player_totals))
    players = player_totals['PLAYER'].values

    ax1.barh(y_pos, player_totals['SCORING_IMPACT'], label='Scoring', color='#5c8bc7', alpha=0.8)
    ax1.barh(y_pos, player_totals['REBOUNDING_IMPACT'], left=player_totals['SCORING_IMPACT'], label='Rebounding', color='#5a4198', alpha=0.8)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(players)
    ax1.set_xlabel('Average Impact per Game', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Player', fontsize=12, fontweight='bold')
    ax1.set_title('Who Impacts Their Team most, and How?', fontsize=14, fontweight='bold', pad=20)
    ax1.legend(loc='lower right')
    ax1.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig('which_players_impact_teams/player_impact_composition.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    collect_player_box_scores()
    analyse_player_impact()
    report()