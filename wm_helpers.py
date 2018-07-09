def derive_scores(team_names, fifa_ranks, team_scores):
    nations_info_y = team_scores["Nationality"]
    missing = set(team_names) - set(nations_info_y)
    derived_teams = []

    for nation in missing:
        search_space = [nation] + list(set(nations_info_y))
        fifa_y_kin = fifa_ranks[fifa_ranks["country_full"].isin(
            search_space)].reset_index(drop=True)

        nations_list = fifa_y_kin["country_full"].tolist()
        nations_idx = nations_list.index(nation)
        nations_len = len(nations_list)

        if (nations_len - 1) == nations_idx:
            kin_nation = nations_list[nations_idx - 1]
            kin_info = team_scores[team_scores["Nationality"] == kin_nation]
            #print(kin_nation)
            new_nation = {
                "Attack": kin_info.Attack.values[0] - 2,
                "Defense": kin_info.Defense.values[0] - 2,
                "Midfield": kin_info.Midfield.values[0] - 2,
                "Nationality": nation,
                "Overall": kin_info.Overall.values[0] - 2,
                "Year": kin_info.Year.values[0]
            }
            derived_teams.append(new_nation)
        else:
            better_nation = nations_list[nations_idx - 1]
            better_info = team_scores[team_scores["Nationality"] ==
                                      better_nation]

            worse_nation = nations_list[nations_idx + 1]
            worse_info = team_scores[team_scores["Nationality"] ==
                                     worse_nation]

            new_nation = {
                "Attack":
                (better_info.Attack.values[0] + worse_info.Attack.values[0]) /
                2,
                "Defense":
                (better_info.Defense.values[0] + worse_info.Defense.values[0])
                / 2,
                "Midfield": (better_info.Midfield.values[0] +
                             worse_info.Midfield.values[0]) / 2,
                "Nationality":
                nation,
                "Overall":
                (better_info.Overall.values[0] + worse_info.Overall.values[0])
                / 2,
                "Year":
                better_info.Year.values[0]
            }
            derived_teams.append(new_nation)

    return derived_teams