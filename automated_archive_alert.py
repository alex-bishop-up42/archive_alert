import functions_module as fm
from datetime import datetime
from pathlib import Path
import up42
import time


def archive_alert(aoi_file_name: str, cloud_cover: int, collection: list[str]):
    """
    The process starts with an authentication, search parameters defined in main() are applied, an archive search is
    performed, nu,ber of scenes found are compared to previous results, if new scenes are available then an email notification is sent.
    Possible archives to search over:
    HOST oneatlas : pneo, phr, spot
    HOST 21at : triplesat
    HOST nearspacelabs : nsl-30cm
    HOST hexagon : hexagon-eu-30cm,hexagon-na-15cm,hexagon-na-30cm
    HOST capellaspace : capella-slc, capella-geo, capella-gec, capella-sicd
    :param aoi_file_name: AOI file name found in aoi directory e.i. aoi_europe.geojson
    :param cloud_cover: Cloud cover value between 0 and 100
    :param collection: You can only search for one HOST at a time.
    :return: If new archive is found then an email will be sent and logs will be made. Available archive metadata is written to ./output/daily_search_report as a geojson file and can be loaded into a GIS software.
    """

    script_path = Path.cwd()

    fm.configure_up42(script_path)

    catalog = up42.initialize_catalog()

    # DEFINE THE AOI
    geojson_aoi_file = script_path / 'aoi' / aoi_file_name
    aoi = up42.read_vector_file(geojson_aoi_file)

    aoi_name_stem = str(geojson_aoi_file.stem)

    # SET SEARCH PARAMETERS
    search_start_date = datetime.today().strftime('%Y-%m-%d')
    search_end_date = datetime.today().strftime('%Y-%m-%d')
    collection = collection
    cloud_cover = cloud_cover

    # RUN THE ARCHIVE SEARCH
    archive_search = fm.archive_search(catalog, cloud_cover, aoi, search_start_date, search_end_date, collection)

    # The first return variable from the function is our count
    scene_count = archive_search[0]

    # The second return variable in our function is the search result data
    results = archive_search[1]

    print(f"The search returned : {scene_count} scenes for AOI {aoi_name_stem} today {search_start_date}")

    # EXPORT SEARCH RESULTS TO GEOJSON FILE
    fm.search_results_to_geojson(script_path, search_start_date, aoi_name_stem, results)

    # SET TIME AND UPDATE LOG
    current_time = time.gmtime()
    gmtime = time.strftime("%I:%M:%S %p", current_time)

    # Log file
    f = open("output/archive_log_file.txt", "a")
    f.write(f"{search_start_date},{aoi_name_stem},{gmtime},{scene_count}\n")
    f.close()

    previous_count = fm.retrieve_previous_count(aoi_file_name)
    print(f'{previous_count} was the previous count')

    scene_delta = scene_count - previous_count

    if scene_delta > 0:
        print(f"{scene_delta} new archive available")
        try:
            fm.send_email(scene_delta, aoi_name_stem, gmtime)
            print(f"Email notification sent!")
        except:
            print("Something went wrong with the email")

    elif scene_delta == 0:
        print(f"No new scenes are available at {gmtime}")

    elif scene_delta < 0:
        print("Delta came back as a negative number, this happens for the first search of a new day "
              "We solve this by setting the previous_scene_count back to 0")
        fm.set_count_to_0(aoi_file_name)
        new_previous_count = fm.retrieve_previous_count(aoi_file_name)
        print(f"New previous count {new_previous_count}")
        new_scene_delta = scene_count - new_previous_count
        if new_scene_delta > 0:
            print(f"{new_scene_delta} new archive available")
            try:
                fm.send_email(new_scene_delta, aoi_name_stem, gmtime)
                print(f"Email notification sent\nWaiting on next scheduled search...\n")
            except:
                print("Something went wrong with the email")
        elif new_scene_delta == 0:
            print(f"No new scenes are available at {gmtime}")

    else:
        print(f"Unhandled exception")

    fm.update_count_value(aoi_file_name, scene_count)


def main():
    print(f'This file is {__name__} file')


if __name__ == "__main__":
    main()
