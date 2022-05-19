import pandas as pd
import os
import matplotlib.pyplot as plt
import re


def filter_reviews_by_length(df_reviews_all):
    """Remove reviews that are shorter than 3 chars and longer than mean + one standard deviation (~1000 chars)
    """
    df_reviews_all['review_text'] = df_reviews_all['review_text'].map(
        lambda review: review[14:])  # remove date, which is at start of every review string (for now works for May only)
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


if __name__ == '__main__':
    file_path = 'reviews.csv'
    if os.path.isfile(file_path):
        df_reviews_all = pd.read_csv(file_path, sep=';')
    else:
        print("File 'reviews.csv' doesn't exist in this directory\n")
        exit(1)
    print("Processing csv...\n")
    df_reviews_all = filter_reviews_by_length(
        df_reviews_all)  # remove too long reviews
    df_reviews_all['review_text'] = df_reviews_all['review_text'].apply(
        filter_emojis)  # remove emojis
    df_reviews_all['review_text'] = df_reviews_all['review_text'].apply(
        filter_non_ascii)  # remove non ascii reviews
    df_reviews_all['review_text'] = df_reviews_all['review_text'].apply(
        remove_punctuation)  # remove punctuation
    df_reviews_all['review_text'] = df_reviews_all['review_text'].apply(
        remove_newlines)  # remove newlines
    # remove empty strings
    df_reviews_all = df_reviews_all[(df_reviews_all.review_text != "")]

    print("Creating new csv file 'reviews_cleaned.csv'\n")
    df_reviews_all.to_csv('reviews_cleaned.csv', sep=';')
