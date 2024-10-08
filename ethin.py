import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
# from sklearn.pipeline import make_pipeline
# from tqdm import tqdm

class BinaryLabeler:
    """
    A class used to label records in a DataFrame as binary classes (0 and 1)
    based on a specified metric and threshold.

    Attributes
    ----------
    dataframe : pd.DataFrame
        The input DataFrame containing the data to be labeled.
    metric : str
        The column name of the metric in the DataFrame used for labeling.
    threshold : callable or float
        A function or a float value used as the threshold to split the classes.
        Default is np.median.

    Methods
    -------
    get_labels():
        Returns a pandas Series of binary labels (0 and 1) based on the specified metric and threshold.
    get_threshold():
        Returns the computed threshold value used for labeling.
    """

    def __init__(self, dataframe: pd.DataFrame, metric: str, threshold=np.median):
        """
        Parameters
        ----------
        dataframe : pd.DataFrame
            The input DataFrame containing the data to be labeled.
        metric : str
            The column name of the metric in the DataFrame used for labeling.
        threshold : callable or float, optional
            A function or a float value used as the threshold to split the classes.
            Default is np.median.
        """
        self.dataframe = dataframe
        self.metric = metric
        self.threshold = threshold

    def get_threshold(self) -> float:
      """
      Returns the computed threshold value used for labeling.

      Returns
      -------
      float
          The threshold value.
      """
      if callable(self.threshold):
          return self.threshold(self.dataframe[self.metric])
      else:
          return self.threshold

    def get_labels(self) -> pd.Series:
        """
        Returns a pandas Series of binary labels (0 and 1) based on the specified metric and threshold.

        Returns
        -------
        pd.Series
            A Series of binary labels (0 and 1).
        """
        threshold_value = self.get_threshold()
        labels = (self.dataframe[self.metric] > threshold_value).astype(int)
        return labels


# Example usage:
# df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})
# labeler = BinaryLabeler(df, 'value')
# threshold_value = labeler.get_threshold()
# labels = labeler.get_label()
# print("Threshold:", threshold_value)
# print("Labels:", labels)

class LogRegExperiment:
    """
    A class to perform logistic regression with elastic net regularization
    and cross-validation.

    Attributes
    ----------
    dataframe : pd.DataFrame
        The input DataFrame containing features and target.
    feature_columns : list
        List of column names to be used as features.
    target_column : str
        The column name of the target variable.
    X_scaled : np.ndarray
        Standardized feature data for training and testing.
    X_test : np.ndarray
        Feature data for testing the model.
    y_test : np.ndarray
        True labels for the test data.
    best_model : sklearn estimator
        The best logistic regression model found by GridSearchCV.

    Methods
    -------
    split_and_fit():
        Performs logistic regression with elastic net regularization and
        returns probability scores for classification results.
    print_classification_report():
        Prints the classification report for the test data.
    print_confusion_matrix():
        Prints and visualizes the confusion matrix for the test data.
    """

    def __init__(self, X, y, standard_scale=False):
        """
        Parameters
        ----------
        dataframe : pd.DataFrame
            The input DataFrame containing features and target.
        feature_columns : list
            List of column names to be used as features.
        target_column : str
            The column name of the target variable.
        """
        self.X = X
        self.y = y
        self.standard_scale = standard_scale
        self.X_scaled = None
        self.X_test = None
        self.y_test = None
        self.best_model = None

    def split_and_fit(self):
        """
        Performs logistic regression with elastic net regularization and
        returns probability scores for classification results.
        """
        # Extract features and target
        X = self.X
        y = self.y

        if self.standard_scale:
            # Standardize features
            scaler = StandardScaler()
            self.X_scaled = scaler.fit_transform(X)
            X = self.X_scaled

        # Split data into training and testing sets
        X_train, self.X_test, y_train, self.y_test = train_test_split(X, y, test_size=0.33, random_state=42, stratify=y)

        # Define the logistic regression model with elastic net regularization
        model = LogisticRegression(penalty='elasticnet',
                                   solver='saga',
                                   # class_weight='balanced',
                                   max_iter=1000,
                                   random_state=42)

        # Define the parameter grid for GridSearchCV
        param_grid = {
            'l1_ratio': [0.05, 0.1, 0.15],
            'C': [1.25, 1.5, 1.75],
        }

        # Initialize GridSearchCV with tqdm for progress tracking
        grid_search = GridSearchCV(model, param_grid, cv=5, verbose=0, n_jobs=-1)

        # Wrap the fit method with tqdm to show progress
        # with tqdm(total=len(param_grid['l1_ratio']) * 5, desc="Grid Search Progress", unit="iteration") as pbar:
        #     def update_bar(*args, **kwargs):
        #         pbar.update(1)

        # grid_search.fit(X_train, y_train, callback=update_bar)
        grid_search.fit(X_train, y_train)

        # Save the best model
        self.best_model = grid_search.best_estimator_

    def print_classification_report(self):
        """
        Prints the classification report for the test data.
        """
        if self.best_model is None:
            raise ValueError("Model has not been trained. Please run the experiment first.")

        # Predict the test data
        y_pred = self.best_model.predict(self.X_test)
        print('Classification Report:')
        print(classification_report(self.y_test, y_pred))

class LargestValueEvaluator:
    """
    A class to evaluate and compare the top n values from two columns of a pandas DataFrame.

    Attributes:
    -----------
    df : pd.DataFrame
        The DataFrame containing the data.
    column1 : str
        The name of the first column to evaluate.
    column2 : str
        The name of the second column to evaluate.
    n : int
        The number of top values to select from each column.
    compare_table : pd.DataFrame
        A DataFrame comparing the top n values from both columns.
    match_percentage : float
        The percentage of top n values that match between the two columns.

    Methods:
    --------
    evaluate():
        Selects the top n values from the specified columns and calculates the match percentage.
    """

    def __init__(self, df, column1, column2, n):
        self.df = df
        self.column1 = column1
        self.column2 = column2
        self.n = n
        self.compare_table = pd.DataFrame()
        self.match_percentage = 0.0

    def evaluate(self):
        # Select top n values from each column
        top_n_col1 = self.df.nlargest(self.n, self.column1)
        top_n_col2 = self.df.nlargest(self.n, self.column2)

        # Combine the indices
        combined_indices = top_n_col1.index.union(top_n_col2.index)

        # Create a comparison table
        columns = [self.column1, self.column2]
        self.compare_table = pd.concat([self.df.loc[top_n_col1.index, columns], \
                                        self.df.loc[top_n_col2.index, columns]])
        self.compare_table['Matched'] = self.compare_table.duplicated(keep=False)

        # Calculate match percentage
        matches = top_n_col1.index.intersection(top_n_col2.index)
        self.match_percentage = (len(matches) / self.n) * 100

if __name__ == '__main__':
    CATEGORIES = ['shoes', 'women', 'house', 'men', 'accessories', 'bags', 'jewelry', 'kids', 'beauty']
    COUNT = 10
    from robbie import DataReader, DataPreProcesser
    from mikael import ClassificationEvaluator
    # define path variables
    zip_file_dir = "A1_2024_Released.zip"
    csv_dir = "A1_2024_Unzip"

    # obtain the data
    data_reader = DataReader(zip_file_dir, csv_dir)
    combined_df = data_reader.combined_df
    dpp = DataPreProcesser(combined_df)
    df_pp = dpp.df

    df_cat = df_pp.copy()
    cat_col = combined_df["category"] 
    df_cat["category"] = cat_col

    lre = LogRegExperiment(df_pp.drop(columns='target'),
                           df_pp['target'].values)
    lre.split_and_fit()
    lr_model = lre.best_model
    print(lr_model)

    lr_y_pred = lr_model.predict(lre.X_test)
    lr_eval = ClassificationEvaluator(lr_model, lre.y_test, lr_y_pred)
    lr_eval.display_report()

    df_cat_proba = df_cat.drop(columns='target')
    lr_top_prod_proba_per_cat = lr_eval.get_top_produ_per_cat(df_cat_proba, cat_col, CATEGORIES, COUNT)
    lr_best_cat_df = lr_eval.get_cat_ratios(df_cat_proba, cat_col, CATEGORIES)

    lr_eval.plot_confusion_matrix()