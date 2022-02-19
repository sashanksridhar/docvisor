import pandas as pd
from sklearn.metrics.pairwise import haversine_distances
import multiprocessing as mp
import tqdm

concatenated_df_night = pd.read_csv("E:\\streetLights\\GPS\\Night\\GH012691_Hero7 Black-GPS5.csv")
concatenated_df_day = pd.read_csv("E:\\streetLights\\GPS\\Day\\GH012684_Hero7 Black-GPS5.csv")
total = pd.DataFrame(columns=['cts_x','date_x','GPS (Lat.) [deg]_x','GPS (Long.) [deg]_x','GPS (Alt.) [m]_x','GPS (2D speed) [m/s]_x','GPS (3D speed) [m/s]_x','fix_x','precision_x',
                              'cts_y', 'date_y', 'GPS (Lat.) [deg]_y', 'GPS (Long.) [deg]_y', 'GPS (Alt.) [m]_y',
                              'GPS (2D speed) [m/s]_y', 'GPS (3D speed) [m/s]_y', 'fix_y', 'precision_y'])

def extract(day, night=concatenated_df_night):

    distances = haversine_distances(
        night[['GPS (Lat.) [deg]', 'GPS (Long.) [deg]']],
        day[['GPS (Lat.) [deg]', 'GPS (Long.) [deg]']].to_frame().transpose()
    )

    if (min(distances)[0] > 0.00009):
        return

    # print(min(distances))

    distances = pd.DataFrame(distances, columns=['distance'])
    list1 = []
    for k, v1 in night.loc[distances.idxmin()].iterrows():
        for j in v1:
            list1.append(j)

    for j in day:
        list1.append(j)

    return list1

if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())
    print(mp.cpu_count())

    results = list(tqdm.tqdm(pool.imap_unordered(extract,  [v for k, v in concatenated_df_day.iterrows()]), total=len(concatenated_df_day)))


    for i in results:
        if i is None:
            continue
        a_series = pd.Series(i, index=total.columns)
        total = total.append(a_series, ignore_index=True)
    total.to_csv("E:\\streetLights\\GPS\\sample1.csv")



