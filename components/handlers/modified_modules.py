'''
    This module contains the handler for web requests pertaining to
    retrieiving modules that have been modified.
'''


from app import RENDER, SESSION
import web
from components import model
from components.handlers.fixed_module_mountings import Fixed
from components.handlers.tentative_module_mountings import Tentative


class Modified(object):
    '''
        This class contains the implementations of the GET and POST requests.
        It retrieves a list of modified modules and determine which attributes
        have been modified.
    '''
    def __init__(self):
        '''
            Define the number of future AYs that will be included
            By right, this value should be set by the superadmin
        '''
        self.number_of_future_ays = 1


    def get_next_ay(self, ay):
        '''
            Return the AY that comes after the given AY
        '''
        ay = ay.split(' ')[1].split('/')
        return 'AY ' + str(int(ay[0])+1) + '/' + str(int(ay[1])+1)


    def get_modules_with_modified_mounting(self):
        '''
            Get all modules whose mounting has been modified in a future AY.
            Return the module code, current AY-Sem, target AY-Sem, and mounting change
        '''
        # Generate fixed mounting plan
        fixed_mounting_handler = Fixed()
        current_ay = model.get_current_ay()
        fixed_mounting_handler.populate_module_code_and_name()
        fixed_mounting_handler.populate_mounting_values()
        fixed_full_mounting_plan = fixed_mounting_handler.full_mounting_plan

        modified_modules = []
        target_ay = current_ay

        # Loop through each future AY
        for i in range(self.number_of_future_ays):
            target_ay = self.get_next_ay(target_ay)

            # Generate tentative mounting plan
            tenta_mounting_handler = Tentative()
            tenta_mounting_handler.populate_module_code_and_name()
            tenta_mounting_handler.populate_mounting_values(target_ay)
            tenta_full_mounting_plan = tenta_mounting_handler.full_mounting_plan

            # Compare the fixed and tentative mounting of each module for each semester
            # to see if there is any difference (if there is, means it's modified)
            for i in range(len(fixed_full_mounting_plan)):
                fixed_subplan = fixed_full_mounting_plan[i]
                tenta_subplan = tenta_full_mounting_plan[i]
                module_code = fixed_subplan[0]
                module_name = fixed_subplan[1]

                fixed_sem_1_mounting = fixed_subplan[2]
                tenta_sem_1_mounting = tenta_subplan[2]
                fixed_sem_2_mounting = fixed_subplan[3]
                tenta_sem_2_mounting = tenta_subplan[3]

                if tenta_sem_1_mounting == 0:
                    modified_modules.append([module_code, module_name, current_ay+" Sem 1",
                                             target_ay+" Sem 1", 0])  # Mounted --> Unmounted
                elif tenta_sem_1_mounting == 1 and fixed_sem_1_mounting == -1:
                    modified_modules.append([module_code, module_name, current_ay+" Sem 1",
                                             target_ay+" Sem 1", 1])  # Unmounted --> Mounted

                if tenta_sem_2_mounting == 0:
                    modified_modules.append([module_code, module_name, current_ay+" Sem 2",
                                             target_ay+" Sem 2", 0])  # Mounted --> Unmounted
                elif tenta_sem_2_mounting == 1 and fixed_sem_2_mounting == -1:
                    modified_modules.append([module_code, module_name, current_ay+" Sem 2",
                                             target_ay+" Sem 2", 1])  # Unmounted --> Mounted

        return modified_modules


    def get_modules_with_modified_quota(self):
        '''
            Get all modules whose quota has been modified in a future AY.
            Return the module code, module name, current AY-Sem, target AY-Sem, 
            current AY-Sem's quota, target AY-Sem's quota, and quota change
        '''
        modified_modules = model.get_modules_with_modified_quota()
        modified_modules = [list(module) for module in modified_modules]

        for module in modified_modules:
            current_quota = module[4]
            modified_quota = module[5]
            if current_quota is None:
                quota_change = '+' + str(modified_quota)
            elif modified_quota is None:
                quota_change = str(-current_quota)
            else:
                quota_change = modified_quota - current_quota
                if quota_change > 0:
                    quota_change = '+' + str(quota_change)
                else:
                    quota_change = str(quota_change)
            module.append(quota_change)

        # Include modules with specified quota that have mounting changes
        modules_wth_modified_mountings = self.get_modules_with_modified_mounting()
        for module in modules_wth_modified_mountings:
            mounting_change = module[4]
            if mounting_change == 1:   # Unmounted --> Mounted
                code = module[0]
                name = module[1]
                current_ay = module[2]
                target_ay = module[3]
                quota = model.get_quota_of_target_tenta_ay_sem(code, target_ay)
                if quota is not None and quota > 0:
                    modified_modules.append((code, name, current_ay, target_ay,
                                             "Unmounted", quota, '+'+str(quota)))
            elif mounting_change == 0:   # Mounted --> Unmounted
                code = module[0]
                name = module[1]
                current_ay = module[2]
                target_ay = module[3]
                quota = model.get_quota_of_target_fixed_ay_sem(code, current_ay)
                if quota is not None and quota > 0:
                    modified_modules.append((code, name, current_ay, target_ay,
                                             quota, "Unmounted", '-'+str(quota)))

        return modified_modules


    def get_modules_with_modified_details(self):
        '''
            Get all modules whose details (name/description/MC) has been modified.
            Return the module code, module name, 
            and [name modification, desc modification, MC modification] (if any)
        '''
        modified_modules = model.get_modules_with_modified_details()
        modified_modules = [list(module) for module in modified_modules]

        i = 0
        while i < len(modified_modules):
            module_details = modified_modules[i]
            module_code = module_details[0]
            old_module_name = module_details[1]
            old_module_desc = module_details[2]
            old_module_mc = module_details[3]
            current_module_name = module_details[4]
            current_module_desc = module_details[5]
            current_module_mc = module_details[6]

            is_name_modified = (current_module_name.rstrip() != old_module_name.rstrip())
            is_desc_modified = (current_module_desc.rstrip() != old_module_desc.rstrip())
            is_mc_modified = (current_module_mc != old_module_mc)
            if not is_name_modified and not is_desc_modified and not is_mc_modified:
                model.remove_original_module_info(module_code)
                del modified_modules[i]
                continue

            modifications = [None, None, None]
            if is_name_modified:
                modifications[0] = (old_module_name, current_module_name)
            if is_desc_modified:
                modifications[1] = (old_module_desc, current_module_desc)
            if is_mc_modified:
                modifications[2] = (old_module_mc, current_module_mc)

            modified_modules[i] = (module_code, current_module_name, modifications)
            i += 1

        return modified_modules


    def get_all_modified_modules(self):
        '''
            Get all modules that have been modified in some way or another.
            Return the module code, whether mounting is modified,
            whether quota is modified, and whether module details are modified
        '''
        modified_mounting_modules = self.get_modules_with_modified_mounting()
        modified_quota_modules = self.get_modules_with_modified_quota()
        modified_details_modules = self.get_modules_with_modified_details()
        modified_mounting_module_codes_names = [module[0:2] for module in modified_mounting_modules]
        modified_quota_module_codes_names = [module[0:2] for module in modified_quota_modules]
        modified_details_module_codes_names = [module[0:2] for module in modified_details_modules]

        modified_module_codes_names = modified_mounting_module_codes_names +\
                                      modified_quota_module_codes_names +\
                                      modified_details_module_codes_names
        modified_modules = []
        for modified_module in modified_module_codes_names:
            module_code = modified_module[0]
            if module_code in [module[0] for module in modified_modules]:
                continue
            module_name = modified_module[1]
            is_mounting_modified = any(module[0] == module_code for module in modified_mounting_module_codes_names)
            is_quota_modified = any(module[0] == module_code for module in modified_quota_module_codes_names)
            is_details_modified = any(module[0] == module_code for module in modified_details_module_codes_names)
            modified_modules.append((module_code, module_name, is_mounting_modified,
                                     is_quota_modified, is_details_modified))

        return modified_modules


    def GET(self):
        '''
            Renders the modified modules page if users requested
            for the page through the GET method.
        '''
        if SESSION['id'] != web.ACCOUNT_LOGIN_SUCCESSFUL:
            raise web.seeother('/login')

        # User can select the type of modified information they want to see
        # By default, the page will show ALL modified modules
        modify_type = None
        module_code = None
        try:
            input_data = web.input()
            modify_type = input_data.modifyType
        except AttributeError:
            raise web.seeother("/modifiedModules?modifyType=all")
        try:
            module_code = input_data.code
        except AttributeError:
            module_code = None

        modified_modules_summary = self.get_all_modified_modules()
        modified_modules_mounting = self.get_modules_with_modified_mounting()
        modified_modules_quota = self.get_modules_with_modified_quota()
        modified_modules_details = self.get_modules_with_modified_details()
        modified_modules = None

        if modify_type == "mounting":
            modified_modules = self.get_modules_with_modified_mounting()
        elif modify_type == "quota":
            modified_modules = self.get_modules_with_modified_quota()
        elif modify_type == "moduleDetails":
            modified_modules = self.get_modules_with_modified_details()
        elif modify_type == "all":
            modified_modules = self.get_all_modified_modules()

        # If module code is specified, only return data for the specified module
        if module_code is not None and (modify_type == "mounting"
                                        or modify_type == "quota"
                                        or modify_type == "moduleDetails"):
            module = [module for module in modified_modules if module[0] == module_code]

            if len(module) == 0:
                modified_modules = None
            else:
                modified_modules = module
        
        return RENDER.moduleModified(modify_type, modified_modules_summary,
                    modified_modules_mounting, modified_modules_quota,
                    modified_modules_details, module_code, modified_modules)


    def POST(self):
        '''
            Directs users to the page for tentative module mountings.

            This method is invoked when users click on the button
            to navigate to the tentative module mountings, that is
            present in other valid pages.
        '''
        raise web.seeother('/modifiedModules?modifyType=all')
