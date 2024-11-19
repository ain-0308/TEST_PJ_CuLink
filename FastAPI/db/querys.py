from db.db_config import get_db_connection

def query_metadata_from_db(id_list: list):
    format_strings = ','.join(['%s'] * len(id_list))
    query = f"""
        SELECT * 
        FROM Cr_Articles 
        WHERE cr_art_id IN ({format_strings})
    """
    # print("쿼리쪽 id 리스트:", id_list)

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, tuple(id_list))
            result = cursor.fetchall()
            if not result:
                print("No matching articles found.")
            # print("조회해온 값.", result)
            return result
    except Exception as e:
        print(f"MySQL error: {e}")
        raise
    finally:
        connection.close()