from string import Template

from enum import Enum

class VaultActions(str, Enum):
    CreateVault = "vault:CreateVault"
    DeleteVault = "vault:DeleteVault"
    ListVault = "vault:ListVault"
    CreateItem = "vault:CreateItem"
    ReadItem = "vault:ReadItem"
    UpdateItem = "vault:UpdateItem"
    DeleteItem = "vault:DeleteItem"
    CreatePermission = "vault:CreatePermission"
    ReadPermission = "vault:ReadPermission"
    UpdatePermission = "vault:UpdatePermission"
    DeletePermission = "vault:DeletePermission"
    FullAccess = "vault:FullAccess"


class AccountActions(str, Enum):
    ListPermissions = "account:ListPermissions"
    CreatePermission = "account:CreatePermission"
    ReadPermission = "account:ReadPermission"
    UpdatePermission = "account:UpdatePermission"
    DeletePermission = "account:DeletePermission"
    ChangeEmail = "account:ChangeEmail"
    ChangeMasterPassword = "account:ChangeMasterPassword"
    CloseAccount = "account:CloseAccount"
    ReadProfile = "account:ReadProfile"
    UpdateProfile = "account:UpdateProfile"
    FullAccess = "account:FullAccess"

def check_account_level_access(
    account_id,
    resource_type,
    action,
    user_id=None,
    principal_id=None,
    vault_id=None,
    item_id=None):

    flag = None

    user_permissions = crud.get_user_permissions()
    effect = "allow"

    if resource_type == "account":
        resource_id = f"krn:kps:account:{account_id}"
        if fetched_action == AccountActions.FullAccess:
            flag = True
        elif effect == "allow":
            flag = True
        elif effect == "deny":
            flag = False

    elif resource_type == "vault":
        if fetched_action == VaultActions.FullAccess:
            flag = True

    return flag


def check_resource_level_access():
    ...


def check_permissions(
    account_id,
    resource_type,
    action,
    user_id=None,
    principal_id=None,
    vault_id=None,
    item_id=None):

    flag = None

    if resource_type in ["account", "vault"]:
        account_level_access = check_account_level_access(
            account_id,
            resource_type,
            action,
            user_id,
            principal_id,
            vault_id,
            item_id)
    if resource_type in ["vault"]:
        account_resource_access = check_resource_level_access(
            account_id,
            resource_type,
            action,
            user_id,
            principal_id,
            vault_id,
            item_id)


    ### CASE-1 Actions related to account###
    if account_level_access == True:
        flag = True
    elif account_level_access == False:
        return False


    return flag

