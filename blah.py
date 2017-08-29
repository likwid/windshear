#!/usr/bin/python3.4
import asyncio
import boto3
from aiohttp import web
from functools import partial

async def hello(request):
    return web.Response(text="Hello, world")

hello_app = web.Application()
hello_app.router.add_get('/', hello)

apps = [hello_app]

def process_message(msg, sqs=None):
    print(msg)

async def listen_to_sqs(sqs):
    response = await sqs.receive_message(
        QueueUrl="http://localhost:4576/123456789012/foobar",
        MaxNumberOfMessages=1
    )
    return response

def process_message(response, sqs=None, loop=None):
    print(response)
    for msg in response["Messages"]:
        sqs.delete_message(QueueUrl="http://localhost:4576/123456789012/foobar", ReceiptHandle=msg.ReceiptHandle)

    task = loop.create(listen_to_sqs(sqs=sqs)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    servers = []
    for i, app in enumerate(apps):
        f = loop.create_server(app.make_handler(), "0.0.0.0", 9000 + i)
        server = loop.run_until_complete(f)
        servers.append(server)

    sqs = boto3.client("sqs", region_name="us-east-1", endpoint_url="http://localhost:4576")
    process = partial(process_message, sqs=sqs)
    sqs_task = loop.create_task(listen_to_sqs(sqs))
    sqs_task.add_done_callback(

    try:
        print("Running... Press ^C to shutdown")
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    for i, server in enumerate(servers):
        server.close()
        loop.run_until_complete(server.wait_closed())
    loop.close()
