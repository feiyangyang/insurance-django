# 财险人工核保流程培训图

本文档用于培训讲解财险人工核保系统的业务流程和功能模块。

## 推荐培训版本

已新增更容易看懂的可视化 UI 版：

[打开 training_ui.html](training_ui.html)

建议培训、演示、截图时优先使用 `docs/training_ui.html`，该页面用卡片、流程箭头、角色泳道和模块矩阵表达业务流程；本文档保留 Mermaid 版本，便于技术人员维护和复制。

## 一、业务主流程图

```mermaid
flowchart TD
    A[客户建档] --> B[新增投保申请]
    B --> C[录入风险评估]
    C --> D[创建核保任务]
    D --> E[核保人员查看详情]
    E --> F{提交核保结论}

    F -->|通过| G[申请状态变更为通过]
    G --> H[生成正式保单]
    H --> I[保单管理]

    F -->|拒保| J[申请状态变更为拒保]
    F -->|补充资料| K[申请状态变更为补充资料]
    F -->|加费/除外/延期| L[申请保持核保中]

    F --> M[写入审核记录]
    H --> N[写入生成保单记录]

    M --> O[审核记录留痕]
    N --> O
```

## 二、核保任务处理流程图

```mermaid
flowchart TD
    A[进入核保任务列表] --> B[选择任务并进入详情页]
    B --> C[查看投保申请信息]
    B --> D[查看风险评估信息]
    B --> E[查看健康/风险告知]

    C --> F[填写核保结论]
    D --> F
    E --> F

    F --> G{结论类型}
    G -->|通过| H[任务状态: 通过]
    G -->|拒保| I[任务状态: 拒保]
    G -->|补充资料| J[任务状态: 补充资料]
    G -->|加费| K[任务状态: 加费]
    G -->|除外| L[任务状态: 除外]
    G -->|延期| M[任务状态: 延期]

    H --> N[同步投保申请状态]
    I --> N
    J --> N
    K --> N
    L --> N
    M --> N

    N --> O[生成审核记录]
    H --> P{是否已生成保单}
    P -->|否| Q[点击生成保单]
    Q --> R[生成 Policy]
    R --> S[生成保单留痕]
    P -->|是| T[展示已生成保单号]
```

## 三、数据对象关系图

```mermaid
erDiagram
    CUSTOMER ||--o{ INSURANCE_APPLICATION : owns
    INSURANCE_APPLICATION ||--o| RISK_ASSESSMENT : has
    INSURANCE_APPLICATION ||--o{ UNDERWRITING_TASK : creates
    UNDERWRITING_TASK ||--o{ AUDIT_LOG : records
    INSURANCE_APPLICATION ||--o| POLICY : generates
    CUSTOMER ||--o{ POLICY : owns
    POLICY ||--o{ UNDERWRITING_TASK : legacy_or_related

    CUSTOMER {
        string customer_type
        string name
        string company_name
        string phone
        string contact_person
    }

    INSURANCE_APPLICATION {
        string application_no
        string insurance_type
        string subject_name
        decimal insured_amount
        decimal estimated_premium
        string status
    }

    RISK_ASSESSMENT {
        string risk_level
        int risk_score
        text risk_factors
        text conclusion
    }

    UNDERWRITING_TASK {
        string task_no
        string risk_level
        string status
        string assigned_to
        text remark
    }

    AUDIT_LOG {
        string action
        string operator
        string from_status
        string to_status
        string decision
    }

    POLICY {
        string policy_no
        string proposal_no
        string product_name
        decimal premium
        decimal insured_amount
        string status
    }
```

## 四、功能模块脑图

```mermaid
mindmap
  root((财险人工核保系统))
    工作台
      流程统计
      风险看板
      最新核保任务
      最新投保申请
    客户管理
      个人客户
        姓名
        性别
        年龄
        手机号
        身份证号
      企业客户
        企业名称
        统一社会信用代码
        联系人
        联系电话
        注册地址
    投保申请
      申请号
      客户
      险种类型
      保险标的
      保险金额
      预估保费
      申请状态
    风险评估
      风险等级
      风险评分
      风险因素
      评估结论
    核保任务
      创建任务
      配置任务
      查看详情
      提交结论
      同步申请状态
    审核记录
      结论留痕
      状态变化
      操作人
      操作时间
      生成保单记录
    保单管理
      手工维护保单
      核保通过生成保单
      来源申请关联
      保单状态
    系统检测
      数据库引擎
      DATABASE_URL
      核心数据量
```

## 五、角色培训视角

```mermaid
flowchart LR
    A[业务录入人员] --> A1[维护客户]
    A --> A2[新增投保申请]

    B[风险评估人员] --> B1[查看投保申请]
    B --> B2[录入风险评估]

    C[核保人员] --> C1[创建/领取核保任务]
    C --> C2[查看核保详情]
    C --> C3[提交核保结论]

    D[复核/管理人员] --> D1[查看审核记录]
    D --> D2[查看工作台统计]
    D --> D3[查看风险看板]

    E[出单人员] --> E1[核保通过后生成保单]
    E --> E2[维护保单信息]
```

## 六、培训讲解顺序

1. 先讲客户：个人客户和企业客户的区别。
2. 再讲投保申请：申请是财险核保流程的业务主单。
3. 再讲风险评估：风险评估为核保任务提供输入。
4. 再讲核保任务：核保人员在详情页查看信息并提交结论。
5. 再讲审核记录：每次关键操作都会留下记录。
6. 最后讲保单生成：只有核保通过后，才从投保申请生成正式保单。
