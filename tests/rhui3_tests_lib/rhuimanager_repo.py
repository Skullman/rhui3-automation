""" RHUIManager Repo functions """

import re

from stitches.expect import Expect, ExpectFailed
from rhui3_tests_lib.rhuimanager import RHUIManager


class RHUIManagerRepo(object):
    '''
    Represents -= Repository Management =- RHUI screen
    '''
    @staticmethod
    def add_custom_repo(connection, reponame, displayname="", path="", checksum_alg="1", entitlement="y", entitlement_path="", redhat_gpg="y", custom_gpg=None):
        '''
        create a new custom repository
        '''
        RHUIManager.screen(connection, "repo")
        Expect.enter(connection, "c")
        Expect.expect(connection, "Unique ID for the custom repository.*:")
        Expect.enter(connection, reponame)
        checklist = ["ID: " + reponame]
        Expect.expect(connection, "Display name for the custom repository.*:")
        Expect.enter(connection, displayname)
        if displayname != "":
            checklist.append("Name: " + displayname)
        else:
            checklist.append("Name: " + reponame)
        Expect.expect(connection, "Path at which the repository will be served.*:")
        Expect.enter(connection, path)
        if path != "":
            path_real = path
        else:
            path_real = reponame
        checklist.append("Path: " + path_real)
        Expect.expect(connection, "Enter value.*:")
        Expect.enter(connection, checksum_alg)
        Expect.expect(connection, "Should the repository require an entitlement certificate to access\? \(y/n\)")
        Expect.enter(connection, entitlement)
        if entitlement == "y":
            Expect.expect(connection, "Path that should be used when granting an entitlement for this repository.*:")
            Expect.enter(connection, entitlement_path)
            if entitlement_path != "":
                checklist.append("Entitlement: " + entitlement_path)
            else:
                educated_guess, replace_count = re.subn("(i386|x86_64)", "$basearch", path_real)
                if replace_count > 1:
                    # bug 815975
                    educated_guess = path_real
                checklist.append("Entitlement: " + educated_guess)
        Expect.expect(connection, "packages are signed by a GPG key\? \(y/n\)")
        if redhat_gpg == "y" or custom_gpg:
            Expect.enter(connection, "y")
            checklist.append("GPG Check Yes")
            Expect.expect(connection, "Will the repository be used to host any Red Hat GPG signed content\? \(y/n\)")
            Expect.enter(connection, redhat_gpg)
            if redhat_gpg == "y":
                checklist.append("Red Hat GPG Key: Yes")
            else:
                checklist.append("Red Hat GPG Key: No")
            Expect.expect(connection, "Will the repository be used to host any custom GPG signed content\? \(y/n\)")
            if custom_gpg:
                Expect.enter(connection, "y")
                Expect.expect(connection, "Enter the absolute path to the public key of the GPG keypair:")
                Expect.enter(connection, custom_gpg)
                Expect.expect(connection, "Would you like to enter another public key\? \(y/n\)")
                Expect.enter(connection, "n")
                checklist.append("Custom GPG Keys: '" + custom_gpg + "'")
            else:
                Expect.enter(connection, "n")
                checklist.append("Custom GPG Keys: \(None\)")
        else:
            Expect.enter(connection, "n")
            checklist.append("GPG Check No")
            checklist.append("Red Hat GPG Key: No")

        RHUIManager.proceed_with_check(connection, "The following repository will be created:", checklist)
        Expect.expect(connection, "Successfully created repository *")
        Expect.enter(connection, "home")
