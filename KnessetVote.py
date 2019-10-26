
class KnessetVote(object):
    """
    a class to initial a knesset vote with all the votes of the MKs
    """
    def __init__(self, pg_u="", dt="", meet_n=0, vt_n=0, rl_nm="", yr_nm="", mk="", prt="", vt_t=""):
        """
        page_url - url of the page
        vote_date - the vote date
        meeting_num - the numer of meet (YESHIVA)
        vote_num - the number of the vote in specific meet
        rule_name - name of the rule
        yor_name - the YOR of the meet
        mk_name - name of the MK
        mk_party - party of the MK
        vote_to - the vote
        """
        self.page_url = pg_u
        self.vote_date = dt
        self.meeting_num = meet_n
        self.vote_num = vt_n
        self.rule_name = rl_nm
        self.yor_name = yr_nm
        self.mk_name = mk
        self.mk_party = prt
        self.vote_to = vt_t