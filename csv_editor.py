"""
Documentation/written report purposes -- this file is used to edit the data set
"""

from __future__ import annotations
from spotipy_class import SpotipyExtended
import csv
import pprint


def csv_user_song_editor(data_set_name: str, new_csv_file: str, spotify_info: SpotipyExtended) -> None:
    """
    This method edits the spotify dataset to include the url and song id
    """
    all_data = []
    limit = 1
    with open(data_set_name, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        all_data.append(next(reader) + ["id", "url"])

        for row in reader:
            if limit == 100000:
                break

            print(limit)
            song_info = spotify_info.get_song_identifiers(row[2], row[1])

            if song_info is not None:
                all_data.append(row + [song_info[0], song_info[1]])

            limit += 1

    with open(new_csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(all_data)


if __name__ == '__main__':
    spot_test = SpotipyExtended("d4438951382c4c05bceb265fd8de11ec",
                                "f6890c57cc42499581c685cd79dadded")
    csv_user_song_editor('spotify_dataset.csv', "spotify_dataset_edited.csv", spot_test)
