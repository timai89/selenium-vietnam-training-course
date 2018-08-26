__author__ = 'jacob@vsee.com'

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../../")
from util.console import start_test
from util.support import create_gif
from resource import ODTC

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
from steps.login_steps import LoginSteps
from steps.font_end.provider.dashboard import DashBoardSteps
from steps.font_end.provider.control_panel import ControlPanelSteps
from steps.font_end.provider.visit_note import VisitNoteSteps
from steps.install_steps import InstallSteps
from steps.font_end.provider.my_patient import MyPatientSteps
from steps.font_end.provider.my_patient import AllVisitSteps
from steps.navigate_steps import NavigateSteps

testID = sys.argv[1]  # test case ID
bType = sys.argv[2]  # type of browser
osType = sys.argv[3]  # type of platform
userID = int(sys.argv[4])  # userID
src = sys.argv[5]  # Local VM ID
dst = sys.argv[6]  # Remote VM ID
is_install = int(sys.argv[7])  # Install VSee client if equal to 1
installFlagMem = int(sys.argv[8])  # Wait for Member installation
editPMHx = int(sys.argv[9])  # if 1 then Provider will edit the PMHx info of patient
checkSurveyFlag = int(sys.argv[10])  # if 1 then Check Provider Post Visit Survey will be on
endFlag = int(sys.argv[11])  # Local ends the call


# Tester thread
def nurse_start_visit():
    _actor = LoginSteps()
    _dashboard = DashBoardSteps()
    _control_panel = ControlPanelSteps()
    _install = InstallSteps()
    _my_patient = MyPatientSteps()
    _visit_note = VisitNoteSteps()
    _all_visit = AllVisitSteps()
    _navigate = NavigateSteps()

    # Patient Tele 02
    odtc = ODTC()
    patient_index = 1
    name = odtc.get_fullname_patient(env='tele', index=patient_index)
    # Provider 02
    index = 1

    try:
        _actor\
            .visit_telepsych() \
            .signin_as_provider(env='tele', index=index)

        _dashboard\
            .wait_for_patient_on_dashboard(name) \

        _navigate.goto_patient_page()

        _my_patient \
            .select_tab("All Visits")
        _all_visit \
            .search_history_visit_by(value=name) \
            .should_see_the_status_visit("Pending")\
            .view()

        # provider start Visit
        _control_panel.make_video_call()

        if is_install:
            _install.install_vsee()
        _install.launch_vsee(is_install)
        _install.accept_privacy_and_term_GDPR()

        _control_panel\
            .visit("InProgress.png")\

        _navigate.goto_patient_page()

        _my_patient \
            .select_tab("All Visits")
        _all_visit \
            .search_history_visit_by(value=name) \
            .should_see_the_status_visit("In Progress")\
            .view()

        _control_panel \
            .end_call(testID, src, dst, endFlag)

        _visit_note\
            .complete_without_notification()\
            .feedback_on_patient(env='tele').submit()

        _navigate.goto_patient_page()

        _my_patient \
            .select_tab("All Visits")
        _all_visit \
            .search_history_visit_by(value=name) \
            .should_see_the_status_visit("Completed")

        _navigate.goto_dashboard()

        print "[PASSED]: TEST PASSED"
    except Exception as e:
        print type(e)
        print e.args
        print e
        print "[FAILED]: TEST FAILED"

    finally:
        _actor.quit()
        create_gif()


def main():
    start_test()
    nurse_start_visit()


main()
