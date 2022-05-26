import pandas as pd
import os
import matplotlib.pyplot as plt
import re
from datetime import date
import sys

CURRENT_YEAR = date.today().year

def remove_date_from_review(review):
    space_pattern = re.compile(r"\s")
    splitted = re.split(space_pattern, review, maxsplit=3)
    if (len(splitted) == 4):
        removed_date = splitted[3]
    else:
        removed_date = ""
    return removed_date

def filter_reviews_by_length(df_reviews_all):
    """Remove reviews that are shorter than 3 chars and longer than mean + one standard deviation (~1000 chars)
    """
    #df_reviews_all['review_text'] = df_reviews_all['review_text'].map(
    #    lambda review: review[14:])  # remove date, which is at start of every review string (for now works for May only)
    df_reviews_all['review_text']  = df_reviews_all['review_text'].map(
        lambda review: remove_date_from_review(review))

    df_reviews_all['review_length'] = df_reviews_all['review_text'].map(
        lambda review: len(review))
    len_mean = df_reviews_all['review_length'].mean()
    standard_deviation = df_reviews_all['review_length'].std()
    df_reviews_all = df_reviews_all[(df_reviews_all.review_length > 4) & (
        df_reviews_all.review_length <= len_mean + standard_deviation)]

    # show review length distribution (histogram)
    #_ = plt.hist(df_reviews_all['review_length'], bins='auto')
    # plt.show()

    return df_reviews_all


def filter_emojis(review_text):
    """Filter emojis out of the string using regex
    """
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"♥"                      # heart icon
                               u""
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', review_text)


def filter_non_ascii(review_text):
    """Filter away reviews consisting of non ascii characters like chinese, russian etc.
    """
    ascii_pattern = re.compile(
        r'^[\s~`!@#$%^&*()_+=\[\]\\{}|;\':\",.\/<>?a-zA-Z0-9-]+$', re.ASCII)
    if re.match(ascii_pattern, review_text):
        return review_text
    else:
        return ""


def remove_punctuation(review_text):
    """Remove punctuation character
    """
    return re.sub(r'[\[\]\\\{\}\(\)\|\;\'\:\"\,\!\?\.]', '', review_text)


def remove_newlines(review_text):
    """Remove newlines
    """
    return review_text.replace("\n", " ")

def remove_early_access(df_reviews_all):
    """Remove "EARLY ACCESS REVIEW" string from review text, add new column with boolean value for early access reviews
    """
    pattern = re.compile(r"[0-9]{4}\sEARLY ACCESS REVIEW")
    df_reviews_all["early_access"] = False

    for i, row in df_reviews_all.iterrows():
        review = row["review_text"]
        if pattern.search(review):
            df_reviews_all.at[i,"review_text"] = re.sub(pattern,"",review)
            df_reviews_all.at[i,"early_access"] = True
        else:
            df_reviews_all.at[i,"early_access"] = False

    return df_reviews_all



def clean_review_date(review_date):
    """Clean review_date column
    """

    # Remove 'Posted: ' prefix at the start of each date
    review_date = review_date.replace("Posted: ", "")

    review_date = review_date.strip()

    # reviews from current year don't have year displayed explicitly, so we add that manually
    has_year_pattern = re.compile("^[0-9a-zA-Z\s]*,\s?[0-9]{4}$")
    if(not has_year_pattern.match(review_date)):
        review_date = review_date + ", " + str(CURRENT_YEAR)

    # make all dates have same format: there are entries where Month is before day, so swap them
    month_before_day_pattern = re.compile("^[a-zA-Z]* [0-9][0-9]?, [0-9]{4}$")
    if(month_before_day_pattern.match(review_date)):
        split_year = review_date.split(", ")
        split_month_day = split_year[0].split(" ")
        split_year[0] = split_month_day[1] + " " + split_month_day[0]
        review_date = ", ".join(split_year)

    # make sure that day is zero-padded
    split_date = review_date.split(" ")
    day = split_date[0]
    if(len(day) == 1):
        split_date[0] = "0" + day
    review_date = " ".join(split_date)

    return review_date


if __name__ == '__main__':
    if len(sys.argv) != 3 or "-h" in sys.argv or "--help" in sys.argv:
        print("\n------------------\nRun with 2 arguments: 1.file to process 2.output file name\nExample: python3 preprocessor.py input_file.csv output_file.csv\n-----------------\n")
        exit(1)
    
    file_path = sys.argv[1]
    output_file = sys.argv[2]
    if os.path.isfile(file_path):
        df_reviews_all = pd.read_csv(file_path, sep=';')
    else:
        print("File " + file_path + " doesn't exist in this directory\n")
        exit(1)
    print("Processing csv...\n")
    df_reviews_all['review_text'] = df_reviews_all['review_text'].apply(
        filter_emojis)  # remove emojis
    df_reviews_all['review_text'] = df_reviews_all['review_text'].apply(
        filter_non_ascii)  # remove non ascii reviews
    df_reviews_all['review_text'] = df_reviews_all['review_text'].apply(
        remove_punctuation)  # remove punctuation
    df_reviews_all = remove_early_access(df_reviews_all)  # remove "early access review" review from text, add new column
    df_reviews_all = filter_reviews_by_length(
        df_reviews_all)  # remove too long reviews
    df_reviews_all['review_text'] = df_reviews_all['review_text'].apply(
        remove_newlines)  # remove newlines
    df_reviews_all['review_date'] = df_reviews_all['review_date'].apply(
        clean_review_date)  # clean date

    # remove empty strings
    df_reviews_all = df_reviews_all[(df_reviews_all.review_text != "")]

    print("Creating new csv file " + output_file + "\n")
    df_reviews_all.to_csv(output_file, sep=';')
    print(df_reviews_all )