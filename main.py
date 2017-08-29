from aiohttp import web
import boto3

async def listen_to_sqs(app):
    running = True
    while(running):
        try:
            sqs = boto3.client('sqs', region_name="us-east-1")
            print("Getting message")
            response = await sqs.receive_message(
                QueueUrl="http://localhost:4576/123456789012/foobar",
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20
            )
            print(response)
        except asyncio.CancelledError:
            pass
        finally:
            running = False

async def start_background_tasks(app):
    app['sqs_listener'] = app.loop.create_task(listen_to_sqs(app))

async def cleanup_background_tasks(app):
    app['sqs_listener'].cancel()
    await app['sqs_listener']

async def hello(request):
    return web.Response(text="Hello, world")

app = web.Application()
app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)
app.router.add_get('/', hello)
web.run_app(app, port=8080)
