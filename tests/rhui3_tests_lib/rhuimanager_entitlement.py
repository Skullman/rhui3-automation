""" Red Hat entitlement certificates """

import re
import nose

from stitches.expect import Expect, ExpectFailed, CTRL_C
from rhui3_tests_lib.rhuimanager import RHUIManager, PROCEED_PATTERN

class MissingCertificate(ExpectFailed):
    """
    To be raised in case rhui-manager wasn't able to locate the provided certificate
    """

class BadCertificate(Exception):
    """
    Raised when a certificate is expired or invalid
    """
    def __init__(self):
        Exception.__init__(self)

class IncompatibleCertificate(Exception):
    """
    Raised when a certificate is incompatible with RHUI
    """
    def __init__(self):
        Exception.__init__(self)

class RHUIManagerEntitlements(object):
    '''
    Represents -= Entitlements Manager =- RHUI screen
    '''
    prompt = 'rhui \(entitlements\) => '

    @staticmethod
    def list(connection):
        '''
        return the list of entitlements
        '''
        RHUIManager.screen(connection, "entitlements")
        lines = RHUIManager.list_lines(connection, prompt=RHUIManagerEntitlements.prompt)
        Expect.enter(connection, 'q')
        return lines

    @staticmethod
    def list_rh_entitlements(connection):
        '''
        list Red Hat entitlements
        '''

        RHUIManager.screen(connection, "entitlements")
        Expect.enter(connection, "l")
        match = Expect.match(connection, re.compile("(.*)" + RHUIManagerEntitlements.prompt, re.DOTALL))

        matched_string = match[0].replace('l\r\n\r\nRed Hat Entitlements\r\n\r\n  \x1b[92mValid\x1b[0m\r\n    ', '', 1)

        entitlements_list = []
        pattern = re.compile('(.*?\r\n.*?pem)', re.DOTALL)
        for entitlement in pattern.findall(matched_string):
            entitlements_list.append(entitlement.strip())
        Expect.enter(connection, 'q')
        return entitlements_list


    @staticmethod
    def list_custom_entitlements(connection):
        '''
        list custom entitlements
        '''

        RHUIManager.screen(connection, "entitlements")
        Expect.enter(connection, "c")
        match = Expect.match(connection, re.compile("c\r\n\r\nCustom Repository Entitlements\r\n\r\n(.*)" + RHUIManagerEntitlements.prompt, re.DOTALL))[0]

        repo_list = []

        for line in match.splitlines():
            if "Name:" in line:
                repo_list.append(line.replace("Name:", "").strip())
        Expect.enter(connection, 'q')
        return sorted(repo_list)

    @staticmethod
    def upload_rh_certificate(connection, certificate_file = '/tmp/extra_rhui_files/rhcert.pem'):
        '''
        upload a new or updated Red Hat content certificate
        '''

        if connection.recv_exit_status("ls -la %s" % certificate_file)!=0:
            raise ExpectFailed("Missing certificate file: %s" % certificate_file)

        bad_cert_msg = "The provided certificate is expired or invalid"
        incompatible_cert_msg = "not compatible with the RHUI"

        RHUIManager.screen(connection, "entitlements")
        Expect.enter(connection, "u")
        Expect.expect(connection, "Full path to the new content certificate:")
        Expect.enter(connection, certificate_file)
        Expect.expect(connection, "The RHUI will be updated with the following certificate:")
        Expect.enter(connection, "y")
        match = Expect.match(connection, re.compile("(.*)" + RHUIManagerEntitlements.prompt, re.DOTALL))
        matched_string = match[0].replace('l\r\n\r\nRed Hat Entitlements\r\n\r\n  \x1b[92mValid\x1b[0m\r\n    ', '', 1)
        if bad_cert_msg in matched_string:
            Expect.enter(connection, 'q')
            raise BadCertificate()
        if incompatible_cert_msg in matched_string:
            Expect.enter(connection, 'q')
            raise IncompatibleCertificate()
        entitlements_list = []
        pattern = re.compile('(.*?\r\n.*?pem)', re.DOTALL)
        for entitlement in pattern.findall(matched_string):
            entitlements_list.append(entitlement.strip())
        Expect.enter(connection, 'q')
        return entitlements_list

