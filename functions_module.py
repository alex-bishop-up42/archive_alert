import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
import json
import up42


def configure_up42(script_path):

    project_conf_file = script_path / 'credentials/proj_conf_file.json'
    up42.authenticate(cfg_file=project_conf_file)


def archive_search(catalog, cloud_cover: int, aoi, search_start_date: str, search_end_date: str, collection: list[str]):

    """
    This function uses the UP42 sdk capabilities to run an archive search. In first step we build the search parameters,
    we then pass these parameters to the search method.

    :param catalog: The Catalog class enables access to the UP42 catalog functionality (data archive search & ordering).
    defined like this in automated_archive_alert.py 'catalog = up42.initialize_catalog()'
    :param cloud_cover: integer 0 to 100
    :param aoi: geojson file geometry single polygon
    :param search_start_date: '2020-01-01'
    :param search_end_date: '2020-01-01'
    :param collection: list string ["pneo", "phr", spot"] only collection within a single host and not cross host
    :return: search results is geopandas dataframe of the found archive, count result is number of results found
    """
    # Build the search parameters
    search_parameters = catalog.construct_search_parameters(geometry=aoi,
                                                            collections=collection,
                                                            start_date=search_start_date,
                                                            end_date=search_end_date,
                                                            usage_type=["DATA", "ANALYTICS"],
                                                            limit=500,
                                                            max_cloudcover=cloud_cover,
                                                            sortby='acquisitionDate',
                                                            ascending=True)

    print(f'Starting archive search')

    # Run the search against our search parameters
    search_results = catalog.search(search_parameters)

    print(f'Archive search done')
    count_results = len(search_results)

    # Return a count and the search results
    return count_results, search_results


def search_results_to_geojson(script_path, search_start_date: str, aoi_name_stem: str, search_results):

    """
    Use this function to write the archive search results to a geojson file.

    :param script_path: path of project directory
    :param search_start_date: string used for naming the output file
    :param aoi_name_stem: string used for the name of the output file
    :param search_results: search results from archive search
    :return: nothing is returned only a file is created in our daily_search_report directory
    """

    # Need to remove fields of type list to export to geojson
    try:
        del search_results['up42:usageType']
    except KeyError:
        pass

    # Write to geojson
    export_dir = script_path / 'output/daily_search_report'
    report_name = search_start_date + '_report_' + aoi_name_stem + '.geojson'
    search_results.to_file(export_dir / report_name, driver='GeoJSON')

    print(f'Archive report exported to geojson file as {report_name}')


def retrieve_previous_count(aoi_file_name):
    """
    This function gets the archive scene count from our previous_scene_count.json lof file
    :param aoi_file_name: current aoi file name
    :return:
    """
    count_json_file = './output/previous_scene_count.json'
    cjf = open(count_json_file)
    cjf_data = json.load(cjf)
    last_count = cjf_data[aoi_file_name]
    cjf.close()

    return int(last_count)


def update_count_value(aoi_file_name, scene_count):
    """
    This function updates the archive scene count in our previous_scene_count.json lof file
    :param aoi_file_name: current aoi file name
    :param scene_count: number of scenes archive search found
    :return:
    """
    count_json_file = './output/previous_scene_count.json'

    cjf = open(count_json_file)
    cjf_data = json.load(cjf)

    cjf_data[aoi_file_name] = scene_count

    with open(count_json_file, 'w') as kl:
        kl.write(json.dumps(cjf_data))

    cjf.close()


def set_count_to_0(aoi_file_name):
    """
    This function updates the archive scene count in our previous_scene_count.json lof file
    :param aoi_file_name: current aoi file name
    :return:
    """
    count_json_file = './output/previous_scene_count.json'

    cjf = open(count_json_file)
    cjf_data = json.load(cjf)

    cjf_data[aoi_file_name] = 0

    with open(count_json_file, 'w') as kl:
        kl.write(json.dumps(cjf_data))

    cjf.close()


def check_for_aoi_in_scene_count_file(aoi_file_name):
    count_json_file = './output/previous_scene_count.json'
    cjf = open(count_json_file)
    cjf_data = json.load(cjf)

    # Check if aoi is in scene count json
    if aoi_file_name in cjf_data.keys():
        print('AOI already in previous_scene_count.json file')
    else:
        print('AOI not in previous_scene_count.json file')
        cjf_data[aoi_file_name] = 0
        print('Has now been added')

    with open(count_json_file, 'w') as kl:
        kl.write(json.dumps(cjf_data))

    cjf.close()


def send_email(scene_count: int, aoi_name_stem: str, time: str):

    """
    Function which sends an email notification, a Google APP Password was created for this program.

    :param scene_count: number of scenes found in archive
    :param aoi_name_stem: name of aoi used for context in email
    :param time: string time when archive search was run
    :return: does not return anything, only that it sends an email
    """

    password_file_path = Path("./credentials/email_password.json")
    p_file = open(password_file_path)
    data = json.load(p_file)
    password = data["email_password"]
    p_file.close()

    email_sender = 'alex.bishop@up42.com'
    email_receiver = ['alex.bishop@up42.com']
    email_password = password

    subject = 'UP42 - New archive available for '+aoi_name_stem
    body = f'''
    AUTOMATED ARCHIVE MONITORING SYSTEM
    
    AOI : {aoi_name_stem}
    Search time : {time}
    Number of new scenes: {scene_count}
         
    '''

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


def main():
    print(f'This file is {__name__} file')


if __name__ == "__main__":
    main()
