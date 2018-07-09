import pandas as pd

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RationalQuadratic
from sklearn.gaussian_process.kernels import WhiteKernel


def preprocess_matches(matches_to_predict, team_scores, fifa_ranks):
    df = pd.merge(
        matches_to_predict,
        team_scores,
        how="left",
        left_on=["Year", "Home Team Name"],
        right_on=["Year", "Nationality"],
    )
    df = pd.merge(
        df,
        team_scores,
        how="left",
        left_on=["Year", "Away Team Name"],
        right_on=["Year", "Nationality"],
        suffixes=(' Home', ' Away'))

    df = pd.merge(
        df,
        fifa_ranks[["year", "country_full", "rank"]],
        how="left",
        left_on=["Year", "Home Team Name"],
        right_on=["year", "country_full"])
    df = pd.merge(
        df,
        fifa_ranks[["year", "country_full", "rank"]],
        how="left",
        left_on=["Year", "Away Team Name"],
        right_on=["year", "country_full"],
        suffixes=(' Home', ' Away'))

    df.drop(
        ['year Away', 'year Home', "country_full Away", "country_full Home"],
        axis=1,
        inplace=True)

    return df


def featurize_matches(preprocessed_matches):
    def featurize(row):
        home_goals = row["Home Team Goals"]
        away_goals = row["Away Team Goals"]

        # Simple result classes
        result = 1
        if home_goals > away_goals:
            result = 2
        elif home_goals < away_goals:
            result = 0
        row["Simple Result"] = result

        # Multi result classes
        row["Win Home"] = row["Win Away"] = row["Draw"] = False
        if home_goals > away_goals:
            row["Win Home"] = True
        elif home_goals < away_goals:
            row["Win Away"] = True
        else:
            row["Draw"] = True

        # Goal difference
        row["Goal Difference"] = abs(home_goals - away_goals)

        # Goals in match
        row["Total Goals"] = home_goals + away_goals
        return row

    return preprocessed_matches.apply(featurize, axis=1)


def predict_matches(preprocessed_matches, training_data):
    """Result: 2 - Home Team Wins, 1 - Draw, 0 - Away Team Wins"""

    X_cols = ["Overall Home", "rank Home", "Overall Away", "rank Away"]

    # Training algorithms
    X = training_data[X_cols]
    y_regr = training_data[["Goal Difference"]].values.ravel()
    y_class = training_data[["Simple Result"]].values.ravel()

    gpr = GaussianProcessRegressor(RationalQuadratic() +
                                   10 * WhiteKernel(noise_level=10))
    gpc = GaussianProcessClassifier(RationalQuadratic() +
                                    10 * WhiteKernel(noise_level=10))

    gpr.fit(X, y_regr)
    gpc.fit(X, y_class)
    print("Finished training")

    # Predicting new matches
    X_pred = preprocessed_matches[X_cols]
    y_regr_pred = gpr.predict(X_pred)
    y_class_pred = gpc.predict(X_pred)

    preprocessed_matches["Pred. Goal Difference"] = y_regr_pred
    preprocessed_matches["Pred. Result"] = y_class_pred

    predictions = preprocessed_matches[[
        "Date", "Home Team Name", "Away Team Name", "Pred. Goal Difference",
        "Pred. Result"
    ]]

    return predictions
