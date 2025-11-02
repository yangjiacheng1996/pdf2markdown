# 工程技术标准

# 深圳证券交易所跨深沪港股票ETF业务之券商技术系统变更指南(Ver1.0)

![](images/302b5afd56f4bf13ecbceb89fe209b9d88659c16a4b40d230b34f780d937d70b.jpg)

深圳证券交易所中国结算深圳分公司

二〇二〇九月

关于本文档  

<table><tr><td colspan="2">文档名称</td><td colspan="3">深圳证券交易所跨深沪港股票ETF业务之券商技术系统变更指南</td></tr><tr><td colspan="2">说明</td><td colspan="3">为券商等相关单位进行跨深沪港股票ETF相关技术准备工作的指 南</td></tr><tr><td colspan="5">修订历史</td></tr><tr><td>日期</td><td colspan="2">版本</td><td>操作</td><td>说明</td></tr><tr><td>2020-09-21</td><td colspan="2">V1.0</td><td></td><td>初始版本</td></tr></table>

# 目录

# 一、说明

# 二、业务简介 1

2.1 跨深沪港股票 ETF 产品的定义 ..... 1  
2.2 跨深沪港股票 ETF 的认购 1  
2.3 跨深沪港股票ETF的交易 1  
2.4 跨深沪港股票 ETF 的申赎 1  
2.5 跨深沪港股票ETF的登记及相关业务 2

# 三、业务实现概况 2

# 四、清算交收 2

4.1 接口修订概述 2  
4.2清算明细库SJSMXn.DBF 3  
4.3 明细结果库SJSJG.DBF 6  
4.4 资金清算汇总库SJSQS.DBF 8  
4.5 资金变动库 SJSZJ.DBF. 9

# 五、跨深沪港ETF申赎模式优化上线切换指引 9

5.1 交易数据接口切换调整 9  
5.2 结算数据接口切换调整 10  
5.3业务暂停事项 10

# 六、联系方式 10

# 深圳证券交易所跨深沪港股票ETF业务之券商技术系

# 统变更指南

# 说明

为方便市场参与各方更好地完成“跨深沪港股票ETF产品”相关技术准备工作，深圳证券交易所（以下简称“深交所”）联合中国证券登记结算有限责任公司（以下简称“中国结算”）深圳分公司，制定本文档，供交易参与人和结算参与人及其IT供应商变更技术系统时参考。

深交所改造系统的宗旨：从技术上保障证券市场安全运行，同时，尽量减少系统改造对市场参与者带来的影响。

特别提示：如果业务规则及业务方案有所变更，本文档将做相应变更。

# 二、业务简介

# 2.1 跨深沪港股票ETF产品的定义

跨深沪港股票ETF，即跟踪股票指数成份证券包括深沪港交易所上市股票的ETF。跨深沪港股票ETF为跨市场股票ETF的特殊类型。

# 2.2 跨深沪港股票ETF的认购

跨深沪港股票ETF可以采用网上现金认购、网下现金认购及网下组合证券认购三种方式。网上现金认购采用目前LOF的连续发行系统处理；网下现金认购由基金管理人组织办理；网下组合证券认购则由基金管理人参照现有跨市场股票ETF网下组合证券认购流程，向中国结算总部基金部申请以深沪组合证券（但不包括港市组合证券）办理认购过户。

# 2.3 跨深沪港股票ETF的交易

跨深沪港股票ETF的交易，采用多边净额担保交收模式。

# 2.4 跨深沪港股票ETF的申赎

跨深沪港股票ETF的组合证券包括深沪港交易所上市股票，其中深市组合证

券部分采用实物申赎，非深市组合证券部分（沪市组合证券及港市组合证券部分）均采用全额现金替代申赎，上述申赎涉及的对价采用的结算安排为：

a、申购赎回涉及的ETF份额、深市组合证券及其现金替代、沪市组合证券的现金替代，以及申购涉及的港市组合证券的现金替代，均采用多边净额担保交收模式；  
b、赎回涉及的港市组合证券的现金替代，以及申购赎回涉及的现金差额、现金替代退补款，则采用代收代付模式。

注：中国结算总部TA系统不对跨深沪港股票ETF开通场外申购赎回权限。

# 2.5 跨深沪港股票ETF的登记及相关业务

跨深沪港股票ETF的登记及相关业务，如分红派息、股东名册、质押登记、非交易过户、司法协助等，处理方式均与跨市场股票ETF相同。

# 三、 业务实现概况

跨深沪港股票ETF产品的证券类别为跨市场股票ETF（类别代码：15），相关PCF文件格式、委托/回报接口、处理方式同现有跨市场股票ETF。

对于跨市场股票ETF的PCF文件（“静态交易参考信息”的“ETF实时申购赎回业务参考信息”）中虚拟成份证券159900记录的申购替代金额字段表示所有非深市成份证券现金替代的总金额（如对于包含深市成份证券、沪市成份证券及港股通标的的跨市场股票ETF，则申购替代金额表示沪市成份证券及港股通标的现金替代总金额）；159900的赎回替代金额字段，表示所有沪市成份证券现金替代的总金额(如对于包含深市成份证券、沪市成份证券及港股通标的的跨市场股票ETF，则赎回替代金额表示沪市成份证券的现金替代总金额)。

# 四、清算交收

# 4.1 接口修订概述

(1) 跨深沪港股票 ETF 产品归入跨市场  $\mathrm{ETF}^{2}$ , 采用与跨市场股票 ETF 相同的 ETF 子类别, 证券类别编码为 ‘EF’, 证券子类别编码为 ‘3’。其中证券类别及证券子类别含义可查看《深市登记结算数据接口规范 (结算参与人版)》附件二

“证券类别子类含义表”，或查看 SJSGB.DBF 中 GBLB 为 ‘ZL’ 及 ‘ZZ’ 的数据。

证券类别子类含义表  

<table><tr><td>证券类别</td><td>证券子类</td><td>子类简称</td></tr><tr><td>EF</td><td>3</td><td>跨市场 ETF</td></tr></table>

(2）跨深沪港股票ETF认购的处理，与现有跨市场ETF相同。  
(3) 跨深沪港股票 ETF 交易的处理，与现有跨市场 ETF 相同。  
（4）跨深沪港股票ETF申赎的处理，除了增加对赎回涉及的港市组合证券的现金替代进行代收代付处理外，其他处理与现有跨市场ETF相同。具体详细见4.2~4.5章节的说明。  
(5) 跨深沪港股票 ETF 登记及相关业务的处理（如分红派息、股东名册、质押登记、非交易过户、司法协助等），均与现有跨市场股票 ETF 相同。

# 4.2 清算明细库 SJSMXn.DBF

# 4.2.1 SJSMX1.DBF

(1) SJSMX1.DBF 中, 跨深沪港股票 ETF 的实物申购份额 (SGSF)、实物申购现金替代 (SGSZ)、实物申购组合券 (SGSQ)、实物赎回份额 (SHSF)、实物赎回现金替代 (SHSZ)、实物赎回组合券 (SHSQ), 采用与现有跨市场 ETF 相同的处理方式。业务类别含义参见下表:

SJSMX1.DBF业务类别含义表  

<table><tr><td>业务类别</td><td>业务类别含义</td></tr><tr><td>SGSF</td><td>实物申购份额，包括单市场ETF、实物债券ETF、跨市场ETF</td></tr><tr><td>SGSZ</td><td>实物申购现金替代，包括单市场ETF、实物债券ETF、跨市场ETF</td></tr><tr><td>SGSQ</td><td>实物申购组合券，包括单市场ETF、实物债券ETF、跨市场ETF</td></tr><tr><td>SHSF</td><td>实物赎回份额，包括单市场ETF、实物债券ETF、跨市场ETF</td></tr><tr><td>SHSZ</td><td>实物赎回现金替代，包括单市场ETF、实物债券ETF、跨市场ETF</td></tr><tr><td>SHSQ</td><td>赎回回组合券，包括单市场ETF、实物债券ETF、跨市场ETF</td></tr></table>

跨市场ETF实物申赎现金替代的说明：

1）SGSZ实物申购现金替代中，159900虚拟组合券记录表示非深市（即沪港两市）组合券现金替代的总金额。  
2）SHSZ实物赎回现金替代中，159900虚拟组合券记录仅表示沪市组合券的替代金额。

注：基金管理人于  $\mathrm{T} + \mathrm{N}$  日，通过D-COM上传港市组合券赎回现金替代，相关代收付清算明细在当日SJSMX2.DBF的业务类别SHDZ中体现。

# 4.2.2 SJSMX2.DBF

（1）SJSMX2.DBF中，跨深沪港股票ETF申赎的税费（SGFY、SHFY）、现金差额（EFXC）、多退少补（EFTB），采用与现有跨市场ETF相同的处理方式。

SJSMX2.DBF业务类别含义表  

<table><tr><td>业务类别</td><td>业务类别含义</td></tr><tr><td>SGFY</td><td>ETF 申购税费、组合券过户费</td></tr><tr><td>SHFY</td><td>ETF 赎回税费、组合券过户费</td></tr><tr><td>SGDZ</td><td>通过中国结算总部申购的 ETF 现金替代</td></tr><tr><td>SHDZ</td><td>ETF 实物赎回现金替代-代收代付（包括通过中国结算总部赎回的 ETF 现金替代以及跨市场 ETF 港市组合券赎回现金替代）</td></tr><tr><td>EFXC</td><td>ETF 申购赎回现金差额</td></tr><tr><td>EFTB</td><td>ETF 申购赎回现金替代多退少补</td></tr></table>

(2) SJSMX2.DBF 中, 跨深沪港股票 ETF 赎回港市组合券现金替代通过 SHDZ 体现, 其交易方式 (MXJYFS 字段) 为 03 (表示经深交所申报的非交易业务)。含义修改如下表:

<table><tr><td rowspan="2">字段名</td><td colspan="2">业务类别</td></tr><tr><td>SGDZ(ETF 实物申购现金替代-代收代付(包括通过中国结算总部申购的 ETF 现金替代))</td><td>SHDZ(ETF 实物赎回现金替代-代收代付(包括通过中国结算总部赎回的 ETF 现金替代以及跨市场 ETF 港市组合券赎回现金替代)</td></tr><tr><td>MXJSZH</td><td>结算账号</td><td>结算账号</td></tr><tr><td>MXBFZH</td><td>备付金账户</td><td>备付金账户</td></tr><tr><td>MXSJLX</td><td>‘01'</td><td>‘01'</td></tr><tr><td>MXYWLB</td><td>'SGDZ'</td><td>'SHDZ'</td></tr><tr><td>MXZQDM</td><td>ETF 代码</td><td>ETF 代码</td></tr><tr><td>MXJYDY</td><td>交易单元</td><td>交易单元</td></tr><tr><td>MXTGDY</td><td>托管单元</td><td>托管单元</td></tr><tr><td>MXZQZH</td><td>证券账户</td><td>证券账户</td></tr><tr><td>MXDDBH</td><td>订单编号</td><td>订单编号</td></tr><tr><td>MXYYB</td><td>营业部代码</td><td>营业部代码</td></tr><tr><td>MXZXBH</td><td></td><td>执行编号(仅跨市场 ETF 港市组合券赎回现金替代填写)</td></tr><tr><td>MXYWLSH</td><td>业务流水号</td><td>业务流水号</td></tr><tr><td>MXCJSL</td><td></td><td></td></tr><tr><td>MXQSSL</td><td></td><td></td></tr><tr><td>MXCJJG</td><td></td><td></td></tr><tr><td>MXQSJJG</td><td></td><td></td></tr><tr><td>MXXYJY</td><td></td><td></td></tr><tr><td>MXPCBS</td><td></td><td></td></tr><tr><td>MXZQLB</td><td>‘EF’</td><td>‘EF’</td></tr><tr><td>MXZQZL</td><td>证券子类别</td><td>证券子类别</td></tr><tr><td>MXGFXZ</td><td></td><td></td></tr><tr><td>MXJSFS</td><td>‘Z’</td><td>‘Z’</td></tr><tr><td>MXHBDH</td><td>货币代号</td><td>货币代号</td></tr><tr><td>MXQSBJ</td><td>负数,应付申购现金替代</td><td>正数,应收赎回现金替代</td></tr><tr><td>MXYHS</td><td></td><td></td></tr><tr><td>MXJYJSF</td><td></td><td></td></tr><tr><td>MXJGGF</td><td></td><td></td></tr><tr><td>MXGHF</td><td></td><td></td></tr><tr><td>MXJSF</td><td></td><td></td></tr><tr><td>MXSXF</td><td></td><td></td></tr><tr><td>MXQSYJ</td><td></td><td></td></tr><tr><td>MXQTFY</td><td></td><td></td></tr><tr><td>MXZJJE</td><td></td><td></td></tr><tr><td>MXSFJE</td><td>负数,应付申购现金替代</td><td>正数,应收赎回现金替代</td></tr><tr><td>MXCJRQ</td><td>成交日期</td><td>成交日期</td></tr><tr><td>MXQSRQ</td><td>T 日</td><td>T 日</td></tr><tr><td>MXJSRQ</td><td>T+1 日</td><td>T+1 日</td></tr><tr><td>MXFSRQ</td><td>T 日</td><td>T 日</td></tr><tr><td>MXQTRQ</td><td></td><td></td></tr><tr><td>MXSCDM</td><td></td><td></td></tr><tr><td>MXJYFS</td><td>‘05’</td><td>‘05'或‘03'</td></tr><tr><td>MXZQDM2</td><td>组合券代码(若基金公司不提供,可能为空)</td><td>组合券代码(若基金公司不提供,可能为空)</td></tr><tr><td>MXTGDY2</td><td></td><td></td></tr><tr><td>MXDDBH2</td><td></td><td></td></tr><tr><td>MXCWDH</td><td></td><td></td></tr><tr><td>MXPPHM</td><td></td><td></td></tr><tr><td>MXFJSM</td><td></td><td></td></tr><tr><td>MXBYBZ</td><td></td><td></td></tr></table>

# 4.3 明细结果库SJSJG.DBF

(1) 跨深沪港股票 ETF 申赎代收代付业务的交收结果在 SJSJG 中体现，涉及的业务类别含义如下表：

SJSJG.DBF业务类别表  

<table><tr><td>接口业务
类别</td><td>业务类别含义</td></tr><tr><td>SHDZ</td><td>ETF 实物赎回现金替代-代收代付（包括通过中国结算总部赎回的ETF现金替代以及跨市场ETF港市组合券赎回现金替代）</td></tr><tr><td>EFXC</td><td>ETF申购赎回现金差额</td></tr><tr><td>EFTB</td><td>ETF申购赎回现金替代多退少补</td></tr></table>

(2)SJSJG.DBF中,跨深沪港股票ETF赎回港市成份证券现金替代通过SHDZ体现,其交易方式(JGJYFS字段)为03(表示经深交所申报的非交易业务),含义修改如下表:

<table><tr><td rowspan="2">字段名</td><td colspan="2">业务类别</td></tr><tr><td>SGDZ (ETF 实物申购现金替代-代收代付(包括通过中国结算总部申购的 ETF 现金替代))</td><td>SHDZ (ETF 实物赎回现金替代-代收代付(包括通过中国结算总部赎回的 ETF 现金替代以及跨市场 ETF 港市组合券赎回现金替代)</td></tr><tr><td>JGJSZH</td><td>结算账号</td><td>结算账号</td></tr><tr><td>JGBFZH</td><td>备付金账户</td><td>备付金账户</td></tr><tr><td>JGSJLX</td><td>‘01’</td><td>‘01’</td></tr><tr><td>JGYWLB</td><td>‘SGDZ’</td><td>‘SHDZ’</td></tr><tr><td>JGZQDM</td><td>ETF 代码</td><td>ETF 代码</td></tr><tr><td>JGJYDY</td><td>交易单元</td><td>交易单元</td></tr><tr><td>JGTGDY</td><td>托管单元</td><td>托管单元</td></tr><tr><td>JGZQZH</td><td>证券账户</td><td>证券账户</td></tr><tr><td>JGDBHB</td><td>订单编号</td><td>订单编号</td></tr><tr><td>JGYYB</td><td></td><td></td></tr><tr><td>JGZXBH</td><td></td><td>执行编号
(仅跨市场ETF港市组合券赎回现金替代填写)</td></tr><tr><td>JGYWLSH</td><td>业务流水号</td><td>业务流水号</td></tr><tr><td>JGCJSL</td><td></td><td></td></tr><tr><td>JGQSSL</td><td></td><td></td></tr><tr><td>JGJSSL</td><td></td><td></td></tr><tr><td>JGCJJG</td><td></td><td></td></tr><tr><td>JGQSJJG</td><td></td><td></td></tr><tr><td>JGXYJJ</td><td></td><td></td></tr><tr><td>JGPCBS</td><td></td><td></td></tr><tr><td>JGZQLB</td><td>‘EF’</td><td>‘EF’</td></tr><tr><td>JGZQZL</td><td>证券子类别</td><td>证券子类别</td></tr><tr><td>JGGFXZ</td><td></td><td></td></tr><tr><td>JGLTLX</td><td></td><td></td></tr><tr><td>JGJSFS</td><td>‘Z’</td><td>‘Z’</td></tr><tr><td>JGHBDH</td><td>货币代号</td><td>货币代号</td></tr><tr><td>JGQSBJ</td><td>负数,应付申购现金替代</td><td>正数,应收赎回现金替代</td></tr><tr><td>JGYHS</td><td></td><td></td></tr><tr><td>JGJYJSF</td><td></td><td></td></tr><tr><td>JGJGGF</td><td></td><td></td></tr><tr><td>JGGHF</td><td></td><td></td></tr><tr><td>JGJSF</td><td></td><td></td></tr><tr><td>JGSXF</td><td></td><td></td></tr><tr><td>JGQSYJ</td><td></td><td></td></tr><tr><td>JGQTFY</td><td></td><td></td></tr><tr><td>JGZJJJE</td><td></td><td></td></tr><tr><td>JGSFJE</td><td>负数,应付申购现金替代</td><td>正数,应收赎回现金替代</td></tr><tr><td>JGJSBZ</td><td>‘Y’或‘N’</td><td>‘Y’或‘N’</td></tr><tr><td>JGZYDH</td><td>若JGJSBZ为‘N’,则是错误代号</td><td>若JGJSBZ为‘N’,则是错误代号</td></tr><tr><td>JGCJRQ</td><td>成交日期</td><td>成交日期</td></tr><tr><td>JGQSRQ</td><td>T-1日</td><td>T-1日</td></tr><tr><td>JGJSRQ</td><td>T日</td><td>T日</td></tr><tr><td>JGFSRQ</td><td>T日</td><td>T日</td></tr><tr><td>JGQTRQ</td><td></td><td></td></tr><tr><td>JGSCDM</td><td></td><td></td></tr><tr><td>JGJYFS</td><td>‘05’</td><td>‘05’或‘03’</td></tr><tr><td>JGZQDM2</td><td>组合券代码（如基金公司不提供，则为空）</td><td>组合券代码（如基金公司不提供，则为空）</td></tr><tr><td>JGTGDY2</td><td></td><td></td></tr><tr><td>JGDDBH2</td><td></td><td></td></tr><tr><td>JGFJSM</td><td></td><td></td></tr><tr><td>JGBYBZ</td><td></td><td></td></tr></table>

# 4.4 资金清算汇总库SJSQS.DBF

（1）SJSQS.DBF中，涉及跨市场ETF（含跨深沪港股票ETF）申赎的业务类别含义如下表：

SJSQS.DBF业务含义表  

<table><tr><td>业务类别</td><td>相应业务含义</td><td>说明</td></tr><tr><td>SGSZ</td><td>ETF 实物申购现金替代</td><td>QSZQDM为 ETF 证券代码（单市场 ETF、实物债券 ETF、跨市场 ETF）。成交日期=清算日期，交收日期=清算日期+1。</td></tr><tr><td>SHSZ</td><td>ETF 实物赎回现金替代</td><td>QSZQDM为 ETF 证券代码（单市场 ETF、实物债券 ETF、跨市场 ETF）。成交日期=清算日期，交收日期=清算日期+1。</td></tr><tr><td>SHDZ</td><td>ETF 实物赎回现金替代-代收代付（包括通过中国结算总部赎回的 ETF 现金替代以及跨市场 ETF 港市组合券 赎回现金替代）</td><td>对于代收代付（跨市场 ETF 实物赎回），成交日期为空，清算日期为当日，交收日期=清算日期+1；对于含代收代付，按“证券”+“托管单元”，分买入和卖出各下发一条记录。买入记录中的卖出金额为0，卖出记录中的买入金额为0。</td></tr><tr><td>SGFY</td><td>ETF 申购税费、组合券过户费</td><td>QSZQDM为 ETF 证券代码。成交日期=清算日期-1，交收日期=清算日期+1。本记录为上个交易日申购业务相关的费用。</td></tr><tr><td>SHFY</td><td>ETF 赎回税费、组合券过户费</td><td>QSZQDM为 ETF 证券代码。成交日期=清算日期-1，交收日期=清算日期+1。本记录为上个交易日赎回业务相关的费用。</td></tr><tr><td>EFXC</td><td>ETF 申购赎回现金差额</td><td>QSZQDM为 ETF 证券代码。成交日期为空，清算日期为当日，交收日期=清算日期+1。买入金额为补款金额，卖出金额为退款金额。对于某“证券”+“托管单元”，分买入和卖出各下发一条记录。买入记录中的卖出金额为0，卖出记录中的买入金额为0。</td></tr><tr><td>EFTB</td><td>ETF 申购赎回现金</td><td>QSZQDM为 ETF 证券代码。</td></tr><tr><td></td><td>替代多退少补</td><td>成交日期为空，清算日期为当日，交收日期=清算日期+1。买入金额为补款金额，卖出金额表示退款金额。对于某“证券”+“托管单元”，分买入和卖出各下发一条记录。买入记录中的卖出金额为0，卖出记录中的买入金额为0。</td></tr></table>

# 4.5 资金变动库SJSZJ.DBF

（1）SJSZJ.DBF中，涉及跨市场ETF（含跨深沪港股票ETF）申赎的业务类别含义如下表：

SJSZJ.DBF中业务类别含义表  

<table><tr><td>ZJYWLB</td><td>业务类别含义</td><td>ZJZQDM</td></tr><tr><td>SGFY</td><td>ETF 申购税费、组合券过户费</td><td>证券代码</td></tr><tr><td>SGSZ</td><td>ETF 申购实物现金替代</td><td>证券代码</td></tr><tr><td>SHFY</td><td>ETF 赎回税费、组合券过户费</td><td>证券代码</td></tr><tr><td>SHSZ</td><td>ETF 实物赎回现金替代</td><td>证券代码</td></tr><tr><td>SHDZ</td><td>ETF 实物赎回现金替代-代收代付(包括通过中国结算总部赎回的 ETF 现金替代以及跨市场 ETF 港市组合券 赎回现金替代)</td><td>证券代码</td></tr><tr><td>EFTB</td><td>ETF 申购赎回现金替代多退少补</td><td>证券代码</td></tr><tr><td>EFXC</td><td>ETF 申购赎回现金差额</td><td>证券代码</td></tr></table>

# 五、 跨深沪港ETF申赎模式优化上线切换指引

相关基金管理人需要按如下指引，在跨深沪港股票ETF申赎模式优化项目上线启用日（S日，XX月XX日）进行系统切换，并通知相关PD券商、结算参与人一同做好系统切换工作。

# 5.1 交易数据接口切换调整

拟切换ETF的证券类别由跨境ETF（类别代码：16）调整为跨市场股票ETF

（类别代码：15）。

# 5.2 结算数据接口切换调整

1）跨深沪港ETF证券代码与证券类别（子类别）对应关系调整

拟切换ETF的证券类别代码仍为EF；证券子类别由跨境ETF（证券子类别：2）调整为跨市场ETF（证券子类别：3)。证券代码与证券类别（及子类别）的对应关系，详见SJSGB.DBF中  $\mathrm{GBLB} =$  ‘ZQ’的相关记录。

2）跨深沪港ETF在途业务数据切换

拟切换ETF的约定购回业务（业务类别为YDCS、YDDQ)，在项目上线启用日前一交易日（S-1日）的清算明细数据接口SJSMX1.DBF中，其证券子类别字段（MXZQZL）填写为2；对应的交收结果在项目上线启用日（S日）的交收结果明细接口SJSJG.DBF中证券子类别字段（JGZQZL）会调整成为3。

# 5.3 业务暂停事项

为便于市场切换处理，拟切换的ETF将在项目上线启用日前一交易日(S-1日，XX月XX日）暂停一个交易日的管理人代收代付业务的申报，代收代付业务包括现金差额、多退少补、赎回的现金替代。

对于业务启用日前达成的申赎，ETF 管理人可与市场参与各方在场外了结对应的代收代付业务，或在项目上线后通过代收代付接口（接口业务类别为 LF、LG、LH）在 D-COM 上进行申报，请市场参与各方妥善做好相关衔接工作。

# 六、联系方式

业务：0755-88668839（交易）

0755-21899269（结算）

技术：0755-88668728（交易）

Email: ssegcb@szse.cn

0755-25946080（结算）

Email: szjsb@chinaclear.com.cn