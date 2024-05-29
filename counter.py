from enum import Enum
from messages import Errors, Info


class Counter:
    def __init__(self):
        self.counter = {}

    def register_group(self, group) -> str:
        if group in self.counter:
            return Errors.GROUP_ALREADY_REGISTERED
        
        self.counter[group] = {}
        return Info.GROUP_REGISTERED

    def subscribe_user(self, group, username) -> str:
        if group not in self.counter:
            return Errors.GROUP_NOT_REGISTERED
        
        if username in self.counter[group]:
            return Errors.USER_ALREADY_SUBSCRIBED
        
        self.counter[group][username] = 0
        return Info.USER_SUBSCRIBED
    
    def get_count(self, group, username, context) -> str:
        if group not in self.counter:
            return Errors.GROUP_NOT_REGISTERED
        
        if len(context.args) == 0:
            if username not in self.counter[group]:
                return Errors.USER_NOT_FOUND
            
            return ", ".join([username, str(self.counter[group][username])])
        elif len(context.args) == 1:
            if (key := str(context.args[0])) not in self.counter[group].keys():
                return Errors.USER_NOT_FOUND
                
            return ", ".join([key, str(self.counter[group][key])])
                
        return Errors.BAD_FORMAT

    def get_counts(self, group) -> str:
        if group not in self.counter:
            return Errors.GROUP_NOT_REGISTERED
        
        if len(self.counter[group].keys()) == 0:
            return Info.NO_USER_SUBSCRIBED

        return '\n'.join([', '.join([str(username), str(count)]) for username, count in self.counter[group].items()])
    
    def set_count(self, group, username, context) -> str:
        if group not in self.counter:
            return Errors.GROUP_NOT_REGISTERED
        
        if username not in self.counter[group]:
            return Errors.USER_NOT_FOUND
        
        if len(context.args) == 1:
            try:
                value = int(context.args[0])
            except ValueError:
                return Errors.BAD_FORMAT
            
            self.counter[group][username] = value
        elif len(context.args) == 2:
            try:
                value = int(context.args[1])
            except ValueError:
                return Errors.BAD_FORMAT
            
            if (key := str(context.args[0])) not in self.counter[group]:
                return Errors.USER_NOT_FOUND
            
            self.counter[group][key] = value

        return Info.SUCCESSFUL_OPERATION
    
    def set_counts(self, group, context) -> None:
        if group not in self.counter:
            return Errors.GROUP_NOT_REGISTERED
        
        if len(context.args) != 1:
            return Errors.BAD_FORMAT
        
        try:
            value = int(context.args[0])
        except ValueError:
            return Errors.BAD_FORMAT
        
        if len(self.counter[group].keys()) == 0:
            return Info.NO_USER_SUBSCRIBED
        
        for username in self.counter[group]:
            self.counter[group][username] = value

        return Info.SUCCESSFUL_OPERATION
    
    def reset_count(self, group, username, context) -> str:
        if group not in self.counter:
            return Errors.GROUP_NOT_REGISTERED
        
        if len(context.args) == 0:
            if username not in self.counter[group]:
                return Errors.USER_NOT_FOUND
            
            self.counter[group][key] = 0
        elif len(context.args) == 1:
            if (key := str(context.args[0])) not in self.counter[group]:
                return Errors.USER_NOT_FOUND
            
            self.counter[group][key] = 0
        else:
            return Errors.BAD_FORMAT
        
        return Info.SUCCESSFUL_OPERATION
    
    def reset_counts(self, group):
        if group not in self.counter:
            return Errors.GROUP_NOT_REGISTERED
        
        if len(self.counter[group].keys()) == 0:
            return Info.NO_USER_SUBSCRIBED
        
        for username in self.counter[group].keys():
            self.counter[group][username] = 0

        return Info.SUCCESSFUL_OPERATION
    
    def increment_count(self, group, username, context):
        if group not in self.counter:
            return Errors.GROUP_NOT_REGISTERED
        
        if len(context.args) == 0:
            if username not in self.counter[group]:
                return Errors.USER_NOT_FOUND
            
            self.counter[group][username] += 1
        elif len(context.args) == 1:
            try:
                value = int(context.args[0])

                self.counter[group][username] += value
            except ValueError:
                if (key := str(context.args[0])) not in self.counter[group]:
                    return Errors.USER_NOT_FOUND
            
                self.counter[group][key] += 1
        elif len(context.args) == 2:
            try:
                value = int(context.args[1])
            except ValueError:
                return Errors.BAD_FORMAT
            
            if (key := str(context.args[0])) not in self.counter[group]:
                return Errors.USER_NOT_FOUND
            
            self.counter[group][key] += value

        return Info.SUCCESSFUL_OPERATION
    
    def handle_help(self):
        return """/start - starts the bot and registers a group in the system\n\n/subscribe - subscribes a user to the group\n\n/get [@user] - returns user's count (sender's count if user not specified)\n\n/getall - returns all counts\n\n/set [@user] <value> - sets user's count (sender's count if user not specified) to the value\n\n/setall <value> - sets all counts to the value\n\n/reset [@user] - resets user's count (sender's count if user not specified)\n\n/resetall - resets all counts\n\n/increment [@user] [value] - increments user's count (sender's count if user not specified) of the value (1 if value not specified)"""