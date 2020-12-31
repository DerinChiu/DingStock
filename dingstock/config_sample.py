# 股票设置
STOCK_CONFIG = [
    {
        'symbol': 'SH000001',      # 你关注的股票代码 SH/SZ******
        'notify_amp': 0.2,         # 当日波动率(百分比)到达此值时发送提醒
        'strong_notifications': [  # 强提醒（@你）
            {'threshold': 2, 'repeat': True, 'repeat_min_interval': 600},  # 当日波动率超过(+-)2%时循环(repeat为True)提醒，两次提醒最小间隔600秒
            {'threshold': 5, 'repeat': True, 'repeat_min_interval': 600},
            {'threshold': 8, 'repeat': True, 'repeat_min_interval': 600}
        ],
        'holder': '13888888888',   # 你的钉钉手机号，用于信息中@强提醒。（钉钉机器人接口官方要求）
        'holds': [                 # 持仓。volume：仓位  quote：仓位成本单价
            {'volume': 3000, 'quote': 11.8},
            {'volume': -500, 'quote': 12.8},
        ],
    },
    {
        # 另一只股票
        ...
    }
]

# 钉钉相关设置
DING_CONFIG = [
    {
        'webhook': 'replaces with your webhook',
        # 'key': '[replaces with your key]'  # (若选择加签方式请提供)SEC开头的key
    }
]
