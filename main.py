import automated_archive_alert
import schedule
import time


def main():
    aoi_file_name = 'aoi_europe.geojson'
    collection = ['pneo', 'spot', 'phr']
    cloud_cover = 10
    print(f"-- Archive search will run on --\naoi: {aoi_file_name}\nCollection: {collection}\nCloud Cover: {cloud_cover}\n"
          f"These parameters can be modified in main.py")

    automated_archive_alert.archive_alert(aoi_file_name, cloud_cover, collection)
    print(f"Pending next run...")


if __name__ == "__main__":
    # main()
    schedule.every(60).minutes.do(main)

    # schedule.every().day.at("13:00").do(main)
    # schedule.every().day.at("14:00").do(main)
    # schedule.every().day.at("16:00").do(main)
    # schedule.every().day.at("18:00").do(main)
    # schedule.every().day.at("20:00").do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
