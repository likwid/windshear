from aiohttp import web
from functools import partial
import aiobotocore
import asyncio
import boto3
import logging

LOGGER_FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, datefmt='[%H:%M:%S]')
log = logging.getLogger()
log.setLevel(logging.INFO)

async def hello(request):
    return web.Response(text="Hello, world")

async def get_sqs_messages(session):
    async with session.create_client("sqs",
            region_name="us-east-1", endpoint_url="http://localhost:4576") as client:
        response = await client.receive_message(
            QueueUrl="http://localhost:4576/123456789012/foobar",
            MaxNumberOfMessages=1
        )

    return response

def callback(fut, session=None):
    log.info("Future resolved")
    response = fut.result()
    log.info(response)

async def poll_for_sqs_messages(loop, session, interval, iteration=0):

    callback_thunk = partial(callback, session=session)

    log.info("Schedule sqs future")
    future = asyncio.ensure_future(
        get_sqs_messages(session)
    )
    future.add_done_callback(callback_thunk)

    log.info("Increment iteration")
    iteration += 1
    log.info(f"Iteration: {iteration}")

    log.info("Schedule poller again")
    thunk = partial(
        poll_for_sqs_messages,
        loop, session, interval, iteration
    )

    loop.call_later(
        interval,
        lambda: asyncio.ensure_future(thunk())
    )

if __name__=='__main__':
    interval = 10
    loop = asyncio.get_event_loop()
    session = aiobotocore.get_session(loop=loop)
    loop.run_until_complete(poll_for_sqs_messages(loop, session, interval)) 
    app = web.Application()
    app.router.add_get('/', hello)

    f = loop.create_server(app.make_handler(), "0.0.0.0", 9000)
    server = loop.run_until_complete(f)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
