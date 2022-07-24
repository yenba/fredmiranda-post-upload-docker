from multiprocessing import Pool
import uuid
import json
import argparse
import pandas as pd
import sqlalchemy
from pool_methods import parse_page

# setup the argument parser
parser = argparse.ArgumentParser(description="This is how you pass Postgres DB Info into the script!",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--dbname", help="Database Name")
parser.add_argument("--dbuser", help="Database Username")
parser.add_argument("--dbpass", help="Database Password")
parser.add_argument("--dbhost", help="Database Host")
parser.add_argument("--dbport", default=5432, help="Database Port number")
args = vars(parser.parse_args())

# Set up parameters
dbname = args["dbname"]
dbuser = args["dbuser"]
dbpass = args["dbpass"]
dbhost = args["dbhost"]
dbport = args["dbport"]

conn_string = "postgresql://"+dbuser+":"+dbpass+"@"+dbhost+"/"+dbname
engine = sqlalchemy.create_engine(conn_string)
indexes = ["post_id"]
pageCount = 10
poolWorkerCount = 2
p = Pool(poolWorkerCount)

##### FUNCTIONS GO HERE ####
def get_data_df():
    pages = p.map(parse_page, range(pageCount))
    merged_page = []
    for page in pages:
        merged_page += page

    df = pd.DataFrame(merged_page)
    df = df.dropna()
    df.url = df.url.apply(lambda path: f"https://www.fredmiranda.com{path}")
    # df.to_csv ('export_new_dataframe.csv', index = False, header=True)
    return df

def upsert_df(df: pd.DataFrame, table_name: str, engine: sqlalchemy.engine.Engine):
    """Implements the equivalent of pd.DataFrame.to_sql(..., if_exists='update')
    (which does not exist). Creates or updates the db records based on the
    dataframe records.
    Conflicts to determine update are based on the dataframes index.
    This will set primary keys on the table equal to the index names

    1. Create a temp table from the dataframe
    2. Insert/update from temp table into table_name

    Returns: True if successful

    """

    # If the table does not exist, we should just use to_sql to create it
    if not engine.execute(
        f"""SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE  table_schema = 'public'
            AND    table_name   = '{table_name}');
            """
    ).first()[0]:
        df.to_sql(table_name, engine)
        return True

    # If it already exists...
    temp_table_name = f"temp_{uuid.uuid4().hex[:6]}"
    df.to_sql(temp_table_name, engine, index=True)

    index = list(df.index.names)
    index_sql_txt = ", ".join([f'"{i}"' for i in index])
    columns = list(df.columns)
    headers = index + columns
    headers_sql_txt = ", ".join(
        [f'"{i}"' for i in headers]
    )  # index1, index2, ..., column 1, col2, ...

    # col1 = exluded.col1, col2=excluded.col2
    update_column_stmt = ", ".join([f'"{col}" = EXCLUDED."{col}"' for col in columns])

    # For the ON CONFLICT clause, postgres requires that the columns have unique constraint
    query_pk = f"""
    ALTER TABLE "{table_name}" ADD CONSTRAINT {table_name}_unique_constraint_for_upsert UNIQUE ({index_sql_txt});
    """
    try:
        engine.execute(query_pk)
    except Exception as e:
        # relation "unique_constraint_for_upsert" already exists
        if 'unique_constraint_for_upsert" already exists' not in e.args[0]:
            raise e

    # Compose and execute upsert query
    query_upsert = f"""
    INSERT INTO "{table_name}" ({headers_sql_txt}) 
    SELECT {headers_sql_txt} FROM "{temp_table_name}"
    ON CONFLICT ({index_sql_txt}) DO UPDATE 
    SET {update_column_stmt};
    """
    engine.execute(query_upsert)
    engine.execute(f'DROP TABLE "{temp_table_name}"')

    return True



#### RUN IT HERE ####
df = get_data_df()
dupedrop = df.drop_duplicates(subset=['post_id'], keep="last")
# dupedrop.to_csv('export_new_dataframe_deduped.csv', index=False, header=True)
# print(dupedrop)

#### CONVERT TO INT #####
converted_dupedrop = dupedrop.astype({'post_id': 'int','views': 'int','posts': 'int'})
print(converted_dupedrop)

#### DB STUFF ####
newdf = pd.DataFrame(converted_dupedrop).set_index(indexes)
TNAME = dbname
upsert_df(df=newdf, table_name=TNAME, engine=engine)