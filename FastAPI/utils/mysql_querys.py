from datetime import datetime

def query_metadata_from_db(id_list: list, connection):
    format_strings = ','.join(['%s'] * len(id_list))
    query = f"""
        SELECT * 
        FROM Cr_Articles 
        WHERE cr_art_id IN ({format_strings})
    """
    # print("쿼리쪽 id 리스트:", id_list)

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, tuple(id_list))
            result = cursor.fetchall()
            if not result:
                print("No matching articles found.")
            return result
    except Exception as e:
        print(f"MySQL 에러:")
        # raise
    finally:
        connection.close()

def query_id_date(id_list: list, date_list: list, connection):
    date_list_str = date_list  # 예시 문자열 날짜
    f_date_list = [
        datetime.strptime(date_str, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
        if i == 0 else datetime.strptime(date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        for i, date_str in enumerate(date_list_str)
    ]
    print('f_date_list',f_date_list)
    query = """
            SELECT * 
            FROM Cr_Articles 
            WHERE cr_art_date BETWEEN %s AND %s
            AND cr_art_id IN ({})
        """.format(', '.join(['%s'] * len(id_list)))
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (*f_date_list, *id_list))
            result = cursor.fetchall()
            # fetchall 결과가 None인지 확인
            if result is None:
                print("No matching articles found.")
                return []

            # result가 None이 아닌 경우에만 처리
            id_count = len([row['cr_art_id'] for row in result if 'cr_art_id' in row])
            print('result 아이디 길이 ',id_count)
            return result
    except Exception as e:
        print(f"MySQL 에러: {e}")
    finally:
        connection.close()

def query_date(date_list: list, connection):
    date_list_str = date_list  # 넘어온 날짜
    f_date_list = [
        datetime.strptime(date_str, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
        if i == 0 else datetime.strptime(date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        for i, date_str in enumerate(date_list_str)
    ]

    query = """
            SELECT * 
            FROM Cr_Articles 
            WHERE cr_art_date BETWEEN %s AND %s
        """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, tuple(f_date_list))
            result = cursor.fetchall()
            # fetchall 결과가 None인지 확인
            if result is None:
                print("No matching articles found.")
                return []

            return result
    except Exception as e:
        print(f"MySQL 에러: {e}")
    finally:
        connection.close()

def all_query(id_list: list, date_list: list, connection):
    if id_list and not date_list:
        metadata = query_metadata_from_db(id_list, connection)
        print('query_metadata_from_db')
        return metadata if metadata else []
    elif date_list and not id_list:
        d_metadata = query_date(date_list, connection)
        print('query_date')
        return d_metadata if d_metadata else []
    elif id_list and date_list:
        id_metadata = query_id_date(id_list, date_list, connection)
        print('query_id_date')
        return id_metadata if id_metadata else []
    