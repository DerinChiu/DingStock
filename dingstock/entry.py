from apscheduler.schedulers.blocking import BlockingScheduler

from .base import DingManager, StockManager

scheduler = BlockingScheduler()


@scheduler.scheduled_job('interval', seconds=3)
def __sche_stock_notify():
    print('__sche_stock_notify ran...')
    for stock in stock_manager.entities():
        stock.update()
        for ding in ding_manager.entities():
            if stock.is_strong_notify():
                output = stock.output(at=True)
                ding.send(content=output, title='❗️持仓剧烈变动')
                continue
            if stock.is_notify():
                output = stock.output()
                ding.send(content=output, title='持仓变动')


if __name__ == "__main__":
    ding_manager = DingManager()
    stock_manager = StockManager()
    scheduler.start()
