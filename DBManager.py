import csv

FILE_PATH = "db_kneset_votes2018.csv"

def kv_to_dict(kv):
    """
    parse KnessetVote to dictionary match to DB
    :param kv: the KnessetVote object
    :type kv: KnessetVote
    :return: tuple match to DB
    :rtype: tuple
    """
    vote_dict = {
        "vote_date": kv.vote_date,
        "meeting_num": kv.meeting_num,
        "vote_num": kv.vote_num,
        "rule_name": kv.rule_name,
        "yor_name": kv.yor_name,
        "mk_name": kv.mk_name,
        "mk_party": kv.mk_party,
        "vote_to": kv.vote_to,
        "page_url": kv.page_url
    }
    return vote_dict

def insert_list_of_knesset_votes(kv_list):
    """
    insert to the DB new lines with the objects from kv_list
    :param kv_list: list of KnessetVote objects
    :type kv_list: list
    :return: 1 if success, 0 if not.
    :rtype: int
    """
    if kv_list == None:
        return 0
    if len(kv_list) < 1:
        return 0
    kv_dicts = [kv_to_dict(kv) for kv in kv_list]
    if len(kv_dicts) < 1:
        print("NO VALUE TO INSERT. Maybe error...")
        return
    
    with open(FILE_PATH, "a", encoding="utf-8") as file_open:
        writer = csv.DictWriter(file_open, kv_dicts[0].keys())
        for kv_d in kv_dicts:
            writer.writerow(kv_d)
    
    return 1


def data_check(txt):
    with open("data_check9.txt", "w", encoding="utf-8") as file_data_check:
        file_data_check.write(txt)

def create_mk_party_dict():
    mk_party_dict = {}
    with open("Mks20.csv", "r", encoding="utf-8") as mks20_file:
        for row in mks20_file.readlines():
            data_row = row.splitlines()[0].split(",")
            mk_party_dict[data_row[0]] = data_row[1]
    return mk_party_dict

# TODO: make a function to remove duplicate lines
def remove_duplicates():
    with open(FILE_PATH,'r') as in_file, open('no_duplicates1.csv','w') as out_file:
        seen = set()
        for line in in_file:
            if line in seen: continue # skip duplicate
            seen.add(line)
            out_file.write(line)