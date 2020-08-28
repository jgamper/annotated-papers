"""Usage:
          generate.py

@ Jevgenij Gamper 2020
Generates readme, badges given the pdfs and md files stored in .annotated/
"""
import os
from docopt import docopt
from pybadges import badge
from collections import Counter
from pytablewriter import MarkdownTableWriter

INTRO = (
    "# Annotated papers :pencil:\n\nTracks research papers, articles and their topics read since July 2020 :+1:, and some "
    "that were read prior to July 2020\n"
    "<p align='center'>\n    <br>\n    <img src='figures/title_collage.jpg' width='800'/>\n    <br>\n<p>\n\n\n"
    "## Topics \n\nEvery badge is a topic with the count of articles associated with that topic. Colour represents "
    "if the number of read articles with that topic is below (red) or above (blue) average count. \n\n"
)


def parse_file_name(file_name):
    """
    Splits file name into author, date, title, and topics
    :param file_name:
    :return:
    """
    extracted_topics = file_name.split("[")[1].split("]")[0].split(", ")

    author, date, title = file_name.split(" [")[0].split(" - ")

    return author, date, title, extracted_topics


def enumerate_and_extract():
    """
    Enumerates articles in pdf directory and extracts author, date, file name and topics
    :return:
    """
    authors = []
    dates = []
    titles = []
    topics = []
    for root, dirs, files in os.walk("annotated/"):
        for file in files:
            if file.endswith(".md") or file.endswith(".pdf"):
                author, date, title, extracted_topics = parse_file_name(file)
                authors.append(author)
                dates.append(date)
                titles.append(title)
                topics.append(extracted_topics)

    return authors, dates, titles, topics


def get_table_string(authors, dates, titles, topics):
    """
    Returns an object ready to write a table
    :param authors:
    :param s:
    :param titles:
    :param topics:
    :return:
    """
    writer = MarkdownTableWriter(
        table_name="Completed Articles",
        headers=["Author", "Title", "Year", "Topics"],
        value_matrix=[
            [a, tit, d, ", ".join(top)]
            for a, d, tit, top in zip(authors, dates, titles, topics)
        ],
        margin=1,  # add a whitespace for both sides of each cell
    )
    return writer.dumps()


def generate_topic_badges(topic_counts):
    """
    Generate topic badges with count
    :param topic_counts:
    :return:
    """
    # Sort topic_counts
    topic_counts = {
        k: v
        for k, v in sorted(topic_counts.items(), key=lambda item: item[1], reverse=True)
    }

    html = ""
    mean_count = int(sum(topic_counts.values()) / len(topic_counts))
    for topic, count in topic_counts.items():
        # Generate badge
        color = "red" if count < mean_count else "blue"
        s = badge(left_text=topic, right_text="{}".format(count), right_color=color)
        # Save svg
        svg_name = "{}.svg".format(topic.replace(" ", "_"))
        svg_path = os.path.join("figures", "badges")
        os.makedirs(svg_path, exist_ok=True)
        svg_path = os.path.join(svg_path, svg_name)
        with open(svg_path, "w") as f:
            f.write(s)
        html += "<img src='figures/badges/{}'/> ".format(svg_name)
    return html


def main():
    authors, dates, titles, topics = enumerate_and_extract()

    table = get_table_string(authors, dates, titles, topics)

    flat_topics = [item for sublist in topics for item in sublist]

    topic_counts = Counter(flat_topics)

    html = generate_topic_badges(topic_counts)

    readme = INTRO + html + "\n\n" + table

    with open("README.md", "w") as f:
        f.write(readme)


if __name__ == "__main__":
    arguments = docopt(__doc__)
    main()
