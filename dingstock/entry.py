from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.triggers.combining import AndTrigger
# from apscheduler.triggers.cron import CronTrigger
# from apscheduler.triggers.interval import IntervalTrigger

from base import DingManager, StockManager

# 复合trigger目前工作不正常 https://github.com/agronholm/apscheduler/issues/281
# trigger = AndTrigger([
#     CronTrigger(day_of_week='mon-fri', hour='9-12,13-20', minute='*', second='*'),
#     IntervalTrigger(seconds=3)
# ])


def __sche_stock():
    print('__sche_stock ran...')
    for stock in _sm.entities():
        stock.update()
        for ding in _dm.entities():
            if stock.is_notify():
                if stock.is_strong_notify():
                    output = stock.output(at=True)
                    ding.send(content=output, title='💡持仓剧烈变动')
                    continue
                output = stock.output()
                ding.send(content=output, title='持仓变动')


if __name__ == "__main__":
    _dm = DingManager()
    _sm = StockManager()

    scheduler = BlockingScheduler()
    scheduler.add_job(__sche_stock, 'interval', seconds=3)
    # scheduler.add_job(__sche_stock_notify, trigger)
    scheduler.start()
