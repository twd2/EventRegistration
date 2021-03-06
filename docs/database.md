# 数据库设计

这份文档描述了本项目最底层数据库的设计，更高层的设计都基于此。

值得说明的是，本项目使用MongoDB作为系统的数据库。MongoDB是一个高性能、易于开发、易于部署、支持分布式的文档型数据库。在MongoDB中，集合（collection）的概念类似于SQL数据库中表的概念。集合中存放的是文档（document），对应表中存放的行。这份文档说明了每个集合的作用，以及每个集合中每个字段的名称及含义。

## 规范

- 集合名字用复数，集合中的文档用单数。 例如：`user`是users集合中的一个文档。

## 集合

### users

这个集合存放用户基本信息。

- `_id`：MongoId，唯一标识符。*唯一索引*
- `username`：字符串，用户名或者Accounts9 API提供的标识符。*唯一索引*
- `username_lower`：字符串，`username`字段的小写形式，用于不区分大小写地查找用户。*索引*
- `role`：整数，用户的角色：普通用户（1000），普通管理员（100），超级管理员（0）。更小的整数值意味着更多的权限，类似x86的ring。
- `name`：字符串，用户的真实姓名。*索引*
- `mail`：字符串，用户电子邮箱。审核报名申请之后会向此邮箱发送电子邮件。
- 扩展字段：用户个人信息以及联系方式。是每个赛事都需要记录的最基本的信息。
  - `student_id`：字符串，学号。
  - `chinese_id`：字符串，证件号。
  - `gender`：字符串，性别。
  - `birthday`：8位的字符串，生日。
  - `degree`：字符串，攻读学位。
  - `department`：字符串，院系。
  - `class`：字符串，班级。
  - `size`：字符串，服装尺寸。
  - `mobile`：字符串，手机号码。
  - `room`：字符串，宿舍房间号。
- `enable_at`：时间，激活时间，为None则表示用户未激活。当用户第一次登录时会创建一条此字段为None的记录；通过填写个人信息激活后，此字段设定为激活的时间。
- `raw`: 对象，API返回的原始用户信息。

### events

这个集合存放赛事信息。

- `_id`：MongoId，唯一标识符。这个字段的类型是MongoId，隐含了创建时间。*唯一索引*
- `name`：字符串，赛事的名字。
- `intro`：字符串，赛事简介，显示时支持Markdown渲染。
- `creator_id`：MongoId，创建者（`user`）的`_id`。*添加索引以方便搜索*
- `register_limit`：整数，报名（人/组）数限制。
- `is_group`：布尔，是否为团队比赛。
- `member_lb`：（当`is_group`为真时必填）整数，每组报名人数下界。
- `member_ub`：（当`is_group`为真时必填）整数，每组报名人数上界。
- `tags`：字符串数组，赛事的年份、类别等分类标签或标记。*添加索引以方便搜索*
- `begin_at`：时间，赛事**报名**开始时间。*添加索引以方便检索最近赛事*
- `end_at`：时间，赛事**报名**截止时间。
- `num_view`：整数，查看次数。每次被查看增加1。*添加索引以方便检索热门赛事*
- `num_register`：整数，报名次数。 *需要确保该字段的值和registrations集合中`event_id`等于此`_id`的记录的条数相等*
- `fields`：对象数组，附加的字段。

**`fields`的补充说明**

这个数组每一个元素描述了一组附加字段，例如：

```json
[
    {
        "type": 0,
        "name": "大学生平均学分绩点"
    },
    {
        "type": 0,
        "name": "参赛理由"
    }
]
```

表示此赛事需要两个额外的字段：

- 字符串（`0`）类型，表单中显示为“大学生平均学分绩点”。
- 字符串（`0`）类型，表单中显示为“参赛理由”。

### registrations

这个集合存放用户对于赛事的报名信息。

- `_id`：MongoId，唯一标识符。这个字段的类型是MongoId，隐含了创建（即申请报名）时间。*唯一索引*
- `creator_id`：MongoId，创建者（即报名者）（`user`）的`_id`。 *索引*
- `forcer_id`：MongoId，创建该报名的管理员（`user`）的`_id`。 *赛事为团队赛事时必填*
- `team_leader` : MongoID，报名团队比赛时的队长（`user`）的`_id`。 *赛事为团队赛事时必填*
- `team_ids` : MongoId数组，报名团队比赛时添加的队员(`user`)的`_id`。 *赛事为团队赛事时必填*
- `event_id`：MongoId，赛事（`event`）的`_id`。 *索引*
- `fields`：对象数组，附加的字段。
- `status`：整数，状态：等待（`0`），未通过（Rejected，`1`），已通过（Approved，`2`）。 *索引*
- `reply`：字符串，审核附言。
- `result`：字符串，比赛结果（成绩）。
- `rank`：整数，比赛名次。

另外，`(creator_id, event_id)`有唯一索引，确保每个用户对特定赛事最多只能报名一次。

**`fields`的补充说明**

这个数组每一个元素包含`name`和`value`两个字段，分别描述了每一个附加字段的名字和具体取值，考虑上面events集合`fields`的例子，对应于这条记录：

```json
[
    {
        "name": "大学生平均学分绩点",
        "value": "4.1"
    },
    {
        "name": "参赛理由",
        "value": "我强"
    }
]
```

表示此报名申请有两个额外的字段：

- 大学生平均学分绩点：4.1
- 参赛理由：我强。

### messages

这个集合存放用户收到的短消息。

- `_id`：MongoId，唯一标识符。这个字段的类型是MongoId，隐含了创建（即发送）时间。*唯一索引*
- `sender_id`：MongoId，发送者（`user`）的`_id`。 *索引*
- `receiver_id`：MongoId，接收者（`user`）的`_id`。 *索引*
- `title`：字符串，标题。
- `content`：字符串，内容。
- `read`：布尔，是否已读。 *索引*

### oplog

这个集合存放所有操作日志。

- `_id`：MongoId，唯一标识符。这个字段的类型是MongoId，隐含了创建（即操作）时间。*唯一索引*
- `creator_id`：MongoId，操作人（`user`）的`_id`。 *索引*
- `type`：整数，操作类型，10表示删除赛事，20表示取消报名，30表示删除文档。
- `edoc`：（可选）对象，被操作的赛事。
- `rdoc`：（可选）对象，被操作的报名。
- `ddoc`：（可选）对象，被操作的文档。

### documents

这个集合存放文档（优秀运动员以及系代表队）。

- `_id`：MongoId，唯一标识符。这个字段的类型是MongoId，隐含了创建时间。*唯一索引*
- `type`：整数，类型，0表示优秀运动员，1表示系代表队。 *添加索引以方便检索*
- `name`：字符串，优秀运动员或系代表队的名字。
- `num_view`：整数，查看次数。
- 其他字段：优秀运动员或者系代表队特定的字段。
  - 对于优秀运动员：
    - `year`：字符串，入选年份。
    - `gender`：字符串，性别。
    - `grade`：字符串，级数。
    - `class`：字符串，班级。
    - `subject`：字符串，主要项目。
    - `link`：字符串，访谈记录链接。
    - `bio`：字符串，个人简介。
    - `honor`：字符串，个人荣誉。
    - `images_text`：字符串，个人风采图片链接。
  - 对于系代表队：
    - `bio`：字符串，队伍简介。
    - `instructor`：字符串，教练。
    - `leader`：字符串，队长。
    - `members`：字符串，队员。
    - `images_text`：字符串，队伍风采图片链接。


## 文档修订历史

请参见git仓库。