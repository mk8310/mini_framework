from pydantic import Field

from mini_framework.web.std_models.base_model import BaseViewModel


class Permission(BaseViewModel):
    owner: str = Field(..., title="owner", description="权限所有者", alias="owner")
    name: str = Field(..., title="name", description="权限名称", alias="name")
    created_time: str = Field(
        ..., title="Created Time", description="创建时间", alias="createdTime"
    )
    display_name: str = Field(
        "", title="Display Name", description="显示名称", alias="displayName"
    )
    description: str = Field(
        "", title="Description", description="描述", alias="description"
    )
    users: list = Field([], title="Users", description="用户", alias="users")
    roles: list = Field([], title="Roles", description="角色", alias="roles")
    domains: list = Field([], title="Domains", description="域", alias="domains")
    model: str = Field("", title="Model", description="模型", alias="model")
    adapter: str = Field("", title="Adapter", description="适配器", alias="adapter")
    resource_type: str = Field(
        "", title="Resource Type", description="资源类型", alias="resourceType"
    )
    resources: list = Field(
        [], title="Resources", description="资源", alias="resources"
    )
    actions: list = Field([], title="Actions", description="操作", alias="actions")
    effect: str = Field("", title="Effect", description="效果", alias="effect")
    is_enabled: bool = Field(
        True, title="Is Enabled", description="是否启用", alias="isEnabled"
    )


class Role(BaseViewModel):
    owner: str = Field(..., title="owner", description="角色所有者", alias="owner")
    name: str = Field(..., title="name", description="角色名称", alias="name")
    created_time: str = Field(
        ..., title="Created Time", description="创建时间", alias="createdTime"
    )
    display_name: str = Field(
        "", title="Display Name", description="显示名称", alias="displayName"
    )
    users: list = Field([], title="Users", description="用户", alias="users")
    roles: list = Field([], title="Roles", description="角色", alias="roles")
    is_enabled: bool = Field(
        True, title="Is Enabled", description="是否启用", alias="isEnabled"
    )
    description: str = Field(
        "", title="Description", description="描述", alias="description"
    )


class AccountInfo(BaseViewModel):
    owner: str = Field("", title="owner", description="账号所有者", alias="owner")
    name: str = Field(..., title="name", description="账号名称", alias="name")
    created_time: str = Field(
        "", title="Created Time", description="创建时间", alias="createdTime"
    )
    updated_time: str = Field(
        "", title="Updated Time", description="更新时间", alias="updatedTime"
    )
    account_id: str = Field(..., title="ID", description="账号ID", alias="account_id")
    type: str = Field(..., title="Type", description="账号类型", alias="type")
    display_name: str = Field(
        "", title="Display Name", description="显示名称", alias="displayName"
    )
    first_name: str = Field("", title="First Name", description="名", alias="firstName")
    last_name: str = Field("", title="Last Name", description="姓", alias="lastName")
    avatar: str = Field("", title="Avatar", description="头像", alias="avatar")
    permanent_avatar: str = Field(
        "", title="Permanent Avatar", description="永久头像", alias="permanentAvatar"
    )
    email: str = Field(..., title="Email", description="邮箱", alias="email")
    email_verified: bool = Field(
        False, title="Email Verified", description="邮箱是否验证", alias="emailVerified"
    )
    phone: str = Field("", title="Phone", description="电话", alias="phone")
    location: str = Field("", title="Location", description="位置", alias="location")
    address: list = Field([], title="Address", description="地址", alias="address")
    affiliation: str = Field(
        "", title="Affiliation", description="从属", alias="affiliation"
    )
    title: str = Field("", title="Title", description="头衔", alias="title")
    id_card_type: str = Field(
        "", title="ID Card Type", description="身份证类型", alias="idCardType"
    )
    id_card: str = Field("", title="ID Card", description="身份证", alias="idCard")
    homepage: str = Field("", title="Homepage", description="主页", alias="homepage")
    bio: str = Field("", title="Bio", description="简介", alias="bio")
    tag: str = Field("", title="Tag", description="标签", alias="tag")
    region: str = Field("", title="Region", description="地区", alias="region")
    language: str = Field("", title="Language", description="语言", alias="language")
    gender: str = Field("", title="Gender", description="性别", alias="gender")
    birthday: str = Field("", title="Birthday", description="生日", alias="birthday")
    education: str = Field("", title="Education", description="教育", alias="education")
    score: int = Field(0, title="Score", description="分数", alias="score")
    karma: int = Field(0, title="Karma", description="业力", alias="karma")
    ranking: int = Field(0, title="Ranking", description="排名", alias="ranking")
    is_default_avatar: bool = Field(
        False,
        title="Is Default Avatar",
        description="是否默认头像",
        alias="isDefaultAvatar",
    )
    is_online: bool = Field(
        False, title="Is Online", description="是否在线", alias="isOnline"
    )
    is_admin: bool = Field(
        False, title="Is Admin", description="是否管理员", alias="isAdmin"
    )
    is_global_admin: bool = Field(
        False,
        title="Is Global Admin",
        description="是否全局管理员",
        alias="isGlobalAdmin",
    )
    is_forbidden: bool = Field(
        False, title="Is Forbidden", description="是否禁用", alias="isForbidden"
    )
    is_deleted: bool = Field(
        False, title="Is Deleted", description="是否删除", alias="isDeleted"
    )
    signup_application: str = Field(
        "",
        title="Signup Application",
        description="注册应用",
        alias="signupApplication",
    )
    permissions: list = Field(
        [], title="Permissions", description="权限", alias="permissions"
    )
    roles: list = Field([], title="Roles", description="角色", alias="roles")

    @property
    def render_account(self):
        account_dict = self.dict()
        permissions = account_dict.pop("permissions", [])
        roles = account_dict.pop("roles", [])
        account_dict["permissions"] = []
        account_dict["roles"] = []
        for perm_dict in permissions:
            account_dict["permissions"].append(perm_dict.get("name"))
        for role_dict in roles:
            account_dict["roles"].append(role_dict.get("name"))
        account_dict = clean_account_info(account_dict)
        render_account = RenderAccount(**account_dict)

        return render_account


class RenderAccount(BaseViewModel):
    name: str = Field(..., title="name", description="账号名称", alias="name")
    display_name: str = Field(
        "", title="Display Name", description="显示名称", alias="displayName"
    )
    account_id: str = Field(..., title="ID", description="账号ID", alias="account_id")
    avatar: str = Field("", title="Avatar", description="头像")
    email: str = Field("", title="Email", description="邮箱")
    phone: str = Field("", title="Phone", description="电话")
    title: str = Field("", title="Title", description="头衔")
    gender: str = Field("", title="Gender", description="性别")
    permissions: list = Field([], title="Permissions", description="权限")
    roles: list = Field([], title="Roles", description="角色")

    # def model_post_init(self, **data):
    #     self.phone = DataSecureUtil.desensitize_phone(self.phone)
    #     self.email = DataSecureUtil.desensitize_email(self.email)


def clean_role(role_dict):
    role_dict.pop("users")
    role_dict.pop("roles")
    role_dict.pop("createdTime")
    role_dict.pop("description")
    role_dict.pop("isEnabled")


def clean_account_info(account_dict: dict):
    render_account_keys = RenderAccount.model_fields.keys()
    account_keys = list(account_dict.keys())
    for key in account_keys:
        if key not in render_account_keys:
            account_dict.pop(key)
    return account_dict
