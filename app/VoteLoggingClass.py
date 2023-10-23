from datetime import datetime

class VoteLoggingClass:
    '''
    Responsible for logging raw and summary votes
    '''
    def get_day_for_timestamp(self):
        today = datetime.now()
        formatted_date = today.strftime("%Y_%m_%d")
        return formatted_date

    def get_time_stamp_with_seconds(self):
        today = datetime.now()
        formatted_date = today.strftime("%Y_%m_%d_%H:%M:%S")
        return formatted_date

    def __init__(self):
        pass

    def log_raw_vote_to_file(self, incoming_number,incoming_msg,current_vote_name):
        pass

    def log_vote_summary_to_file(self,summary):
        pass

class LocalVoteLoggingClass(VoteLoggingClass):
    file_log_folder = '/home/regolith/Downloads/'

    def __init__(self):
        pass

    def log_raw_vote_to_file(self, incoming_number: str, incoming_msg: str, current_vote_name: str) -> None:
        f = open(self.file_log_folder+'/vote_log'+ self.get_day_for_timestamp() +'.txt', "a")
        f.write(self.get_time_stamp_with_seconds()+','+incoming_number+','+incoming_msg+','+current_vote_name+'\n')
        f.close()

    def log_vote_summary_to_file(self,summary):
        f = open(self.file_log_folder+'/vote_summary'+ self.get_day_for_timestamp() +'.txt', "a")
        f.write(summary)
        f.close()