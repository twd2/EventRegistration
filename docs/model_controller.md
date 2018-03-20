# 模型层设计

主要实现在`model`。完成数据库操作。我们约定将模块内部参数的检查放在此层，模块之间耦合的参数的检查放在逻辑层。

此外，每一个模型都有`ensure_indexes()`函数用于创建数据库索引，下面不再重复。关于数据库索引，请参见`database.md`或`database.pdf`。

## 用户子系统

主要实现在`model/user.py`。完成用户管理的数据库操作。

### `def init(username: str, rawdoc={})`

查询或者创建（若查询不到则创建）一个用户，并返回。创建时指定Accounts9的原始用户资料为`rawdoc`。

**参数：**

* `username`：字符串，用户名。
* `rawdoc`：（可选）对象，Accounts9返回的原始用户资料等信息。


### `def get(uid: objectid.ObjectId)`

根据用户ID查找相应用户，找不到则产生UserNotFoundError异常。

**参数：**

* `uid`：ObjectId，用户ID。

### `def get_by_username(username: str)`

根据用户名查找相应用户，找不到则产生UserNotFoundError异常。

**参数：**

* `username`：字符串，用户名。

### `def get_list_by_name(name: str)`

根据姓名查找用户列表。

**参数：**

* `name`：字符串，姓名。

### `def edit(uid: objectid.ObjectId, keep_enabled=False, **kwargs)`

修改用户信息，并可能激活用户，最后返回这个用户。

**参数：**

* `uid`：ObjectId，用户ID。
* `keep_enabled`：（可选）布尔，若用户未激活，是否保持未激活状态。默认不保持。


* 其他参数：请参见数据库设计文档。

### `def set_role(uid: objectid.ObjectId, role: int)`

根据用户ID给用户设定角色。

**参数：**

* `uid`：ObjectId，用户ID。
* `role`：整数，角色。

### `def set_role_by_username(username: str, role: int, when_old_role: int=None)`

根据用户名给用户设定角色，当用户原角色符合条件时。

**参数：**

- `username`：字符串，用户名。
- `role`：整数，角色。
- `when_old_role`：（可选）整数，要求用户原角色为特定角色。默认不要求。

### `def set_roles(uids, role, when_old_role: int=None)`

批量设置用户权限，当用户原角色符合条件时。

**参数：**

- `uid`：ObjectId的列表，用户ID列表。
- `role`：整数，角色。
- `when_old_role`：（可选）整数，要求用户原角色为特定角色。默认不要求。

### `def get_multi(**kwargs)`

返回数据库迭代器。

**参数：**

* 其他参数：数据库查询。

### `def get_list_by_role(role: int)`

根据角色查找用户列表。

**参数：**

- `role`：整数，角色。

### `def get_dict(uids)`

根据用户ID获得用户字典。

**参数：**

* `uids`：ObjectId的列表，用户ID列表。

### `def get_dict_by_username(usernames)`

根据用户名获得用户字典。

**参数：**

- `usernames`：字符串的列表，用户名列表。

### `def get_prefix_list(prefix: str, limit: int=50)`

获得有相同前缀用户名的用户的列表。

**参数：**

* `prefix`：字符串，用户名列表。
* `limit`：（可选）整数，列表项数限制。默认为50。

## 赛事管理

主要实现在`model/event.py`。完成消息管理的数据库操作。

### `def check_tags(tags)`

检查标签字符串集合的个数和集合中每个元素的长度是否在规定范围内。

**参数：**

* `tags`：列表，标签字符串的列表集合。

### `def sanitize_and_check_fields(fields)`

检查附加字段集合的个数和集合中每个元素是否符合附加字段规定的格式。

**参数：**

* `fields`：列表，附加字段的列表集合。

### `def check_time(begin_at: datetime.datetime, end_at: datetime.datetime)`

检查赛事报名开始时间是否早于赛事报名结束时间。

**参数：**

* `begin_at`：datetime，赛事报名开始时间。
* `end_at`：datetime，赛事报名结束时间。

### `def check_match_place(place: str)`

检查赛事举办地点字符串长度是否在规定范围内。

**参数：**

* `place`：字符串，赛事举办地点。

### `def check_match_time(time: str)`

检查赛事举办时间字符串长度是否在规定范围内。

**参数：**

* `time`：字符串，赛事举办时间。

### `def check_register(register_limit: int)`

检查赛事报名数限制是否在规定范围内。

**参数：**

* `register_limit`：整数，赛事报名数限制。

### `def check_member(member_lb: int, member_ub: int)`

检查赛事队伍人数下限与赛事队伍人数上限是否在规定范围内。

**参数：**

* `member_lb`：整数，若以组队形式报名，赛事队伍人数下限。
* `member_ub`：整数，若以组队形式报名，赛事队伍人数上限。

### `def add(...)`

函数原型为：

```python
def add(name: str, intro: str, creator_id: objectid.ObjectId,
        begin_at: datetime.datetime, end_at: datetime.datetime,
        place: str, time: str, register_limit: int,
        show_list: bool=False, is_group: bool=False, member_lb: int=0,
        member_ub: int=0, tags: list=[], fields: list=[])
```

添加一个赛事，并返回该赛事ID。

**参数：**

* `name`：字符串，赛事名称。
* `intro`：字符串，赛事简介。
* `creator_id`：ObjectId，赛事创建者ID。
* `begin_at`：datetime，赛事报名开始时间。
* `end_at`：datetime，赛事报名结束时间。
* `place`：字符串，赛事举办地点。
* `time`：字符串，赛事举办时间。
* `register_limit`：整数，赛事报名数限制。
* `show_list`：（可选）布尔，是否公布报名者列表，默认是不公布。
* `is_group`：（可选）布尔，是否以组队形式报名，默认是个人形式报名。
* `member_lb`：（可选）整数，若以组队形式报名，赛事队伍人数下限，默认是0。
* `member_ub`：（可选）整数，若以组队形式报名，赛事队伍人数上限，默认是0。
* `tags`：（可选）列表，赛事标签的列表集合，默认是空。
* `fields`：（可选）列表，赛事附加字段的列表集合，默认是空。

请参见数据库设计文档`events`集合。

### `def delete(eid: objectid.ObjectId)`

根据赛事ID在数据库中删除赛事，并返回该赛事。

**参数：**

* `eid`：ObjectId，赛事ID。

### `def inc(eid: objectid.ObjectId, **kwargs)`

根据赛事ID在数据库中增加赛事的查看次数或者报名次数，并返回该赛事。

**参数：**

* `eid`：ObjectId，赛事ID。
* 其他参数：目前取为`{'num_view': 1}`或`{'num_register': 1}`。

### `def inc_limited(eid: objectid.ObjectId, field: str, limit: int, inc: int=1)`

如果没有超过上限，根据赛事ID在数据库中增加指定字段指定数值，并返回该赛事。

**参数：**

* `eid`：ObjectId，赛事ID。
* `field`：字符串，字段名称。
* `limit`：整数，字段的数值上限。
* `inc`：（可选）整数，增加的大小，默认为1。

### `def get(eid: objectid.ObjectId)`

根据赛事ID在数据库中获取赛事并返回。

**参数：**

* `eid`：ObjectId，赛事ID。

### `def edit(eid: objectid.ObjectId, **kwargs)`

根据赛事ID在数据库中更新赛事信息，并返回该赛事。

**参数：**

* `eid`：ObjectId，赛事ID。
* 其他参数：同add。

### `def get_multi(**kwargs)`

根据赛事信息在数据库中查找符合要求的所有赛事，并返回赛事集合。

**参数：**

* 其他参数：同add。

### `def get_dict(eids)`

根据赛事ID的列表集合在数据库中查找符合要求的所有赛事，并返回赛事集合。

**参数：**

* `eids`：列表，赛事ID的列表集合。

## 赛事报名

### `def is_status(s)`

检查传入的报名状态是否合法。

**参数：**

* `s`：整数，报名状态。

### `def check_status(s)`

检查传入的报名状态是否合法。

**参数：**

* `s`：整数，报名状态。

### `def add(...)`

函数原型为：

```python
def add(creator_id: objectid.ObjectId, event_id: objectid.ObjectId, forcer_id: objectid.ObjectId=None,
        team_ids: list=[], team_leader: objectid.ObjectId=None, fields: list=[],
        status: int=STATUS_PENDING, reply: str='')
```

向数据库中添加一条新的报名表，返回ObjectId。如果该用户针对该赛事多次报名，产生DuplicateRegistrationError异常。

**参数：**

请参见数据库设计文档`registrations`集合。

### `def get(rid: objectid.ObjectId)`

根据ID查询数据库中的一条报名表，如果查询不到，产生RegistrationNotFoundError异常。

**参数：**
* `rid`：ObjectId，报名表ID。

### `def get_by_ids(creator: objectid.ObjectId, event: objectid.ObjectId)`

根据报名者ID和赛事ID查询数据库中的一条报名表，如果查询不到，返回null。

**参数：**
* `creator`：ObjectId，报名者ID。
* `event`：ObjectId，赛事ID。

### `def get_multi_by_creator(creator_id: objectid.ObjectId)`

查询某个用户的所有报名表。

**参数：**
* `creator_id`：ObjectId，报名者ID。

### `def get_multi_by_event(event_id: objectid.ObjectId, **kwargs)`

查询某个赛事的所有报名表。

**参数：**
* `event_id`：ObjectId，赛事ID。

### `def get_multi(**kwargs)`

根据给定参数查询数据库中所有相符的报名表。

**参数：**
* `kwargs`：查询条件。

### `def edit(rid: objectid.ObjectId, **kwargs)`

修改某报名表的有关内容。

**参数：**
* `rid`：ObjectId，报名表ID。
* 其余参数：待修改的报名表内容。

### `def delete(rid: objectid.ObjectId)`

根据ID从数据库中删除某条报名表。

**参数：**
* `rid`：ObjectId，报名表ID。

### `def review(rids, status, reply='')`

**参数：**

### `def has_group(eid: objectid.ObjectId, uid: objectid.ObjectId, exc: objectid.ObjectId=None)`

获得一个用户对于一个赛事而言，是否已经在某一个队伍中。

**参数：**

* `eid`：ObjectId，赛事ID。
* `uid`：ObjectId，用户ID。
* `exc`：（可选）ObjectId，报名ID。如果此参数不为`None`，则检索时忽略`exc`对应报名的影响。

## 用户消息提醒

主要实现在`model/message.py`。完成消息系统的数据库操作。

### `def add(sender_id: ObjectId, receiver_id: ObjectId, title: str, content: str)`

在数据库中添加一条未读的新消息，返回消息的ID。

**参数：**

* `sender_id`：ObjectId，发送者的ID。
* `receiver_id`：ObjectId，接受者的ID。
* `title`：字符串，新消息的标题。
* `content`：字符串，新消息的内容。

### `def get(mid: ObjectId)`

根据ID查询数据库中的一条消息，如果查询不到，产生MessageNotFoundError异常。

**参数：**

* `mid`：ObjectId，消息的ID。

### `def get_by_receiver(receiver_id: ObjectId, unread_only: bool=True)`

查询某个用户收到的所有未读消息（默认）或者已读消息。

**参数：**

* `receiver_id`：ObjectId，接受者的ID。
* `unread_only`：（可选）布尔，查询的是未读消息还是全部消息，默认只查询未读消息。

### `def set_read(mid: ObjectId, read: bool=True)`

设置某条消息的阅读状态，并返回该消息；如果没有查到，产生MessageNotFoundError异常。

**参数：**

* `mid`：ObjectId，消息的ID。
* `read`：（可选）布尔，将这条消息设置成未读还是已读，默认设置成已读。

## 内容管理

主要实现在`model/document.py`。完成内容增删查改的数据库操作。

### `def add(type: int, **kwargs)`

添加一个优秀运动员或系代表队，返回ID。

**参数：**

* `type`：整数，指明是优秀运动员还是系代表队。
* 其他参数：优秀运动员或系代表队特定的参数。参见数据库设计文档。

### `def delete(did: objectid.ObjectId, type: int)`

根据ID删除一个优秀运动员或系代表队。

**参数：**

* `did`：ObjectId，优秀运动员或系代表队ID。


* `type`：整数，指明是优秀运动员还是系代表队。

### `def inc(did: objectid.ObjectId, type: int, **kwargs)`

给一个优秀运动员或系代表队的计数器增加相应值。

**参数：**

- `did`：ObjectId，优秀运动员或系代表队ID。


- `type`：整数，指明是优秀运动员还是系代表队。
- 其他参数：要增加的计数器以及要增加的值。

### `def get(did: objectid.ObjectId, type: int)`

根据ID获得一个优秀运动员或系代表队。

**参数：**

- `did`：ObjectId，优秀运动员或系代表队ID。


- `type`：整数，指明是优秀运动员还是系代表队。

### `def edit(did: objectid.ObjectId, type: int, **kwargs)`

根据ID修改一个优秀运动员或系代表队。

**参数：**

- `did`：ObjectId，优秀运动员或系代表队ID。


- `type`：整数，指明是优秀运动员还是系代表队。
- 其他参数：同`add(...)`。

### `get_multi(type, **kwargs)`

获得数据库迭代器。

**参数：**

* `type`：整数，指明是优秀运动员还是系代表队。

## 二维码生成

主要实现在`util/qrcode.py`。完成赛事二维码的生成。

### `def generate(s)`

生成跳转到某个赛事链接的二维码，并加上酒井logo。

**参数：**

* `s`：字符串，二维码要跳转到的相对链接。


##操作日志

主要实现在`model/oplog.py`。完成操作日志的添加操作。

### `def add(creator_id: objectid.ObjectId, type: int, **kwargs)`

添加一则操作日志。

**参数：**

* `creator_id`：ObjectId，发起操作的用户ID。
* `type`：整数，操作类型。
* 其余参数：操作具体内容以及被操作用户、赛事、报名、消息或文档。

# 逻辑层设计

主要实现在`handler`。完成将用户的请求转换为模型层操作，并进行参数检查的动作。我们约定将模块内部参数的检查放在模块层，模块之间耦合的参数的检查放在此层。

注：所有GET请求，根据HTTP，均没有POST参数。所有POST请求，除非特别指明，均需要`csrf_token`参数用于防止跨站请求伪造攻击，下面POST参数一项中不再重复说明。

## 用户子系统

主要实现在`handler/user.py`、`handler/manage.py`。

### `GET /login`

跳转到Accounts9登录，如果登录前在浏览赛事，登录后返回相应赛事。

**RESTful参数：**

无

**GET参数：**

* `return_eid`：（可选）字符串，登录成功后返回的赛事。

### `GET /login/{return_eid}`

从Accounts9返回，继续登录。如果登录前在浏览赛事，登录后返回相应赛事。如果需要激活，先跳转到激活页面。

**RESTful参数：**

* `return_eid`：（可选）字符串，登录成功后返回的赛事。

**GET参数：**

* `code`：字符串，Accounts9返回的登录代码。
* `error`：字符串，Accounts9返回的登录错误信息。

### `GET /logout`

登出系统页面。

**RESTful参数：**

无

**GET参数：**

无

### `POST /logout`

登出系统。

**RESTful参数：**

无

**GET参数：**

无

**POST参数：**

无

### `GET /user/info`

编辑个人信息页面。

**RESTful参数：**

无

**GET参数：**

无

### `POST /user/info`

编辑个人信息。

**RESTful参数：**

无

**GET参数：**

无

**POST参数：**

同模型层`edit(...)`。

### `GET /user/search`

用户搜索。

**RESTful参数：**

无

**GET参数：**

* `q`：字符串，用户名前缀或用户姓名。

### `GET /manage`

用户管理首页。

**RESTful参数：**

无

**GET参数：**

无

### `GET /manage/admin`

管理员管理。

**RESTful参数：**

无

**GET参数：**

无

### `POST /manage/admin`

管理员添加。

**RESTful参数：**

无

**GET参数：**

无

**POST参数：**

* `operation=add`
* `username`：字符串，用户名。

### `POST /manage/admin`

管理员删除。

**RESTful参数：**

无

**GET参数：**

无

**POST参数：**

- `operation=remove`
- `uid`：ObjectId，用户ID。

## 赛事管理

主要实现在`handler/event.py`。

### `GET /event`

赛事列表页面，显示赛事名称，简介和报名开始时间。

**RESTful参数：**

无

**GET参数：**

* `page`：（可选）整数，显示赛事列表的第几页，默认为1。

### `GET /event/tag/{tag:[^/]*}`

根据赛事标签搜索，显示相关赛事列表的页面，显示赛事名称，简介和报名开始时间。

**RESTful参数：**

* `tag`：字符串，搜索的标签字符串。

**GET参数：**

* `page`：（可选）整数，显示赛事列表的第几页，默认为1。

### `GET /event/{eid:\w{24}}`

赛事详情页面，展示赛事的所有相关信息。

**RESTful参数：**

* `eid`：ObjectId，赛事ID。

**GET参数：**

* `page`：（可选）整数，显示赛事正在审核的报名者列表的第几页，默认为1。
* `page_approved`：（可选）整数，显示赛事已通过审核的报名者列表的第几页，默认为1。

### `POST /event/{eid:\w{24}}`

删除赛事。

**RESTful参数：**

* `eid`：ObjectId，赛事ID。

**GET参数：**

无

**POST参数：**

无

### `GET /event/add`

赛事添加页面。

**RESTful参数：**

无

**GET参数：**

无

### `POST /event/add`

赛事添加。

**RESTful参数：**

无

**GET参数：**

无

**POST参数：**

* `name`：字符串，赛事名称。
* `intro`：字符串，赛事简介。
* `creator_id`：ObjectId，赛事创建者ID。
* `begin_at`：datetime，赛事报名开始时间。
* `end_at`：datetime，赛事报名结束时间。
* `place`：字符串，赛事举办地点。
* `time`：字符串，赛事举办时间。
* `register_limit`：整数，赛事报名数限制。
* `show_list`：（可选）布尔，是否公布报名者列表，默认是不公布。
* `is_group`：（可选）布尔，是否以组队形式报名，默认是个人形式报名。
* `member_lb`：（可选）整数，若以组队形式报名，赛事队伍人数下限，默认是0。
* `member_ub`：（可选）整数，若以组队形式报名，赛事队伍人数上限，默认是0。
* `tags`：（可选）列表，赛事标签的列表集合，默认是空。
* `fields`：（可选）列表，赛事附加字段的列表集合，默认是空。

### `GET /event/{eid}/edit`

赛事修改页面。

**RESTful参数：**

* `eid`：ObjectId，赛事ID。

**GET参数：**

无

### `POST /event/{eid}/edit`

赛事修改。

**RESTful参数：**

* `eid`：ObjectId，赛事ID。

**GET参数：**

无

**POST参数：**

* `name`：字符串，赛事名称。
* `intro`：字符串，赛事简介。
* `creator_id`：ObjectId，赛事创建者ID。
* `begin_at`：datetime，赛事报名开始时间。
* `end_at`：datetime，赛事报名结束时间。
* `place`：字符串，赛事举办地点。
* `time`：字符串，赛事举办时间。
* `register_limit`：整数，赛事报名数限制。
* `show_list`：（可选）布尔，是否公布报名者列表，默认是不公布。
* `is_group`：（可选）布尔，是否以组队形式报名，默认是个人形式报名。
* `member_lb`：（可选）整数，若以组队形式报名，赛事队伍人数下限，默认是0。
* `member_ub`：（可选）整数，若以组队形式报名，赛事队伍人数上限，默认是0。
* `tags`：（可选）列表，赛事标签的列表集合，默认是空。
* `fields`：（可选）列表，赛事附加字段的列表集合，默认是空。

### `GET /event/{eid}/download`

报名表下载。

**RESTful参数：**

- `eid`：ObjectId，赛事ID。

**GET参数：**

无

### `GET /event/{eid}/advanced`

报名表下载定制页面。

**RESTful参数：**

- `eid`：ObjectId，赛事ID。

**GET参数：**

无

### `POST /event/{eid}/advanced`

报名表定制下载。

**RESTful参数：**

- `eid`：ObjectId，赛事ID。

**GET参数：**

无

**POST参数：**

- `field`：字符串，选择列。

## 赛事报名
主要实现在`handler/registration.py`。

### `GET /registration`

用户已发起的报名列表界面。

**RESTful参数：**

无

**GET参数：**

* `page`：正整数，显示用户报名列表的第几页。

### `POST /event/{eid}/register`

对某一赛事发起报名。

**RESTful参数：**

* `eid`：ObjectId，将要报名的赛事在数据库中的ID。

**POST参数：**

同模型层`add(...)`。

### `GET /event/{eid}/register_force`

由管理员替某一用户向某一赛事发起报名的界面。

**RESTful参数：**

* `eid`：ObjectId，将要报名的赛事在数据库中的ID。

**GET参数：**

无

### `POST /event/{eid}/register_force`

由管理员替某一用户向某一赛事发起报名。

**RESTful参数：**

* `eid`：ObjectId，将要报名的赛事在数据库中的ID。

**POST参数：**

* `username`：字符串，被代替报名的用户的用户名。
* `field`：字符串，报名表的所需信息。

### `POST /registration/{rid}/delete`

删除某一报名表。

**RESTful参数：**

* `rid`：ObjectId，将要删除的报名表在数据库中的ID。

**POST参数：**

无

### `GET /registration/{rid}/edit`

修改报名表的界面。

**RESTful参数：**

* `rid`：ObjectId，将要修改的报名表在数据库中的ID。

**GET参数：**

无

### `POST /registration/{rid}/edit`

由管理员替某一用户向某一赛事发起报名。

**RESTful参数：**

* `rid`：ObjectId，将要修改的报名表在数据库中的ID。

**POST参数：**

* `field`：字符串，报名表待修改内容的信息。
* `teammates`：字符串，若为团队报名，团队中队员的用户名。
* `team_leader`：字符串，若为团队报名，团队中队长的用户名。

### `GET /registration/{rid}`

报名表详情的界面。

**RESTful参数：**

* `rid`：ObjectId，报名表在数据库中的ID。

**GET参数：**

无

### `POST /registration/review`

审核报名。

**RESTful参数：**

* `rid`：ObjectId，报名表在数据库中的ID。

**GET参数：**

无

**POST参数：**

- `reply`：字符串，管理员回复。
- `status`：整数，审核结果。

## 用户消息提醒

主要实现在`handler/user.py`。

### `GET /user/message`

用户消息列表界面。

**RESTful参数：**

无

**GET参数：**
* `unread_only`：整数，是否为未读消息列表。0为否，1为是。
* `page`：正整数，显示用户列表的第几页。

### `GET /user/message/{mid}`

用户消息详情页面，将消息设为已读，并显示消息的具体内容，同时更新当前用户的未读消息数。

**RESTful参数：**

* `mid`：ObjectId，消息在数据库中的ID。

**GET参数：**

无

## 内容管理

主要实现在`handler/athlete.py`以及`handler/team.py`。

### `GET /athlete`

显示优秀运动员列表，每页20个。

**RESTful参数：**

无

**GET参数：**

* `page`：正整数，页码。

### `GET /athlete/add`

添加优秀运动员表单。

**RESTful参数：**

无

**GET参数：**

无

### `POST /athlete/add`

添加优秀运动员。

**RESTful参数：**

无

**GET参数：**

无

**POST参数：**

同模型层`add(...)`，但`type`取为`TYPE_ATHLETE`。

### `GET /athlete/{did}`

显示优秀运动员详细信息。

**RESTful参数：**

* `did`：优秀运动员ID。

**GET参数：**

无

### `GET /athlete/{did}/edit`

修改优秀运动员的页面。

**RESTful参数：**

* `did`：优秀运动员ID。

**GET参数：**

无

### `POST /athlete/{did}/edit`

修改优秀运动员。

**RESTful参数：**

* `did`：优秀运动员ID。

**GET参数：**

无

**POST参数：**

同模型层`edit(...)`，但`type`取为`TYPE_ATHLETE`。

### `GET /team`

显示系代表队列表，每页20个。

**RESTful参数：**

无

**GET参数：**

* `page`：正整数，页码。

### `GET /team/add`

添加系代表队表单。

**RESTful参数：**

无

**GET参数：**

无

### `POST /team/add`

添加系代表队。

**RESTful参数：**

无

**GET参数：**

无

**POST参数：**

同模型层`add(...)`，但`type`取为`TYPE_TEAM`。

### `GET /team/{did}`

显示系代表队详细信息。

**RESTful参数：**

* `did`：系代表队ID。

**GET参数：**

无

### `GET /team/{did}/edit`

修改系代表队的页面。

**RESTful参数：**

* `did`：系代表队ID。

**GET参数：**

无

### `POST /team/{did}/edit`

修改系代表队。

**RESTful参数：**

* `did`：系代表队ID。

**GET参数：**

无

**POST参数：**

同模型层`edit(...)`，但`type`取为`TYPE_TEAM`。


## 二维码生成

主要实现在`handler/misc.py`。


### `GET /qrcode`

生成二维码图像。

**RESTful参数：**

无

**GET参数：**

* `a`：字符串，二维码跳转地址。

# 前端用户界面设计

前端的框架直接复用一个开源项目vj4的前端框架，它设计美观，组件齐全，重点突出，表现力强。

请参见：[https://github.com/vijos/vj4/tree/master/vj4/ui](https://github.com/vijos/vj4/tree/master/vj4/ui)

# 文档修订历史

请参见git仓库。