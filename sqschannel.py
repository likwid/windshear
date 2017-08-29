import boto3

async def main():
    sqs = boto3.client("sqs", region_name="us-east-1", endpoint_url="http://localhost:4576")
    async for m in get_message(sqs):
        print(await m)

async def get_message(sqs):
    response = await sqs.receive_message( 
        QueueUrl="http://localhost:4576/123456789012/foobar",
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20
    )
    yield response

if __name__=="__main__":
    await main()
