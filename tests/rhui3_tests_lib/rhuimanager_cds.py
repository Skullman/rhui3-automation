""" RHUIManager CDS functions """

import re

from stitches.expect import Expect, ExpectFailed, CTRL_C
from rhui3_tests_lib.rhuimanager import RHUIManager, PROCEED_PATTERN
from rhui3_tests_lib.cds import Cds

class CdsAlreadyExistsError(ExpectFailed):
    """
    To be raised when trying to add an already tracked Cds
    """

class NoSuchCds(ExpectFailed):
    """
    To be raised e.g. when trying to select a non-existing Cds
    """

class InvalidSshKeyPath(ExpectFailed):
    """
    To be raised if rhui-manager wasn't able to locate the provided SSH key path
    """

class RHUIManagerCds(object):
    '''
    Represents -= Content Delivery Server (CDS) Management =- RHUI screen
    '''
    prompt = 'rhui \(cds\) => '

    @staticmethod
    def add_cds(connection, cds=Cds(), update=False):
        '''
        Register (add) a new CDS instance
        @param cds: rhuilib.cds.Cds instance
        @param update: Bool; update the cds if it is already tracked or raise ExpectFailed
        '''
        
        RHUIManager.screen(connection, "cds")
        Expect.enter(connection, "a")
        Expect.expect(connection, ".*Hostname of the CDS instance to register:")
        Expect.enter(connection, cds.host_name)
        state = Expect.expect_list(connection, [ \
            (re.compile(".*Username with SSH access to %s and sudo privileges:.*" % cds.host_name, re.DOTALL), 1),
            (re.compile(".*A Content Delivery Server instance with that hostname exists.*Continue\?\s+\(y/n\): ", re.DOTALL), 2)
        ])
        if state == 2:
            # cds of the same hostname is already being tracked
            if not update:
                # but we don't wish to update its config: raise
                raise ExpectFailed("%s already tracked but update wasn't required" % cds.host_name)
            else:
                # we wish to update, send 'y' answer
                Expect.enter(connection, "y")
                # the question about user name comes now
                Expect.expect(connection, "Username with SSH access to %s and sudo privileges:" % cds.host_name)
        # if the execution reaches here, uesername question was already asked
        Expect.enter(connection, cds.user_name)
        Expect.expect(connection, "Absolute path to an SSH private key to log into %s as ec2-user:" % cds.host_name)
        Expect.enter(connection, cds.ssh_key_path)
        state = Expect.expect_list(connection, [
            (re.compile(".*Cannot find file, please enter a valid path.*", re.DOTALL), 1),
            (PROCEED_PATTERN, 2)
        ])
        if state == 1:
            # don't know how to continue with invalid path: raise
            Expect.enter(connection, CTRL_C)
            Expect.enter(connection, "q")
            raise InvalidSshKeyPath(cds.ssh_key_path)
        # all OK, confirm
        Expect.enter(connection, "y")
        # some installation and configuration through Puppet happens here, let it take its time
        Expect.expect(connection, "The CDS was successfully configured." + ".*rhui \(.*\) =>", 180)


    @staticmethod
    def delete_cdses(connection, *cdses):
        '''
        unregister (delete) CDS instance from the RHUI
        '''
        RHUIManager.screen(connection, "cds")
        Expect.enter(connection, "d")
        RHUIManager.select_items(connection, *cdses)
        Expect.enter(connection, "y")
        Expect.expect(connection, "Unregistered" + ".*rhui \(.*\) =>", 180)

    @staticmethod
    def list(connection):
        '''
        return the list of currently managed CDSes
        '''
        RHUIManager.screen(connection, "cds")
        # eating prompt!!
        lines = RHUIManager.list_lines(connection, prompt=RHUIManagerCds.prompt)
        ret = Cds.parse(lines)
        return [cds for _, cds in ret]

